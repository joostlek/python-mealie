"""Models for Mealie."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import SerializationStrategy


class OrderDirection(StrEnum):
    """OrderDirection type."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class ShoppingItemsOrderBy(StrEnum):
    """ShoppingItemOrderBy type."""

    POSITION = "position"


@dataclass
class StartupInfo(DataClassORJSONMixin):
    """StartupInfo model."""

    is_first_login: bool = field(metadata=field_options(alias="isFirstLogin"))


@dataclass
class GroupSummary(DataClassORJSONMixin):
    """GroupSummary model."""

    name: str
    group_id: str = field(metadata=field_options(alias="id"))
    slug: str


@dataclass
class Theme(DataClassORJSONMixin):
    """Theme model."""

    light_primary: str = field(metadata=field_options(alias="lightPrimary"))
    light_accent: str = field(metadata=field_options(alias="lightAccent"))
    light_secondary: str = field(metadata=field_options(alias="lightSecondary"))
    light_success: str = field(metadata=field_options(alias="lightSuccess"))
    light_info: str = field(metadata=field_options(alias="lightInfo"))
    light_warning: str = field(metadata=field_options(alias="lightWarning"))
    light_error: str = field(metadata=field_options(alias="lightError"))
    dark_primary: str = field(metadata=field_options(alias="darkPrimary"))
    dark_accent: str = field(metadata=field_options(alias="darkAccent"))
    dark_secondary: str = field(metadata=field_options(alias="darkSecondary"))
    dark_success: str = field(metadata=field_options(alias="darkSuccess"))
    dark_info: str = field(metadata=field_options(alias="darkInfo"))
    dark_warning: str = field(metadata=field_options(alias="darkWarning"))
    dark_error: str = field(metadata=field_options(alias="darkError"))


@dataclass
class Recipe(DataClassORJSONMixin):
    """Recipe model."""

    recipe_id: str = field(metadata=field_options(alias="id"))
    user_id: str = field(metadata=field_options(alias="userId"))
    group_id: str = field(metadata=field_options(alias="groupId"))
    name: str
    slug: str
    image: str
    recipe_yield: str = field(metadata=field_options(alias="recipeYield"))
    description: str
    original_url: str = field(metadata=field_options(alias="orgURL"))


@dataclass
class RecipesResponse(DataClassORJSONMixin):
    """RecipesResponse model."""

    items: list[Recipe]


class OptionalStringSerializationStrategy(SerializationStrategy):
    """Serialization strategy for optional strings."""

    def serialize(self, value: str | None) -> str | None:
        """Serialize optional string."""
        return value

    def deserialize(self, value: str) -> str | None:
        """Deserialize optional string."""
        val = value.strip()
        return val if val else None


class MealplanEntryType(StrEnum):
    """MealplanEntryType model."""

    DINNER = "dinner"
    LUNCH = "lunch"
    BREAKFAST = "breakfast"
    SIDE = "side"


@dataclass
class Mealplan(DataClassORJSONMixin):
    """Mealplan model."""

    mealplan_id: str = field(metadata=field_options(alias="id"))
    user_id: str = field(metadata=field_options(alias="userId"))
    group_id: str = field(metadata=field_options(alias="groupId"))
    entry_type: MealplanEntryType = field(metadata=field_options(alias="entryType"))
    mealplan_date: date = field(metadata=field_options(alias="date"))
    title: str | None = field(
        metadata=field_options(
            serialization_strategy=OptionalStringSerializationStrategy()
        )
    )
    description: str | None = field(
        metadata=field_options(
            alias="text", serialization_strategy=OptionalStringSerializationStrategy()
        )
    )
    recipe: Recipe | None


@dataclass
class MealplanResponse(DataClassORJSONMixin):
    """MealplanResponse model."""

    items: list[Mealplan]


@dataclass
class ShoppingList(DataClassORJSONMixin):
    """ShoppingList model."""

    list_id: str = field(metadata=field_options(alias="id"))
    name: str


@dataclass
class ShoppingListsResponse(DataClassORJSONMixin):
    """ShoppingListsResponse model."""

    items: list[ShoppingList]


@dataclass
class ShoppingItem(DataClassORJSONMixin):
    """ShoppingItem model."""

    item_id: str = field(metadata=field_options(alias="id"))
    list_id: str = field(metadata=field_options(alias="shoppingListId"))
    note: str
    display: str
    checked: bool
    position: int
    is_food: bool = field(metadata=field_options(alias="isFood"))
    disable_amount: bool = field(metadata=field_options(alias="disableAmount"))
    quantity: float
    label_id: str = field(metadata=field_options(alias="labelId"))
    food_id: str = field(metadata=field_options(alias="foodId"))
    unit_id: str = field(metadata=field_options(alias="unitId"))


@dataclass
class ShoppingItemsResponse(DataClassORJSONMixin):
    """ShoppingItemsResponse model."""

    items: list[ShoppingItem]
