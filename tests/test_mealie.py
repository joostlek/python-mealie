"""Asynchronous Python client for Mealie."""

from __future__ import annotations

import asyncio
import json
from datetime import date
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp.hdrs import METH_GET, METH_POST, METH_PUT, METH_DELETE
from aioresponses import CallbackResult, aioresponses
import pytest
from yarl import URL

from aiomealie.exceptions import (
    MealieAuthenticationError,
    MealieConnectionError,
    MealieValidationError,
    MealieError,
    MealieNotFoundError,
    MealieBadRequestError,
)
from aiomealie.mealie import MealieClient
from aiomealie.models import MutateRecipe, MutateShoppingItem, MealplanEntryType
from tests import load_fixture

from .const import HEADERS, MEALIE_URL

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


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
        analytics = MealieClient(session=session, api_host="https://demo.mealie.io")
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
    mealie_client = MealieClient(api_host="https://demo.mealie.io", token="XXX")
    await mealie_client.get_startup_info()
    assert mealie_client.session is not None
    assert not mealie_client.session.closed
    await mealie_client.close()
    assert mealie_client.session.closed


async def test_invalid_url_error() -> None:
    """Test invalid URL error."""
    mealie_client = MealieClient(api_host="abc", token="XXX")
    with pytest.raises(MealieConnectionError):
        await mealie_client.get_startup_info()


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


