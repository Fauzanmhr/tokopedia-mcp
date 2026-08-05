"""MCP server exposing Tokopedia product data as tools."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Literal

from mcp.server.mcpserver import Context, MCPServer

from . import __version__
from .client import TokopediaClient, TokopediaError
from .models import SearchFilters

MAX_RESULT_LIMIT = 100
MAX_REVIEW_LIMIT = 100


@asynccontextmanager
async def lifespan(server: MCPServer):
    """One shared HTTP client for the server's lifetime."""
    client = TokopediaClient()
    try:
        yield {"client": client}
    finally:
        await client.aclose()


def create_server() -> MCPServer:
    server = MCPServer(
        "tokopedia-mcp",
        title="Tokopedia Product Search",
        description=(
            "Search products on Tokopedia and fetch product details and "
            "customer reviews. Prices are in Indonesian Rupiah (IDR)."
        ),
        version=__version__,
        lifespan=lifespan,
    )

    @server.tool()
    async def search_products(
        ctx: Context,
        keyword: str,
        max_result: int = 20,
        pmin: int | None = None,
        pmax: int | None = None,
        condition: Literal[1, 2] | None = None,
        shop_tier: Literal[2, 3] | None = None,
        rt: float | None = None,
        latest_product: Literal[7, 30, 90] | None = None,
        bebas_ongkir_extra: bool | None = None,
        is_discount: bool | None = None,
        is_fulfillment: bool | None = None,
        is_plus: bool | None = None,
        cod: bool | None = None,
    ) -> dict[str, Any]:
        """Search Tokopedia products by keyword.

        Returns a dict with a "products" list (name, price in IDR, rating,
        shop, URL) and the "count" of results returned. Each product can be
        passed to get_product_details for full information.

        Args:
            keyword: Search keyword, e.g. "logitech mouse" or "asus zenbook".
            max_result: Maximum number of results (1-100, default 20).
            pmin: Minimum price in IDR.
            pmax: Maximum price in IDR.
            condition: Product condition: 1 = new, 2 = used.
            shop_tier: Shop tier: 2 = Mall, 3 = Power Shop.
            rt: Minimum average rating, e.g. 4.5.
            latest_product: Only products listed within the last 7, 30, or 90 days.
            bebas_ongkir_extra: Only products with extra free-shipping benefit.
            is_discount: Only discounted products.
            is_fulfillment: Only products fulfilled by Tokopedia.
            is_plus: Only Tokopedia PLUS seller products.
            cod: Only products eligible for cash on delivery.
        """
        client: TokopediaClient = ctx.request_context.lifespan_context["client"]
        filters = SearchFilters(
            pmin=pmin,
            pmax=pmax,
            condition=condition,
            shop_tier=shop_tier,
            rt=rt,
            latest_product=latest_product,
            bebas_ongkir_extra=bebas_ongkir_extra,
            is_discount=is_discount,
            is_fulfillment=is_fulfillment,
            is_plus=is_plus,
            cod=cod,
        )
        try:
            products = await client.search(
                keyword, max_result=min(max(1, max_result), MAX_RESULT_LIMIT), filters=filters
            )
        except TokopediaError as exc:
            return {"error": str(exc)}
        return {"products": [p.model_dump(mode="json") for p in products], "count": len(products)}

    @server.tool()
    async def get_product_details(
        ctx: Context,
        product_id: str | int | None = None,
        url: str | None = None,
    ) -> dict[str, Any]:
        """Fetch full details for one Tokopedia product.

        Provides price, description, variants, stock, media, and shop info.

        Args:
            product_id: The numeric product id (from search_products). Takes
                precedence over url.
            url: A full tokopedia.com product URL, used when product_id is
                not provided.
        """
        client: TokopediaClient = ctx.request_context.lifespan_context["client"]
        try:
            product = await client.get_product(product_id=product_id, url=url)
        except TokopediaError as exc:
            return {"error": str(exc)}
        return product.model_dump(mode="json")

    @server.tool()
    async def get_product_reviews(
        ctx: Context,
        product_id: str | int,
        max_count: int = 20,
    ) -> dict[str, Any]:
        """Fetch customer reviews for a Tokopedia product.

        Returns a dict with a "reviews" list (messages, ratings, user info,
        seller responses, attached media) and the "count" of reviews returned.

        Args:
            product_id: The numeric product id (from search_products).
            max_count: Maximum number of reviews (1-100, default 20).
        """
        client: TokopediaClient = ctx.request_context.lifespan_context["client"]
        try:
            reviews = await client.get_reviews(
                product_id, max_count=min(max(1, max_count), MAX_REVIEW_LIMIT)
            )
        except TokopediaError as exc:
            return {"error": str(exc)}
        return {"reviews": [r.model_dump(mode="json") for r in reviews], "count": len(reviews)}

    return server
