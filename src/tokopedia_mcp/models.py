"""Typed models for Tokopedia product data."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Condition = Literal[1, 2]  # 1 = new, 2 = used
ShopTier = Literal[2, 3]  # 2 = Mall, 3 = Power Shop
Recency = Literal[7, 30, 90]  # listed within the last N days


class Shop(BaseModel):
    """A Tokopedia shop."""

    shop_id: int | None = None
    name: str = ""
    city: str | None = None
    url: str | None = None
    shop_type: str | None = None  # "Normal" | "Mall" | "Power Shop"


class ProductOption(BaseModel):
    """A selectable option group, e.g. color."""

    option_id: int | None = None
    name: str = ""
    values: list[str] = Field(default_factory=list)


class ProductVariant(BaseModel):
    """A concrete variant of a product (a specific option combination)."""

    option_ids: list[int] = Field(default_factory=list)
    name: str = ""
    url: str | None = None
    price: int | None = None
    price_text: str | None = None
    price_original_text: str | None = None
    discount_percentage: str | None = None
    stock: int | None = None
    image_url: str | None = None


class ProductMedia(BaseModel):
    """An image or video attached to a product."""

    type: str = ""
    original: str | None = None
    thumbnail: str | None = None
    max_res: str | None = None


class Review(BaseModel):
    """A customer review of a product."""

    feedback_id: int | None = None
    variant_name: str = ""
    message: str = ""
    rating: float | None = None
    created_text: str = ""  # relative age as shown by Tokopedia, e.g. "1 bulan lalu"
    user_name: str = ""
    user_url: str | None = None
    seller_response: str = ""
    images: list[str] = Field(default_factory=list)
    videos: list[str] = Field(default_factory=list)
    likes: int = 0


class Product(BaseModel):
    """A Tokopedia product, either from search results or full detail."""

    product_id: int | None = None
    sku: str | None = None
    name: str = ""
    url: str | None = None
    main_image: str | None = None
    status: str | None = None
    description: str | None = None
    price: int | None = None
    price_text: str | None = None
    price_original_text: str | None = None
    discount_percentage: str | None = None
    weight: int | None = None
    weight_unit: str | None = None
    sold_count: int | None = None
    rating: float | None = None
    review_count: int | None = None
    total_stock: int | None = None
    category: str | None = None
    sub_category: list[str] = Field(default_factory=list)
    media: list[ProductMedia] = Field(default_factory=list)
    options: list[ProductOption] = Field(default_factory=list)
    variants: list[ProductVariant] = Field(default_factory=list)
    shop: Shop | None = None


class SearchFilters(BaseModel):
    """Optional filters applied to a product search.

    Only fields that are set are sent to Tokopedia.
    """

    pmin: int | None = None  # minimum price in IDR
    pmax: int | None = None  # maximum price in IDR
    condition: Condition | None = None
    shop_tier: ShopTier | None = None
    rt: float | None = None  # minimum average rating
    latest_product: Recency | None = None
    bebas_ongkir_extra: bool | None = None  # extra free-shipping benefit
    is_discount: bool | None = None
    is_fulfillment: bool | None = None  # fulfilled by Tokopedia
    is_plus: bool | None = None  # Tokopedia PLUS sellers
    cod: bool | None = None