async def test_authentication_error(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test authentication error from mealie."""

    responses.get(
        f"{MEALIE_URL}/api/groups/self",
        status=401,
        body=load_fixture("authentication_error.json"),
    )

    with pytest.raises(MealieAuthenticationError):
        assert await mealie_client.get_groups_self()


async def test_validation_error(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test validation error from mealie."""

    item_id: str = "64207a44-7b40-4392-a06a-bc4e10394622"

    item = MutateShoppingItem(
        list_id="27edbaab-2ec6-441f-8490-0283ea77585f", note="Bread", position=0
    )

    responses.put(
        f"{MEALIE_URL}/api/households/shopping/items/{item_id}",
        status=422,
        body=load_fixture("validation_error.json"),
    )

    with pytest.raises(MealieValidationError):
        await mealie_client.update_shopping_item(item_id, item)


async def test_not_found_error(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test not found error from mealie."""
    responses.get(
        f"{MEALIE_URL}/api/recipes/original-sacher-torte-2",
        status=404,
        body=load_fixture("not_found_error.json"),
    )

    with pytest.raises(MealieNotFoundError):
        await mealie_client.get_recipe("original-sacher-torte-2")


async def test_bad_request_error(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test not found error from mealie."""
    responses.post(
        f"{MEALIE_URL}/api/recipes/create/url",
        status=400,
        body=load_fixture("bad_request_error.json"),
    )

    with pytest.raises(MealieBadRequestError):
        await mealie_client.import_recipe(
            "https://www.sacher.com/en/original-sacher-torte/recipe/"
        )


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
        request_timeout=1, api_host="https://demo.mealie.io"
    ) as mealie_client:
        with pytest.raises(MealieConnectionError):
            assert await mealie_client.get_startup_info()


async def test_client_connection_error() -> None:
    """Test client connection error from mealie."""

    async with MealieClient(api_host="https://bad-url") as mealie_client:
        with pytest.raises(MealieConnectionError):
            assert await mealie_client.get_startup_info()


async def test_about(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving about."""
    responses.get(
        f"{MEALIE_URL}/api/app/about",
        status=200,
        body=load_fixture("about.json"),
    )
    assert await mealie_client.get_about() == snapshot


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


async def test_groups_self(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving groups self."""
    responses.get(
        f"{MEALIE_URL}/api/groups/self",
        status=200,
        body=load_fixture("groups_self.json"),
    )
    assert await mealie_client.get_groups_self() == snapshot


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


@pytest.mark.parametrize(
    ("kwargs", "params"),
    [
        ({}, {"perPage": 50}),
        ({"search": "pasta"}, {"perPage": 50, "search": "pasta"}),
        ({"search": "pasta", "per_page": 20}, {"perPage": 20, "search": "pasta"}),
    ],
)
async def test_recipes(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
    kwargs: dict[str, Any],
    params: dict[str, Any],
) -> None:
    """Test retrieving recipes with various parameters."""
    url = URL(MEALIE_URL).joinpath("api/recipes").with_query(params)
    responses.get(
        url,
        status=200,
        body=load_fixture("recipes.json"),
    )
    assert await mealie_client.get_recipes(**kwargs) == snapshot
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/recipes",
        METH_GET,
        headers=HEADERS,
        params=params,
        json=None,
    )


async def test_retrieving_recipe(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving recipe."""
    responses.get(
        f"{MEALIE_URL}/api/recipes/original-sacher-torte-2",
        status=200,
        body=load_fixture("recipe.json"),
    )
    assert await mealie_client.get_recipe("original-sacher-torte-2") == snapshot

    # Load a nested referenced recipe
    recipe_v3 = load_fixture("recipe-v3.json")
    recipe_json = json.loads(recipe_v3)
    recipe_json["recipeIngredient"][1]["referencedRecipe"] = json.loads(
        load_fixture("recipe.json")
    )

    responses.get(
        f"{MEALIE_URL}/api/recipes/maple-bars",
        status=200,
        body=json.dumps(recipe_json),
    )
    assert await mealie_client.get_recipe("maple-bars") == snapshot


async def test_importing_recipe(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test importing recipe."""
    responses.post(
        f"{MEALIE_URL}/api/recipes/create/url",
        status=201,
        body=load_fixture("scrape_recipe.json"),
    )
    responses.get(
        f"{MEALIE_URL}/api/recipes/original-sacher-torte-2",
        status=200,
        body=load_fixture("recipe.json"),
    )
    assert (
        await mealie_client.import_recipe(
            "https://www.sacher.com/en/original-sacher-torte/recipe/"
        )
        == snapshot
    )
    responses.assert_called_with(
        f"{MEALIE_URL}/api/recipes/create/url",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "url": "https://www.sacher.com/en/original-sacher-torte/recipe/",
            "include_tags": False,
        },
    )
    responses.assert_called_with(
        f"{MEALIE_URL}/api/recipes/original-sacher-torte-2",
        METH_GET,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_create_recipe(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test creating a recipe."""
    responses.post(
        f"{MEALIE_URL}/api/recipes",
        status=201,
        body=load_fixture("scrape_recipe.json"),
    )
    responses.get(
        f"{MEALIE_URL}/api/recipes/original-sacher-torte-2",
        status=200,
        body=load_fixture("recipe.json"),
    )
    assert await mealie_client.create_recipe("Original Sacher Torte") == snapshot
    responses.assert_called_with(
        f"{MEALIE_URL}/api/recipes",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={"name": "Original Sacher Torte"},
    )


async def test_update_recipe(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test updating a recipe."""
    slug = "original-sacher-torte-2"
    recipe_data = MutateRecipe(name="Updated Sacher Torte", rating=4.5)

    responses.put(
        f"{MEALIE_URL}/api/recipes/{slug}",
        status=200,
        body=load_fixture("recipe.json"),
    )
    assert await mealie_client.update_recipe(slug, recipe_data) == snapshot
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/recipes/{slug}",
        METH_PUT,
        headers=HEADERS,
        params=None,
        json={"name": "Updated Sacher Torte", "rating": 4.5},
    )


async def test_delete_recipe(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test deleting a recipe."""
    slug = "original-sacher-torte-2"

    responses.delete(
        f"{MEALIE_URL}/api/recipes/{slug}",
        status=200,
        body=load_fixture("recipe.json"),
    )
    await mealie_client.delete_recipe(slug)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/recipes/{slug}",
        METH_DELETE,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_mealplan_today(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving mealplan."""
    responses.get(
        f"{MEALIE_URL}/api/households/mealplans/today",
        status=200,
        body=load_fixture("mealplan_today.json"),
    )
    assert await mealie_client.get_mealplan_today() == snapshot


async def test_mealplans(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving mealplan."""

    params: dict[str, Any] = {
        "perPage": -1,
    }

    url = URL(MEALIE_URL).joinpath("api/households/mealplans").with_query(params)
    responses.get(
        url,
        status=200,
        body=load_fixture("mealplans.json"),
    )
    assert await mealie_client.get_mealplans() == snapshot


async def test_user_info(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving user info."""

    responses.get(
        f"{MEALIE_URL}/api/users/self",
        status=200,
        body=load_fixture("users_self.json"),
    )
    assert await mealie_client.get_user_info() == snapshot


@pytest.mark.parametrize(
    ("kwargs", "params"),
    [
        ({}, {"perPage": -1}),
        (
            {
                "start_date": date(2021, 1, 1),
                "end_date": date(2021, 1, 2),
            },
            {
                "start_date": "2021-01-01",
                "end_date": "2021-01-02",
                "perPage": -1,
            },
        ),
    ],
)
async def test_mealplans_parameters(
    responses: aioresponses,
    mealie_client: MealieClient,
    kwargs: dict[str, Any],
    params: dict[str, Any],
) -> None:
    """Test retrieving mealplans."""

    url = URL(MEALIE_URL).joinpath("api/households/mealplans").with_query(params)
    responses.get(
        url,
        status=200,
        body=load_fixture("mealplans.json"),
    )
    assert await mealie_client.get_mealplans(**kwargs)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/mealplans",
        METH_GET,
        headers=HEADERS,
        params=params,
        json=None,
    )


async def test_shopping_lists(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving shopping lists."""

    params: dict[str, Any] = {
        "perPage": -1,
    }

    url = URL(MEALIE_URL).joinpath("api/households/shopping/lists").with_query(params)
    responses.get(
        url,
        status=200,
        body=load_fixture("shopping_lists.json"),
    )
    assert await mealie_client.get_shopping_lists() == snapshot


async def test_shopping_items(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving shopping items."""

    shopping_list_id: str = "27edbaab-2ec6-441f-8490-0283ea77585f"
    params: dict[str, Any] = {
        "queryFilter": f"shoppingListId={shopping_list_id}",
        "orderBy": "position",
        "orderDirection": "asc",
        "perPage": -1,
    }

    url = URL(MEALIE_URL).joinpath("api/households/shopping/items").with_query(params)
    responses.get(
        url,
        status=200,
        body=load_fixture("shopping_items.json"),
    )
    assert (
        await mealie_client.get_shopping_items(shopping_list_id=shopping_list_id)
        == snapshot
    )

    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/items",
        METH_GET,
        headers=HEADERS,
        params=params,
        json=None,
    )


async def test_add_shopping_item(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test adding shopping item."""

    item = MutateShoppingItem(
        list_id="27edbaab-2ec6-441f-8490-0283ea77585f", note="Bread", position=0
    )

    responses.post(
        f"{MEALIE_URL}/api/households/shopping/items",
        status=201,
    )
    await mealie_client.add_shopping_item(item=item)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/items",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "shoppingListId": "27edbaab-2ec6-441f-8490-0283ea77585f",
            "note": "Bread",
            "position": 0,
        },
    )


async def test_update_shopping_item(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test updating shopping item."""

    item_id: str = "64207a44-7b40-4392-a06a-bc4e10394622"

    item = MutateShoppingItem(
        list_id="27edbaab-2ec6-441f-8490-0283ea77585f", note="Bread", position=0
    )

    responses.put(
        f"{MEALIE_URL}/api/households/shopping/items/{item_id}",
        status=201,
    )
    await mealie_client.update_shopping_item(item_id=item_id, item=item)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/items/{item_id}",
        METH_PUT,
        headers=HEADERS,
        params=None,
        json={
            "shoppingListId": "27edbaab-2ec6-441f-8490-0283ea77585f",
            "note": "Bread",
            "position": 0,
        },
    )


async def test_delete_shopping_item(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test deleting shopping item."""

    item_id: str = "64207a44-7b40-4392-a06a-bc4e10394622"

    responses.delete(
        f"{MEALIE_URL}/api/households/shopping/items/{item_id}",
        status=201,
    )
    await mealie_client.delete_shopping_item(item_id=item_id)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/items/{item_id}",
        METH_DELETE,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_statistics(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving statistics."""
    responses.get(
        f"{MEALIE_URL}/api/households/statistics",
        status=200,
        body=load_fixture("statistics.json"),
    )
    assert await mealie_client.get_statistics() == snapshot


async def test_random_mealplan(
    responses: aioresponses, mealie_client: MealieClient, snapshot: SnapshotAssertion
) -> None:
    """Test setting random mealplan."""

    responses.post(
        f"{MEALIE_URL}/api/households/mealplans/random",
        status=201,
        body=load_fixture("mealplan.json"),
    )
    assert (
        await mealie_client.random_mealplan(
            at=date(2021, 1, 1), entry_type=MealplanEntryType.BREAKFAST
        )
    ) == snapshot
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/mealplans/random",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "date": "2021-01-01",
            "entryType": "breakfast",
        },
    )


@pytest.mark.parametrize(
    ("kwargs", "data"),
    [
        ({"recipe_id": "abc"}, {"recipeId": "abc"}),
        ({"note_title": "title"}, {"title": "title"}),
        (
            {"note_title": "title", "note_text": "description"},
            {"title": "title", "text": "description"},
        ),
    ],
)
async def test_set_mealplan(
    responses: aioresponses,
    mealie_client: MealieClient,
    kwargs: dict[str, Any],
    data: dict[str, Any],
) -> None:
    """Test setting mealplan."""

    responses.post(
        f"{MEALIE_URL}/api/households/mealplans",
        status=201,
        body=load_fixture("mealplan.json"),
    )

    await mealie_client.set_mealplan(
        at=date(2021, 1, 1), entry_type=MealplanEntryType.BREAKFAST, **kwargs
    )
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/mealplans",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={
            "date": "2021-01-01",
            "entryType": "breakfast",
        }
        | data,
    )


