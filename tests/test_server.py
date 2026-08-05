"""Server tests: tool registration (offline) and end-to-end round trip (live)."""

from __future__ import annotations

import sys

import pytest

from tokopedia_mcp.server import create_server


def test_server_registers_expected_tools():
    server = create_server()
    names = sorted(t.name for t in server._tool_manager.list_tools())
    assert names == ["get_product_details", "get_product_reviews", "search_products"]


def test_tool_parameter_schemas():
    server = create_server()
    tools = {t.name: t for t in server._tool_manager.list_tools()}
    params = tools["search_products"].parameters
    props = params["properties"]
    assert props["keyword"]["type"] == "string"
    assert props["max_result"]["default"] == 20
    # context parameter must not leak into the public schema
    assert "ctx" not in props
    # enum-constrained filters (nullable -> nested under anyOf)
    assert props["condition"]["anyOf"][0]["enum"] == [1, 2]
    assert props["shop_tier"]["anyOf"][0]["enum"] == [2, 3]
    assert props["latest_product"]["anyOf"][0]["enum"] == [7, 30, 90]
    for required in ("keyword",):
        assert required in params["required"]


@pytest.mark.live
@pytest.mark.asyncio
async def test_end_to_end_round_trip():
    """Spawn the real server over stdio and call all three tools."""
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    params = StdioServerParameters(
        command=sys.executable, args=["-m", "tokopedia_mcp"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            assert {t.name for t in tools.tools} == {
                "get_product_details",
                "get_product_reviews",
                "search_products",
            }

            # search
            res = await session.call_tool("search_products", {"keyword": "logitech mouse", "max_result": 3})
            payload = _parse_dict_result(res)
            products = payload["products"]
            assert payload["count"] == len(products)
            assert 1 <= len(products) <= 3
            assert products[0]["name"]
            assert products[0]["shop"]["name"]
            pid = products[0]["product_id"]

            # details
            res = await session.call_tool("get_product_details", {"product_id": pid})
            detail = _parse_dict_result(res)
            assert detail["product_id"] == pid
            assert detail["name"]

            # reviews
            res = await session.call_tool("get_product_reviews", {"product_id": pid, "max_count": 5})
            payload = _parse_dict_result(res)
            reviews = payload["reviews"]
            assert payload["count"] == len(reviews)
            assert isinstance(reviews, list)


def _parse_dict_result(res) -> dict:
    assert not res.is_error
    import json

    return json.loads(res.content[0].text)
