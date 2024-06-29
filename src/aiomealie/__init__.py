"""Asynchronous Python client for Mealie."""

from aiomealie.exceptions import (
    MealieConnectionError,
    MealieError,
    MealieAuthenticationError,
    MealieValidationError,
)
from aiomealie.mealie import MealieClient
from aiomealie.models import (
    StartupInfo,
    GroupSummary,
    Theme,
    Recipe,
    RecipesResponse,
    Mealplan,
    MealplanResponse,
    MealplanEntryType,
    ShoppingListsResponse,
    ShoppingItemsResponse,
    UserInfo,
)

__all__ = [
    "MealieConnectionError",
    "MealieError",
    "MealieAuthenticationError",
    "MealieValidationError",
    "MealieClient",
    "StartupInfo",
    "GroupSummary",
    "Theme",
    "Recipe",
    "RecipesResponse",
    "Mealplan",
    "MealplanResponse",
    "MealplanEntryType",
    "ShoppingListsResponse",
    "ShoppingItemsResponse",
    "UserInfo",
]
