"""Asynchronous Python client for Mealie."""

from typing import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
import pytest

from aiomealie import MealieClient
from syrupy import SnapshotAssertion

from .syrupy import MealieSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Mealie extension."""
    return snapshot.use_extension(MealieSnapshotExtension)


@pytest.fixture(name="mealie_client")
async def client() -> AsyncGenerator[MealieClient, None]:
    """Return a Mealie client."""
    async with (
        aiohttp.ClientSession() as session,
        MealieClient(
            "https://demo.mealie.io",
            session=session,
        ) as mealie_client,
    ):
        mealie_client.household_support = True
        yield mealie_client


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
