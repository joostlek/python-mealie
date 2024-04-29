"""Homeassistant Client."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, Self

from aiohttp import ClientSession
import orjson
from yarl import URL

from aiomealie.exceptions import MealieConnectionError, MealieError
from aiomealie.models import (
    Mealplan,
    MealplanResponse,
    RecipesResponse,
    StartupInfo,
    Theme,
)

if TYPE_CHECKING:
    from datetime import date

VERSION = metadata.version(__package__)


@dataclass
class MealieClient:
    """Main class for handling connections with Mealie."""

    api_host: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(self, uri: str, params: dict[str, Any] | None = None) -> str:
        """Handle a request to Mealie."""
        url = URL.build(
            scheme="https",
            host=self.api_host,
            port=443,
        ).joinpath(uri)

        headers = {
            "User-Agent": f"AioMealie/{VERSION}",
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.get(
                    url,
                    params=params,
                    headers=headers,
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to Mealie"
            raise MealieConnectionError(msg) from exception

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from Mealie"
            raise MealieError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.text()

    async def get_startup_info(self) -> StartupInfo:
        """Get startup info."""
        response = await self._request("api/app/about/startup-info")
        return StartupInfo.from_json(response)

    async def get_theme(self) -> Theme:
        """Get theme."""
        response = await self._request("api/app/about/theme")
        return Theme.from_json(response)

    async def get_recipes(self) -> RecipesResponse:
        """Get recipes."""
        response = await self._request("api/recipes")
        return RecipesResponse.from_json(response)

    async def get_mealplan_today(self) -> list[Mealplan]:
        """Get mealplan."""
        raw_response = await self._request("api/groups/mealplans/today")
        response = orjson.loads(raw_response)  # pylint: disable=maybe-no-member
        return [Mealplan.from_dict(item) for item in response]

    async def get_mealplans(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MealplanResponse:
        """Get mealplans."""
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        response = await self._request("api/groups/mealplans", params)
        return MealplanResponse.from_json(response)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The MealieClient object.
        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
