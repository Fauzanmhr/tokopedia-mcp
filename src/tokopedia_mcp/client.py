"""Async client for Tokopedia's internal iOS GraphQL API.

The public endpoints Tokopedia serves to its mobile app are reverse
engineered: requests must carry the app's custom headers plus a per-request
randomized device identity (user id, device id, fingerprint, timestamps) or
the edge layer resets the HTTP/2 stream. TLS fingerprint impersonation
(``impersonate``) further reduces the chance of bot detection.
"""

from __future__ import annotations

import asyncio
import base64
import json
import random
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qs, quote, urlencode

from curl_cffi import requests

from .extractors import parse_product, parse_reviews, parse_search_items
from .models import Product, Review, SearchFilters
from .queries import (
    GQL_ENDPOINT,
    PRODUCT_PATH,
    PRODUCT_QUERY,
    REVIEWS_PATH,
    REVIEWS_QUERY,
    SEARCH_PATH,
    SEARCH_QUERY,
)

APP_VERSION = "2.318.0"
USER_AGENT = (
    f"Tokopedia/{APP_VERSION} (com.tokopedia.Tokopedia; build:202505022018; "
    f"iOS 18.5.0) Alamofire/{APP_VERSION}"
)
WIB = timezone(timedelta(hours=7))


class TokopediaError(Exception):
    """Raised when Tokopedia's API rejects or fails a request."""


def _random_identity() -> dict[str, str]:
    """Fresh device identity headers, one per request."""
    fingerprint = {
        "device_manufacturer": "Apple",
        "timezone": "Asia/Jakarta",
        "location_longitude": f"{random.uniform(104.5, 114.0):.6f}",
        "location_latitude": f"{random.uniform(-8.8, -5.5):.6f}",
        "idfa": secrets.token_hex(16).upper(),
        "is_emulator": False,
        "unique_id": secrets.token_hex(16).upper(),
        "access_type": 1,
        "device_system": "iOS",
        "device_model": "iPhone",
        "is_tablet": False,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "is_jailbroken_rooted": False,
        "screen_resolution": "2556x1179",
        "versionName": APP_VERSION,
        "current_os": "18.5",
        "language": "id",
        "device_name": "iPhone 15 Pro Max",
    }
    return {
        "X-Tkpd-Userid": str(random.randint(10**8, 10**9 - 1)),
        "Bd-Device-Id": str(random.randint(10**18, 10**19 - 1)),
        "Fingerprint-Data": base64.b64encode(json.dumps(fingerprint).encode()).decode(),
        "Date": datetime.now(WIB).strftime("%a, %d %b %Y %H:%M:%S +0700"),
        "Tt-Request-Time": str(int(time.time() * 1000)),
    }


def _base_headers(path: str) -> dict[str, str]:
    return {
        "Host": "gql.tokopedia.com",
        "Os_type": "2",
        "X-Tkpd-Path": path,
        "X-Method": "POST",
        "Request-Method": "POST",
        "X-Device": f"ios-{APP_VERSION}",
        "Accept-Language": "id;q=1.0, en;q=0.9",
        "Content-Type": "application/json; encoding=utf-8",
        "User-Agent": USER_AGENT,
        "X-App-Version": APP_VERSION,
        "Accept": "application/json",
        "X-Dark-Mode": "false",
        "X-Theme": "default",
        "X-Price-Center": "true",
        "Device-Type": "iphone",
    }


def parse_product_url(url: str) -> tuple[str, str]:
    """Split ``https://www.tokopedia.com/<shop>/<product-key>?...`` into
    ``(shop_domain, product_key)``."""
    path = url.split("?")[0]
    parts = path.split("tokopedia.com/")[-1].split("/")
    if len(parts) < 2 or not all(parts[:2]):
        raise TokopediaError(f"Could not parse product url: {url}")
    return parts[0], parts[1]


def _merge_params(base: str, additional: str) -> str:
    merged = {k: v[0] for k, v in parse_qs(base).items()}
    merged.update({k: v[0] for k, v in parse_qs(additional).items()})
    return urlencode(merged, safe=",", quote_via=quote)


