"""Asynchronous Python client for Mealie."""
import asyncio
from typing import Any

import aiohttp
from aioresponses import CallbackResult, aioresponses
import pytest

from aiomealie.exceptions import MealieConnectionError, MealieError
from aiomealie.mealie import MealieClient
from syrupy import SnapshotAssertion
from tests import load_fixture

from .const import MEALIE_URL


async def test_putting_in_own_session(
    responses: aioresponses,
) -> None:
    """Test putting in own session."""
    responses.get(
        f"{MEALIE_URL}/api/app/about/startup-info",
        status=200,
        body=load_fixture("startup_info.json"),
    )
    async with aiohttp.ClientSession() as session:
        analytics = MealieClient(session=session, api_host="demo.mealie.io")
        await analytics.get_startup_info()
        assert analytics.session is not None
        assert not analytics.session.closed
        await analytics.close()
        assert not analytics.session.closed


async def test_creating_own_session(
    responses: aioresponses,
) -> None:
    """Test creating own session."""
    responses.get(
        f"{MEALIE_URL}/api/app/about/startup-info",
        status=200,
        body=load_fixture("startup_info.json"),
    )
    analytics = MealieClient(api_host="demo.mealie.io")
    await analytics.get_startup_info()
    assert analytics.session is not None
    assert not analytics.session.closed
    await analytics.close()
    assert analytics.session.closed


async def test_unexpected_server_response(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test handling unexpected response."""
    responses.get(
        f"{MEALIE_URL}/api/app/about/startup-info",
        status=200,
        headers={"Content-Type": "plain/text"},
        body="Yes",
    )
    with pytest.raises(MealieError):
        assert await mealie_client.get_startup_info()


async def test_timeout(
    responses: aioresponses,
) -> None:
    """Test request timeout."""

    # Faking a timeout by sleeping
    async def response_handler(_: str, **_kwargs: Any) -> CallbackResult:
        """Response handler for this test."""
        await asyncio.sleep(2)
        return CallbackResult(body="Goodmorning!")

    responses.get(
        f"{MEALIE_URL}/api/app/about/startup-info",
        callback=response_handler,
    )
    async with MealieClient(
        request_timeout=1,
        api_host="demo.mealie.io",
    ) as mealie_client:
        with pytest.raises(MealieConnectionError):
            assert await mealie_client.get_startup_info()


async def test_startup_info(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving startup info."""
    responses.get(
        f"{MEALIE_URL}/api/app/about/startup-info",
        status=200,
        body=load_fixture("startup_info.json"),
    )
    assert await mealie_client.get_startup_info() == snapshot


async def test_theme(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving theme."""
    responses.get(
        f"{MEALIE_URL}/api/app/about/theme",
        status=200,
        body=load_fixture("theme.json"),
    )
    assert await mealie_client.get_theme() == snapshot


async def test_recipes(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving recipes."""
    responses.get(
        f"{MEALIE_URL}/api/recipes",
        status=200,
        body=load_fixture("recipes.json"),
    )
    assert await mealie_client.get_recipes() == snapshot
