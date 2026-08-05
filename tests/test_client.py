"""Offline tests for client helpers and validation."""

from __future__ import annotations

import pytest

from tokopedia_mcp.client import (
    TokopediaClient,
    TokopediaError,
    _merge_params,
    parse_product_url,
)
from tokopedia_mcp.models import Product, SearchFilters


def test_parse_product_url():
    shop, key = parse_product_url(
        "https://www.tokopedia.com/orbitbyte-digital-store/logitech-g102-mouse-123?extParam=ivf%3Dfalse"
    )
    assert shop == "orbitbyte-digital-store"
    assert key == "logitech-g102-mouse-123"


def test_parse_product_url_rejects_bad_url():
    with pytest.raises(TokopediaError):
        parse_product_url("https://www.tokopedia.com/only-shop")


def test_merge_params_overrides_base():
    merged = _merge_params("q=logitech&page=1&ob=0", "page=2&rt=4.5")
    assert merged == "q=logitech&page=2&ob=0&rt=4.5"


def test_build_search_params_base():
    params = TokopediaClient._build_search_params("logitech mouse", None)
    assert "q=logitech%20mouse" in params
    assert "page=1" in params
    assert "device=ios" in params


def test_build_search_params_filters():
    filters = SearchFilters(pmin=100000, pmax=2000000, rt=4.5, condition=1, bebas_ongkir_extra=True)
    params = TokopediaClient._build_search_params("mouse", filters)
    assert "pmin=100000" in params
    assert "pmax=2000000" in params
    assert "rt=4.5" in params
    assert "condition=1" in params
    assert "bebas_ongkir_extra=True" in params
    # unset filters are omitted
    assert "is_discount" not in params
    assert "cod" not in params


def test_dedupe_keeps_first_occurrence():
    dupes = [
        Product(product_id=1, name="a"),
        Product(product_id=2, name="b"),
        Product(product_id=1, name="a-duplicate"),
    ]
    unique = TokopediaClient._dedupe(dupes)
    assert [p.product_id for p in unique] == [1, 2]
    assert unique[0].name == "a"


@pytest.mark.asyncio
async def test_search_rejects_bad_input():
    client = TokopediaClient()
    with pytest.raises(TokopediaError):
        await client.search("   ")
    with pytest.raises(TokopediaError):
        await client.search("mouse", max_result=0)
    with pytest.raises(TokopediaError):
        await client.get_product()
    with pytest.raises(TokopediaError):
        await client.get_reviews(1, max_count=0)
    await client.aclose()