LIST_ID = "27edbaab-2ec6-441f-8490-0283ea77585f"
GROUP_ID = "9ed7c880-3e85-4955-9318-1443d6e080fe"
USER_ID = "bf1c62fe-4941-4332-9886-e54e88dbdba0"


async def test_get_categories(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving categories."""
    url = (
        URL(MEALIE_URL)
        .joinpath("api/organizers/categories")
        .with_query({"perPage": -1})
    )
    responses.get(url, status=200, body=load_fixture("categories.json"))
    assert await mealie_client.get_categories() == snapshot


async def test_get_tags(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving tags."""
    url = URL(MEALIE_URL).joinpath("api/organizers/tags").with_query({"perPage": -1})
    responses.get(url, status=200, body=load_fixture("tags.json"))
    assert await mealie_client.get_tags() == snapshot


async def test_get_tools(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving tools."""
    url = URL(MEALIE_URL).joinpath("api/organizers/tools").with_query({"perPage": -1})
    responses.get(url, status=200, body=load_fixture("tools.json"))
    assert await mealie_client.get_tools() == snapshot


async def test_get_foods(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving foods."""
    url = URL(MEALIE_URL).joinpath("api/foods").with_query({"perPage": -1})
    responses.get(url, status=200, body=load_fixture("foods.json"))
    assert await mealie_client.get_foods() == snapshot


async def test_get_units(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving units."""
    url = URL(MEALIE_URL).joinpath("api/units").with_query({"perPage": -1})
    responses.get(url, status=200, body=load_fixture("units.json"))
    assert await mealie_client.get_units() == snapshot


async def test_get_shopping_list(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving a single shopping list."""
    responses.get(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}",
        status=200,
        body=load_fixture("shopping_list.json"),
    )
    assert await mealie_client.get_shopping_list(LIST_ID) == snapshot


async def test_create_shopping_list(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test creating a shopping list."""
    responses.post(
        f"{MEALIE_URL}/api/households/shopping/lists",
        status=201,
        body=load_fixture("shopping_list.json"),
    )
    assert await mealie_client.create_shopping_list("Supermarket") == snapshot
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/lists",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={"name": "Supermarket"},
    )


async def test_update_shopping_list(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test updating a shopping list."""
    responses.get(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}",
        status=200,
        body=load_fixture("shopping_list.json"),
    )
    responses.put(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}",
        status=200,
        body=load_fixture("shopping_list.json"),
    )
    assert await mealie_client.update_shopping_list(LIST_ID, "Supermarket") == snapshot
    responses.assert_called_with(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}",
        METH_PUT,
        headers=HEADERS,
        params=None,
        json={"id": LIST_ID, "name": "Supermarket", "groupId": GROUP_ID},
    )


