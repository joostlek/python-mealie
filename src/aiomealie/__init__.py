"""Asynchronous Python client for Mealie."""

from aiomealie.exceptions import (
    MealieConnectionError,
    MealieError,
    MealieAuthenticationError,
)
from aiomealie.mealie import MealieClient
from aiomealie.models import (
    StartupInfo,
    Theme,
    Recipe,
    RecipesResponse,
    Mealplan,
    MealplanResponse,
    MealplanEntryType,
)

__all__ = [
    "MealieConnectionError",
    "MealieError",
    "MealieAuthenticationError",
    "MealieClient",
    "StartupInfo",
    "Theme",
    "Recipe",
    "RecipesResponse",
    "Mealplan",
    "MealplanResponse",
    "MealplanEntryType",
]
