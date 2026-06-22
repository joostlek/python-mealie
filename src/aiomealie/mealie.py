"""Mealie Client."""

from __future__ import annotations


import asyncio
import json
from dataclasses import dataclass
from importlib import metadata
from typing import TYPE_CHECKING, Any, Self

from aiohttp import ClientSession, ClientConnectionError, InvalidUrlClientError
from aiohttp.hdrs import METH_GET, METH_POST, METH_PUT, METH_DELETE
from mashumaro.codecs.orjson import ORJSONDecoder
from yarl import URL

from aiomealie.exceptions import (
    MealieConnectionError,
    MealieError,
    MealieAuthenticationError,
    MealieValidationError,
    MealieNotFoundError,
    MealieBadRequestError,
)
from aiomealie.models import (
    About,
    CategoriesResponse,
    FoodsResponse,
    GroupSummary,
    Mealplan,
    MealplanEntryType,
    MealplanResponse,
    MutateRecipe,
    OrderDirection,
    RecipeFavoritesResponse,
    RecipesResponse,
    ShoppingList,
    ShoppingListsResponse,
    MutateShoppingItem,
    ShoppingItemsOrderBy,
    ShoppingItemsResponse,
    StartupInfo,
    TagsResponse,
    Theme,
    ToolsResponse,
    UnitsResponse,
    UserInfo,
    Recipe,
    Statistics,
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
    _user_id: str | None = None
    _close_session: bool = False
    _version: str | None = None

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

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method, url, headers=headers, params=params, json=data
                )
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to Mealie"
            raise MealieConnectionError(msg) from exception
        except ClientConnectionError as exception:
            msg = "Client connection error while connecting to Mealie"
            raise MealieConnectionError(msg) from exception
        except InvalidUrlClientError as exception:
            msg = "Invalid URL found while connecting to Mealie"
            raise MealieConnectionError(msg) from exception

        if response.status == 400:
            msg = "Bad request to Mealie"
            raise MealieBadRequestError(
                msg,
            )

        if response.status == 401:
            msg = "Unauthorized access to Mealie"
            raise MealieAuthenticationError(msg)

        if response.status == 422:
            msg = "Mealie validation error"
            raise MealieValidationError(
                msg,
            )

        if response.status == 404:
            msg = "Object not found in Mealie"
            raise MealieNotFoundError(
                msg,
            )

        content_type = response.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            msg = "Unexpected response from Mealie"
            raise MealieError(
                msg,
                {"Content-Type": content_type},
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

    async def get_version(self) -> str:
        """Return the version, retrieve from get_about if not stored."""
        if not self._version:
            about = await self.get_about()
            self._version = about.version
        return self._version

    @property
    async def version(self) -> str:
        """Backward-compatible alias for get_version()."""
        return await self.get_version()

    async def get_startup_info(self) -> StartupInfo:
        """Get startup info."""
        response = await self._get("api/app/about/startup-info")
        return StartupInfo.from_json(response)

    async def get_about(self) -> About:
        """Get about info."""
        response = await self._get("api/app/about")
        return About.from_json(response)

    async def get_user_info(self) -> UserInfo:
        """Get user info."""
        response = await self._get("api/users/self")
        return UserInfo.from_json(response)

    async def get_groups_self(self) -> GroupSummary:
        """Get groups self."""
        response = await self._get("api/groups/self")
        return GroupSummary.from_json(response)

    async def get_theme(self) -> Theme:
        """Get theme."""
        response = await self._get("api/app/about/theme")
        return Theme.from_json(response)

    async def get_recipes(
        self, search: str | None = None, per_page: int = 50
    ) -> RecipesResponse:
        """Get recipes."""
        params: dict[str, Any] = {}
        params["perPage"] = per_page
        if search:
            params["search"] = search
        response = await self._get("api/recipes", params=params)
        return RecipesResponse.from_json(response)

    async def get_recipe(self, recipe_id_or_slug: str) -> Recipe:
        """Get recipe."""
        response = await self._get(f"api/recipes/{recipe_id_or_slug}")
        return Recipe.from_json(response)

    async def import_recipe(self, url: str, include_tags: bool = False) -> Recipe:
        """Import a recipe."""
        data = {"url": url, "include_tags": include_tags}
        response = await self._post("api/recipes/create/url", data)
        return await self.get_recipe(json.loads(response))

    async def create_recipe(self, name: str) -> Recipe:
        """Create a new recipe with the given name."""
        response = await self._post("api/recipes", data={"name": name})
        return await self.get_recipe(json.loads(response))

    async def update_recipe(self, slug: str, recipe_data: MutateRecipe) -> Recipe:
        """Update a recipe by slug."""
        response = await self._put(
            f"api/recipes/{slug}", data=recipe_data.to_dict(omit_none=True)
        )
        return Recipe.from_json(response)

    async def delete_recipe(self, slug: str) -> None:
        """Delete a recipe by slug."""
        await self._delete(f"api/recipes/{slug}")

    async def get_categories(self, per_page: int = -1) -> CategoriesResponse:
        """Get all recipe categories. Pass per_page=-1 to retrieve all pages."""
        response = await self._get(
            "api/organizers/categories", params={"perPage": per_page}
        )
        return CategoriesResponse.from_json(response)

    async def get_tags(self, per_page: int = -1) -> TagsResponse:
        """Get all recipe tags. Pass per_page=-1 to retrieve all pages."""
        response = await self._get("api/organizers/tags", params={"perPage": per_page})
        return TagsResponse.from_json(response)

    async def get_tools(self, per_page: int = -1) -> ToolsResponse:
        """Get all recipe tools. Pass per_page=-1 to retrieve all pages."""
        response = await self._get("api/organizers/tools", params={"perPage": per_page})
        return ToolsResponse.from_json(response)

    async def get_foods(self, per_page: int = -1) -> FoodsResponse:
        """Get all foods. Pass per_page=-1 to retrieve all pages."""
        response = await self._get("api/foods", params={"perPage": per_page})
        return FoodsResponse.from_json(response)

    async def get_units(self, per_page: int = -1) -> UnitsResponse:
        """Get all units. Pass per_page=-1 to retrieve all pages."""
        response = await self._get("api/units", params={"perPage": per_page})
        return UnitsResponse.from_json(response)

    async def get_mealplan_today(self) -> list[Mealplan]:
        """Get mealplan."""
        response = await self._get("api/households/mealplans/today")
        return ORJSONDecoder(list[Mealplan]).decode(response)

    async def get_mealplans(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> MealplanResponse:
        """Get mealplans."""
        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        params["perPage"] = -1
        response = await self._get("api/households/mealplans", params)
        return MealplanResponse.from_json(response)

    async def get_shopping_lists(self) -> ShoppingListsResponse:
        """Get shopping lists."""
        params: dict[str, Any] = {}
        params["perPage"] = -1
        response = await self._get("api/households/shopping/lists", params)
        return ShoppingListsResponse.from_json(response)

    async def get_shopping_list(self, list_id: str) -> ShoppingList:
        """Get a single shopping list by ID."""
        response = await self._get(f"api/households/shopping/lists/{list_id}")
        return ShoppingList.from_json(response)

    async def create_shopping_list(self, name: str) -> ShoppingList:
        """Create a new shopping list."""
        response = await self._post(
            "api/households/shopping/lists", data={"name": name}
        )
        return ShoppingList.from_json(response)

    async def update_shopping_list(self, list_id: str, name: str) -> ShoppingList:
        """Update a shopping list's name."""
        existing = await self.get_shopping_list(list_id)
        data: dict[str, Any] = {"id": list_id, "name": name}
        if existing.group_id:
            data["groupId"] = existing.group_id
        response = await self._put(
            f"api/households/shopping/lists/{list_id}", data=data
        )
        return ShoppingList.from_json(response)

    async def delete_shopping_list(self, list_id: str) -> None:
        """Delete a shopping list."""
        await self._delete(f"api/households/shopping/lists/{list_id}")

    async def add_recipe_to_shopping_list(
        self,
        list_id: str,
        recipe_id: str,
        *,
        scale: float = 1.0,
    ) -> ShoppingList:
        """Add a recipe's ingredients to a shopping list."""
        response = await self._post(
            f"api/households/shopping/lists/{list_id}/recipe/{recipe_id}",
            data={"recipeIncrementQuantity": scale},
        )
        return ShoppingList.from_json(response)

    async def remove_recipe_from_shopping_list(
        self,
        list_id: str,
        recipe_id: str,
        *,
        scale: float = 1.0,
    ) -> None:
        """Remove a recipe's ingredients from a shopping list."""
        await self._post(
            f"api/households/shopping/lists/{list_id}/recipe/{recipe_id}/delete",
            data={"recipeDecrementQuantity": scale},
        )

    async def get_shopping_items(
        self,
        shopping_list_id: str,
    ) -> ShoppingItemsResponse:
        """Get shopping items."""
        params: dict[str, Any] = {}
        params["queryFilter"] = f"shoppingListId={shopping_list_id}"
        params["orderBy"] = ShoppingItemsOrderBy.POSITION
        params["orderDirection"] = OrderDirection.ASCENDING
        params["perPage"] = -1
        response = await self._get("api/households/shopping/items", params)
        return ShoppingItemsResponse.from_json(response)

    async def add_shopping_item(
        self,
        item: MutateShoppingItem,
    ) -> None:
        """Add a shopping item."""

        await self._post(
            "api/households/shopping/items", data=item.to_dict(omit_none=True)
        )

    async def update_shopping_item(
        self, item_id: str, item: MutateShoppingItem
    ) -> None:
        """Update a shopping item."""

        await self._put(
            f"api/households/shopping/items/{item_id}",
            data=item.to_dict(omit_none=True),
        )

    async def delete_shopping_item(self, item_id: str) -> None:
        """Delete shopping item."""

        await self._delete(
            f"api/households/shopping/items/{item_id}",
        )

    async def _get_user_id(self) -> str:
        """Return cached user id, fetching from API if needed."""
        if not self._user_id:
            user_info = await self.get_user_info()
            self._user_id = user_info.user_id
        return self._user_id

    async def get_recipe_favorites(self) -> RecipeFavoritesResponse:
        """Get current user's favorite recipes."""
        response = await self._get("api/users/self/favorites")
        return RecipeFavoritesResponse.from_json(response)

    async def add_recipe_favorite(self, recipe_slug: str) -> None:
        """Add a recipe to the current user's favorites."""
        user_id = await self._get_user_id()
        await self._post(f"api/users/{user_id}/favorites/{recipe_slug}")

    async def remove_recipe_favorite(self, recipe_slug: str) -> None:
        """Remove a recipe from the current user's favorites."""
        user_id = await self._get_user_id()
        await self._delete(f"api/users/{user_id}/favorites/{recipe_slug}")

    async def rate_recipe(
        self,
        recipe_slug: str,
        *,
        rating: float | None = None,
        is_favorite: bool | None = None,
    ) -> None:
        """Set a rating or favorite flag for a recipe."""
        user_id = await self._get_user_id()
        data: dict[str, float | bool] = {}
        if rating is not None:
            data["rating"] = rating
        if is_favorite is not None:
            data["isFavorite"] = is_favorite
        await self._post(f"api/users/{user_id}/ratings/{recipe_slug}", data=data)

    async def get_statistics(self) -> Statistics:
        """Get statistics."""

        response = await self._get("api/households/statistics")
        return Statistics.from_json(response)

    async def random_mealplan(
        self, at: date, entry_type: MealplanEntryType
    ) -> Mealplan:
        """Set a random mealplan for a specific date."""
        response = await self._post(
            "api/households/mealplans/random",
            {
                "date": at.isoformat(),
                "entryType": entry_type.value,
            },
        )
        return Mealplan.from_json(response)

    async def set_mealplan(
        self,
        at: date,
        entry_type: MealplanEntryType,
        *,
        recipe_id: str | None = None,
        note_title: str | None = None,
        note_text: str | None = None,
    ) -> Mealplan:
        """Set a mealplan for a specific date."""
        data = {
            "date": at.isoformat(),
            "entryType": entry_type.value,
        }
        if recipe_id:
            data["recipeId"] = recipe_id
        if note_title:
            data["title"] = note_title
            if note_text:
                data["text"] = note_text
        response = await self._post("api/households/mealplans", data)
        return Mealplan.from_json(response)

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