async def test_delete_shopping_list(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test deleting a shopping list."""
    responses.delete(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}",
        status=200,
        body=load_fixture("shopping_list.json"),
    )
    await mealie_client.delete_shopping_list(LIST_ID)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}",
        METH_DELETE,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_add_recipe_to_shopping_list(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test adding a recipe to a shopping list."""
    recipe_id = "40393996-417e-4487-a081-28608a668826"
    responses.post(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}/recipe/{recipe_id}",
        status=200,
        body=load_fixture("shopping_list.json"),
    )
    assert (
        await mealie_client.add_recipe_to_shopping_list(LIST_ID, recipe_id)
    ) == snapshot
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}/recipe/{recipe_id}",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={"recipeIncrementQuantity": 1.0},
    )


async def test_remove_recipe_from_shopping_list(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test removing a recipe from a shopping list."""
    recipe_id = "40393996-417e-4487-a081-28608a668826"
    responses.post(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}/recipe/{recipe_id}/delete",
        status=200,
        body=load_fixture("shopping_list.json"),
    )
    await mealie_client.remove_recipe_from_shopping_list(LIST_ID, recipe_id)
    responses.assert_called_once_with(
        f"{MEALIE_URL}/api/households/shopping/lists/{LIST_ID}/recipe/{recipe_id}/delete",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={"recipeDecrementQuantity": 1.0},
    )


async def test_get_recipe_favorites(
    responses: aioresponses,
    mealie_client: MealieClient,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving recipe favorites."""
    responses.get(
        f"{MEALIE_URL}/api/users/self/favorites",
        status=200,
        body=load_fixture("recipe_favorites.json"),
    )
    assert await mealie_client.get_recipe_favorites() == snapshot


async def test_add_recipe_favorite(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test adding a recipe to favorites."""
    slug = "cauliflower-salad"
    responses.get(
        f"{MEALIE_URL}/api/users/self",
        status=200,
        body=load_fixture("users_self.json"),
    )
    responses.post(
        f"{MEALIE_URL}/api/users/{USER_ID}/favorites/{slug}",
        status=200,
        body="{}",
    )
    await mealie_client.add_recipe_favorite(slug)
    responses.assert_called_with(
        f"{MEALIE_URL}/api/users/{USER_ID}/favorites/{slug}",
        METH_POST,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_remove_recipe_favorite(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test removing a recipe from favorites."""
    slug = "cauliflower-salad"
    responses.get(
        f"{MEALIE_URL}/api/users/self",
        status=200,
        body=load_fixture("users_self.json"),
    )
    responses.delete(
        f"{MEALIE_URL}/api/users/{USER_ID}/favorites/{slug}",
        status=200,
        body="{}",
    )
    await mealie_client.remove_recipe_favorite(slug)
    responses.assert_called_with(
        f"{MEALIE_URL}/api/users/{USER_ID}/favorites/{slug}",
        METH_DELETE,
        headers=HEADERS,
        params=None,
        json=None,
    )


async def test_rate_recipe(
    responses: aioresponses,
    mealie_client: MealieClient,
) -> None:
    """Test rating a recipe."""
    slug = "cauliflower-salad"
    responses.get(
        f"{MEALIE_URL}/api/users/self",
        status=200,
        body=load_fixture("users_self.json"),
    )
    responses.post(
        f"{MEALIE_URL}/api/users/{USER_ID}/ratings/{slug}",
        status=200,
        body="{}",
    )
    await mealie_client.rate_recipe(slug, rating=4.5, is_favorite=True)
    responses.assert_called_with(
        f"{MEALIE_URL}/api/users/{USER_ID}/ratings/{slug}",
        METH_POST,
        headers=HEADERS,
        params=None,
        json={"rating": 4.5, "isFavorite": True},
    )
