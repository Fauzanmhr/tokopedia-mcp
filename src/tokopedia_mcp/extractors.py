"""Pure functions turning raw Tokopedia GraphQL payloads into typed models.

Kept free of I/O so the parsing logic is unit-testable offline against
recorded responses (see ``tests/fixtures``).
"""

from __future__ import annotations

import json
from typing import Any

from .models import (
    Product,
    ProductMedia,
    ProductOption,
    ProductVariant,
    Review,
    Shop,
)


SHOP_TIERS = {1: "Normal", 2: "Mall", 3: "Power Shop"}


def resolve_shop_type(shop_tier: Any) -> str | None:
    """Resolve a shop tier from a numeric stier value or a badge image URL.

    Search results carry a badge image URL, while the PDP response carries
    the numeric stier value. Badge URL formats observed (2026): empty for
    normal shops, ``official_store/badge_os.png`` for Mall, ``Power Merchant
    Pro`` for Power Shop.
    """
    if shop_tier is None:
        return None
    if isinstance(shop_tier, int) and shop_tier in SHOP_TIERS:
        return SHOP_TIERS[shop_tier]
    if isinstance(shop_tier, str):
        if "Power%20Merchant%20Pro" in shop_tier or "Power Merchant Pro" in shop_tier:
            return "Power Shop"
        if "official_store" in shop_tier:
            return "Mall"
    return None


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_search_items(products: list[dict]) -> list[Product]:
    """Parse the ``searchProductV5.data.products`` list."""
    result: list[Product] = []
    for raw in products:
        price = raw.get("price", {})
        shop = raw.get("shop", {})
        stock = raw.get("stock", {})
        media = raw.get("mediaURL", {})
        result.append(
            Product(
                product_id=_to_int(raw.get("id")),
                sku=stock.get("ttsSKUID"),
                name=raw.get("name", ""),
                category=(raw.get("category") or {}).get("name"),
                url=raw.get("url"),
                sold_count=_to_int(stock.get("sold")),
                price=_to_int(price.get("number")),
                price_text=price.get("text"),
                price_original_text=price.get("original"),
                rating=_to_float(raw.get("rating")),
                main_image=media.get("image700"),
                shop=Shop(
                    shop_id=_to_int(shop.get("id")),
                    name=shop.get("name", ""),
                    city=shop.get("city"),
                    url=shop.get("url"),
                    shop_type=resolve_shop_type((raw.get("badge") or {}).get("url")),
                ),
            )
        )
    return result


def parse_product(json_data: dict) -> Product:
    """Parse a ``pdpGetLayout`` response."""
    pdp = json_data.get("data", {}).get("pdpGetLayout", {})
    basic_info = pdp.get("basicInfo", {})
    components = {c.get("name"): c.get("data") for c in pdp.get("components", [])}

    def payload(name: str) -> dict:
        entries = components.get(name) or []
        return entries[0] if entries else {}

    content = payload("product_content")
    price = content.get("price", {}) or {}

    media_raw = payload("product_media").get("media", []) or []
    media = [
        ProductMedia(
            type=m.get("type", ""),
            original=m.get("URLOriginal"),
            thumbnail=m.get("URLThumbnail"),
            max_res=m.get("URLMaxRes"),
        )
        for m in media_raw
    ]

    variant_payload = payload("mini_variant_options")
    children = variant_payload.get("children", []) or []
    variants = [
        ProductVariant(
            option_ids=list(v.get("optionID") or []),
            name=v.get("productName", ""),
            url=v.get("productURL"),
            price=_to_int(v.get("price")),
            price_text=v.get("priceFmt"),
            price_original_text=v.get("slashPriceFmt"),
            discount_percentage=v.get("discPercentage"),
            stock=_to_int((v.get("stock") or {}).get("stock")),
            image_url=(v.get("picture") or {}).get("url"),
        )
        for v in children
    ]

    options: list[ProductOption] = []
    for option in variant_payload.get("variants") or []:
        options.append(
            ProductOption(
                option_id=_to_int(option.get("id") or option.get("optionID")),
                name=option.get("name", ""),
                values=[v.get("name", "") for v in option.get("value", [])],
            )
        )

    description: str | None = None
    detail = payload("product_detail")
    for line in detail.get("content", []) or []:
        if isinstance(line, dict) and line.get("key") == "deskripsi":
            description = line.get("subtitle")
            break

    shop_type: Any = None
    pdp_session = pdp.get("pdpSession")
    if pdp_session:
        try:
            shop_type = json.loads(pdp_session).get("stier")
        except ValueError:
            shop_type = None

    category = basic_info.get("category", {}) or {}
    product_url = basic_info.get("url", "")
    return Product(
        product_id=_to_int(basic_info.get("productID")),
        sku=basic_info.get("ttsSKUID"),
        name=content.get("name", ""),
        url=product_url,
        main_image=basic_info.get("defaultMediaURL"),
        status=basic_info.get("status"),
        description=description,
        price=_to_int(price.get("value")),
        price_text=price.get("priceFmt"),
        price_original_text=price.get("slashPriceFmt"),
        discount_percentage=price.get("discPercentage"),
        weight=_to_int(basic_info.get("weight")),
        weight_unit=basic_info.get("weightUnit"),
        sold_count=_to_int((basic_info.get("txStats") or {}).get("countSold")),
        rating=_to_float((basic_info.get("stats") or {}).get("rating")),
        review_count=_to_int((basic_info.get("stats") or {}).get("countReview")),
        total_stock=_to_int(str(basic_info.get("totalStockFmt", "")).replace(".", "")),
        category=category.get("name"),
        sub_category=[d.get("name", "") for d in category.get("detail", []) or []],
        media=media,
        options=options,
        variants=variants,
        shop=Shop(
            shop_id=_to_int(basic_info.get("shopID")),
            name=basic_info.get("shopName", ""),
            city=(basic_info.get("shopMultilocation") or {}).get("cityName"),
            url="/".join(product_url.split("/")[:-1]) if product_url else None,
            shop_type=resolve_shop_type(shop_type),
        ),
    )


def parse_reviews(items: list[dict]) -> list[Review]:
    """Parse the ``productrevGetProductReviewList.list`` entries."""
    result: list[Review] = []
    for item in items:
        user = item.get("user", {}) or {}
        response = item.get("reviewResponse", {}) or {}
        likes = item.get("likeDislike", {}) or {}
        result.append(
            Review(
                feedback_id=_to_int(item.get("feedbackID")),
                variant_name=item.get("variantName", ""),
                message=item.get("message", ""),
                rating=_to_float(item.get("productRating")),
                created_text=item.get("reviewCreateTime", ""),
                user_name=user.get("fullName", ""),
                user_url=user.get("url"),
                seller_response=response.get("message", ""),
                images=[img.get("imageUrl", "") for img in item.get("imageAttachments") or []],
                videos=[v.get("videoUrl", "") for v in item.get("videoAttachments") or []],
                likes=_to_int(likes.get("totalLike")) or 0,
            )
        )
    return result
