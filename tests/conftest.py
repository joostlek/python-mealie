"""Asynchronous Python client for Mealie."""

from collections.abc import AsyncGenerator

import aiohttp
from aiointercept import aiointercept
import pytest

from aiomealie import MealieClient
from syrupy import SnapshotAssertion

from .syrupy import MealieSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Mealie extension."""
    return snapshot.use_extension(MealieSnapshotExtension)


@pytest.fixture(name="mealie_client")
async def client() -> AsyncGenerator[MealieClient]:
    """Return a Mealie client."""
    async with (
        aiohttp.ClientSession() as session,
        MealieClient(
            "https://demo.mealie.io",
            session=session,
        ) as mealie_client,
    ):
        yield mealie_client


@pytest.fixture(name="responses")
async def aiointercept_fixture() -> AsyncGenerator[aiointercept]:
    """Return aiointercept fixture."""
    async with aiointercept(mock_external_urls=True) as mocked_responses:
        yield mocked_responses
