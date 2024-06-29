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
    BaseRecipe,
    RecipesResponse,
    Mealplan,
    MealplanResponse,
    MealplanEntryType,
    ShoppingList,
    ShoppingListsResponse,
    ShoppingItem,
    ShoppingItemsResponse,
    UserInfo,
    Recipe,
    Instruction,
    Ingredient,
    Tag,
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
    "BaseRecipe",
    "Recipe",
    "Instruction",
    "Ingredient",
    "Tag",
    "RecipesResponse",
    "Mealplan",
    "MealplanResponse",
    "MealplanEntryType",
    "ShoppingItem",
    "ShoppingItemsResponse",
    "ShoppingList",
    "ShoppingListsResponse",
    "UserInfo",
]
