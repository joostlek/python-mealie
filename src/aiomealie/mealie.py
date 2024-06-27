"""Homeassistant Client."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, Self

from aiohttp import ClientSession
from aiohttp.hdrs import METH_GET, METH_POST, METH_PUT, METH_DELETE
import orjson
from yarl import URL

from aiomealie.exceptions import (
    MealieConnectionError,
    MealieError,
    MealieAuthenticationError,
)
from aiomealie.models import (
    GroupSummary,
    Mealplan,
    MealplanResponse,
    OrderDirection,
    RecipesResponse,
    ShoppingListsResponse,
    ShoppingItemsOrderBy,
    ShoppingItemsResponse,
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
    token: str | None = None
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        method: str,
        uri: str,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to Mealie."""
        url = URL(self.api_host).joinpath(uri)

        headers = {
            "User-Agent": f"AioMealie/{VERSION}",
            "Accept": "application/json, text/plain, */*",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        kwargs = {
            "headers": headers,
            "params": params,
            "json": data,
        }

        not_none_kwargs = {k: v for k, v in kwargs.items() if v is not None}

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(method, url, **not_none_kwargs)
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to Mealie"
            raise MealieConnectionError(msg) from exception

        if response.status == 401:
            msg = "Unauthorized access to Mealie"
            raise MealieAuthenticationError(msg)

        if response.status == 422:
            text = await response.text()
            msg = "Mealie validation error"
            raise MealieError(
                msg,
                {"response": text},
            )

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected response from Mealie"
            raise MealieError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.text()

    async def _get(self, uri: str, params: dict[str, Any] | None = None) -> str:
        """Handle a GET request to Mealie."""
        return await self._request(METH_GET, uri, params=params)

    async def _post(
        self,
        uri: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a POST request to Mealie."""
        return await self._request(METH_POST, uri, data=data, params=params)

    async def _put(
        self,
        uri: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a PUT request to Mealie."""
        return await self._request(METH_PUT, uri, data=data, params=params)

    async def _delete(
        self,
        uri: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a DELETE request to Mealie."""
        return await self._request(METH_DELETE, uri, data=data, params=params)

    async def get_startup_info(self) -> StartupInfo:
        """Get startup info."""
        response = await self._get("api/app/about/startup-info")
        return StartupInfo.from_json(response)

    async def get_groups_self(self) -> GroupSummary:
        """Get groups self."""
        response = await self._get("api/groups/self")
        return GroupSummary.from_json(response)

    async def get_theme(self) -> Theme:
        """Get theme."""
        response = await self._get("api/app/about/theme")
        return Theme.from_json(response)

    async def get_recipes(self) -> RecipesResponse:
        """Get recipes."""
        response = await self._get("api/recipes")
        return RecipesResponse.from_json(response)

    async def get_mealplan_today(self) -> list[Mealplan]:
        """Get mealplan."""
        raw_response = await self._get("api/groups/mealplans/today")
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
        response = await self._get("api/groups/mealplans", params)
        return MealplanResponse.from_json(response)

    async def get_shopping_lists(self) -> ShoppingListsResponse:
        """Get shopping lists."""
        response = await self._get("api/groups/shopping/lists")
        return ShoppingListsResponse.from_json(response)

    async def get_shopping_items(
        self,
        shopping_list_id: str,
    ) -> ShoppingItemsResponse:
        """Get shopping items."""
        params: dict[str, Any] = {}
        params["queryFilter"] = f"shoppingListId={shopping_list_id}"
        params["orderBy"] = ShoppingItemsOrderBy.POSITION
        params["orderDirection"] = OrderDirection.ASCENDING
        params["perPage"] = 9999
        response = await self._get("api/groups/shopping/items", params)
        return ShoppingItemsResponse.from_json(response)

    async def add_shopping_item(
        self,
        item: dict[str, Any],
    ) -> None:
        """Add a shopping item."""

        await self._post("api/groups/shopping/items", data=item)

    async def update_shopping_item(self, item_id: str, item: dict[str, Any]) -> None:
        """Update a shopping item."""

        await self._put(f"api/groups/shopping/items/{item_id}", data=item)

    async def delete_shopping_item(self, item_id: str) -> None:
        """Delete shopping item."""

        await self._delete(f"api/groups/shopping/items/{item_id}")

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
