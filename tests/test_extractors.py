"""Offline tests: parse recorded Tokopedia responses into typed models."""

from __future__ import annotations

import json
from pathlib import Path

from tokopedia_mcp.extractors import (
    parse_product,
    parse_reviews,
    parse_search_items,
    resolve_shop_type,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_search_items_parsed():
    data = _load("search_page1.json")
    products = parse_search_items(data["data"]["searchProductV5"]["data"]["products"])
    assert len(products) == 26
    first = products[0]
    assert first.product_id == 171262787
    assert first.name.startswith("Mouse Logitech Optical B100")
    assert first.price == 80000
    assert first.price_text == "Rp80.000"
    assert first.rating == 4.9
    assert first.sold_count == 1286
    assert first.shop.name == "Dunia Mas Computer"
    assert first.shop.shop_type == "Mall"
    assert first.main_image and first.main_image.startswith("https://")


def test_search_items_badge_mapping():
    # Power Shop badge URL (URL-encoded "Power Merchant Pro")
    assert resolve_shop_type("https://…/badge/Power%20Merchant%20Pro.png") == "Power Shop"
    # Mall badge URL (current format)
    assert resolve_shop_type("https://…/img/official_store/badge_os.png") == "Mall"
    assert resolve_shop_type("") is None
    assert resolve_shop_type(None) is None
    # numeric stier from PDP session
    assert resolve_shop_type(1) == "Normal"
    assert resolve_shop_type(2) == "Mall"
    assert resolve_shop_type(3) == "Power Shop"


def test_product_details_parsed():
    product = parse_product(_load("product.json"))
    assert product.product_id == 103483271373
    assert product.name.startswith("Logitech G102 Mouse Gaming Wired")
    assert product.price == 175000
    assert product.price_text == "Rp175.000"
    assert product.price_original_text == "Rp379.000"
    assert product.discount_percentage == "54%"
    assert product.description and len(product.description) > 100
    assert product.rating == 5.0
    assert product.review_count == 10
    assert product.total_stock == 1785
    assert product.shop.name == "ORBITBYTE DIGITAL STORE"
    assert product.shop.shop_type == "Normal"
    assert len(product.variants) == 3
    variant = product.variants[0]
    assert variant.option_ids == [2]
    assert variant.price == 228000
    assert variant.stock == 890
    assert variant.url and "tokopedia.com" in variant.url
    assert product.main_image and product.main_image.startswith("https://")


def test_reviews_parsed():
    data = _load("reviews.json")
    reviews = parse_reviews(data["data"]["productrevGetProductReviewList"]["list"])
    assert len(reviews) == 8
    first = reviews[0]
    assert first.feedback_id == 2159810422
    assert first.rating == 5.0
    assert first.user_name == "User582948"
    assert first.variant_name == "Hitam."
    assert first.seller_response  # seller reply present
    assert first.created_text  # relative age present
    assert first.likes == 0