class TokopediaClient:
    """Async client for Tokopedia product search, details, and reviews."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        impersonate: str = "safari_ios",
    ) -> None:
        self._session = requests.AsyncSession(impersonate=impersonate, timeout=timeout)
        self._max_retries = max_retries

    async def __aenter__(self) -> "TokopediaClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._session.close()

    async def _post(
        self, path: str, payload: dict[str, Any], *, akamai: str | None = None
    ) -> dict[str, Any]:
        headers = _base_headers(path)
        if akamai:
            headers["X-Tkpd-Akamai"] = akamai
        headers.update(_random_identity())

        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                response = await self._session.post(
                    GQL_ENDPOINT + path, headers=headers, json=payload
                )
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise TokopediaError(
                        f"Unexpected response from {path}: {type(data).__name__}"
                    )
                return data
            except (requests.RequestException, TokopediaError) as exc:
                last_error = exc
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(2**attempt)
        raise TokopediaError(
            f"Request to {path} failed after {self._max_retries} attempts: {last_error}"
        ) from last_error

    async def search(
        self, keyword: str, max_result: int = 20, filters: SearchFilters | None = None
    ) -> list[Product]:
        """Search products by keyword, optionally paginating until ``max_result``."""
        if not keyword.strip():
            raise TokopediaError("keyword must not be empty")
        if max_result < 1:
            raise TokopediaError("max_result must be >= 1")

        base_params = self._build_search_params(keyword, filters)
        products: list[Product] = []
        next_params: str | None = None

        while len(products) < max_result:
            params = (
                _merge_params(base_params, next_params) if next_params else base_params
            )
            data = await self._post(
                SEARCH_PATH,
                {
                    "query": SEARCH_QUERY,
                    "variables": {"params": params, "query": keyword},
                },
            )
            block = data.get("data", {}).get("searchProductV5", {})
            items = block.get("data", {}).get("products", [])
            products.extend(parse_search_items(items))

            additional = (block.get("header") or {}).get("additionalParams")
            if not additional or not items:
                break
            next_params = additional

        return self._dedupe(products)[:max_result]

    async def get_product(
        self, product_id: int | str | None = None, url: str | None = None
    ) -> Product:
        """Fetch full details for a product by id or URL."""
        if product_id is None and url is None:
            raise TokopediaError("Provide either product_id or url")
        shop_domain = product_key = ""
        if product_id is None:
            shop_domain, product_key = parse_product_url(url)  # type: ignore[arg-type]

        variables = {
            "apiVersion": 1,
            "userLocation": {
                "addressID": "",
                "addressName": "",
                "receiverName": "",
                "postalCode": "",
                "districtID": "",
                "cityID": "",
                "latlon": "",
            },
            "tokonow": {"shopID": "0", "warehouses": [], "whID": "0", "serviceType": "ooc"},
            "extParam": "",
            "productId": str(product_id) if product_id is not None else "",
            "shopDomain": shop_domain,
            "productKey": product_key,
            "whID": "",
            "layoutID": "",
        }
        data = await self._post(
            PRODUCT_PATH,
            {"query": PRODUCT_QUERY, "variables": variables},
            akamai="pdpGetLayout",
        )
        return parse_product(data)

    async def get_reviews(
        self, product_id: int | str, max_count: int = 20
    ) -> list[Review]:
        """Fetch up to ``max_count`` customer reviews for a product."""
        if max_count < 1:
            raise TokopediaError("max_count must be >= 1")

        reviews: list[Review] = []
        page = 1
        while len(reviews) < max_count:
            data = await self._post(
                REVIEWS_PATH,
                {
                    "query": REVIEWS_QUERY,
                    "variables": {
                        "productID": str(product_id),
                        "page": page,
                        "limit": 10,
                        "filterBy": "",
                        "opt": "",
                        "sortBy": "informative_score desc",
                    },
                },
            )
            block = data.get("data", {}).get("productrevGetProductReviewList", {})
            items = block.get("list", [])
            reviews.extend(parse_reviews(items))
            if not items or not block.get("hasNext"):
                break
            page += 1
        return reviews[:max_count]

    @staticmethod
    def _build_search_params(keyword: str, filters: SearchFilters | None) -> str:
        params: dict[str, str] = {
            "user_warehouseId": "0",
            "user_shopId": "0",
            "user_postCode": "10110",
            "srp_initial_state": "false",
            "breadcrumb": "true",
            "ep": "product",
            "user_cityId": "0",
            "q": keyword,
            "related": "true",
            "source": "search",
            "srp_enter_method": "normal_search",
            "enter_method": "normal_search",
            "l_name": "sre",
            "user_districtId": "0",
            "srp_feature_id": "",
            "catalog_rows": "0",
            "page": "1",
            "srp_component_id": "02.01.00.00",
            "ob": "0",
            "srp_sug_type": "",
            "src": "search",
            "with_template": "true",
            "show_adult": "false",
            "srp_direct_middle_page": "false",
            "channel": "product search",
            "rf": "false",
            "navsource": "home",
            "use_page": "true",
            "dep_id": "",
            "device": "ios",
        }
        if filters:
            params.update(
                {
                    k: str(v)
                    for k, v in filters.model_dump(exclude_none=True).items()
                }
            )
        return urlencode(params, safe=",", quote_via=quote)

    @staticmethod
    def _dedupe(products: list[Product]) -> list[Product]:
        seen: set[int | None] = set()
        unique: list[Product] = []
        for product in products:
            if product.product_id in seen:
                continue
            seen.add(product.product_id)
            unique.append(product)
        return unique
