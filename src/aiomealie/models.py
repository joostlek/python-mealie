"""Models for Mealie."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import SerializationStrategy
from mashumaro.config import BaseConfig


class OptionalStringSerializationStrategy(SerializationStrategy):
    """Serialization strategy for optional strings."""

    def serialize(self, value: str | None) -> str | None:
        """Serialize optional string."""
        return value

    def deserialize(self, value: str | None) -> str | None:
        """Deserialize optional string."""
        if not value:
            return None
        val = value.strip()
        return val if val else None


class OrderDirection(StrEnum):
    """OrderDirection type."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class ShoppingItemsOrderBy(StrEnum):
    """ShoppingItemOrderBy type."""

    POSITION = "position"


@dataclass
class About(DataClassORJSONMixin):
    """About model."""

    version: str


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
class UserInfo(DataClassORJSONMixin):
    """UserInfo model."""

    user_id: str = field(metadata=field_options(alias="id"))
    username: str
    email: str
    full_name: str = field(metadata=field_options(alias="fullName"))


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
class Tag(DataClassORJSONMixin):
    """Tag model."""

    tag_id: str = field(metadata=field_options(alias="id"))
    name: str
    slug: str


@dataclass
class Ingredient(DataClassORJSONMixin):
    """Ingredient model."""

    quantity: float | None
    note: str
    unit: str | None
    is_food: bool = field(metadata=field_options(alias="isFood"))
    reference_id: str = field(metadata=field_options(alias="referenceId"))


@dataclass
class Instruction(DataClassORJSONMixin):
    """Instruction model."""

    instruction_id: str = field(metadata=field_options(alias="id"))
    title: str | None = field(
        metadata=field_options(
            serialization_strategy=OptionalStringSerializationStrategy()
        )
    )
    text: str
    ingredient_references: list[str] = field(
        metadata=field_options(alias="ingredientReferences")
    )


@dataclass
class BaseRecipe(DataClassORJSONMixin):
    """Recipe model."""

    recipe_id: str = field(metadata=field_options(alias="id"))
    user_id: str = field(metadata=field_options(alias="userId"))
    group_id: str = field(metadata=field_options(alias="groupId"))
    name: str
    slug: str
    description: str
    image: str | None = None
    recipe_yield: str | None = field(
        default=None, metadata=field_options(alias="recipeYield")
    )
    original_url: str | None = field(
        default=None, metadata=field_options(alias="orgURL")
    )
    household_id: str | None = field(
        default=None,
        metadata=field_options(
            alias="householdId",
            serialization_strategy=OptionalStringSerializationStrategy(),
        ),
    )


@dataclass(kw_only=True)
class Recipe(BaseRecipe):
    """Recipe model."""

    tags: list[Tag]
    date_added: date = field(metadata=field_options(alias="dateAdded"))
    ingredients: list[Ingredient] = field(
        metadata=field_options(alias="recipeIngredient")
    )
    instructions: list[Instruction] = field(
        metadata=field_options(alias="recipeInstructions")
    )


@dataclass
class RecipesResponse(DataClassORJSONMixin):
    """RecipesResponse model."""

    items: list[BaseRecipe]


class MealplanEntryType(StrEnum):
    """MealplanEntryType model."""

    DINNER = "dinner"
    LUNCH = "lunch"
    BREAKFAST = "breakfast"
    SIDE = "side"


@dataclass
class Mealplan(DataClassORJSONMixin):
    """Mealplan model."""

    mealplan_id: int = field(metadata=field_options(alias="id"))
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
    recipe: BaseRecipe | None
    household_id: str | None = field(
        default=None,
        metadata=field_options(
            alias="householdId",
            serialization_strategy=OptionalStringSerializationStrategy(),
        ),
    )


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
    label_id: str | None = field(default=None, metadata=field_options(alias="labelId"))
    food_id: str | None = field(default=None, metadata=field_options(alias="foodId"))
    unit_id: str | None = field(default=None, metadata=field_options(alias="unitId"))


@dataclass
class MutateShoppingItem(DataClassDictMixin):
    """MutateShoppingItem model."""

    item_id: str | None = field(default=None, metadata=field_options(alias="id"))
    list_id: str | None = field(
        default=None, metadata=field_options(alias="shoppingListId")
    )
    note: str | None = None
    display: str | None = None
    checked: bool | None = None
    position: int | None = None
    is_food: bool | None = field(default=None, metadata=field_options(alias="isFood"))
    disable_amount: bool | None = field(
        default=None, metadata=field_options(alias="disableAmount")
    )
    quantity: float | None = None
    label_id: str | None = field(default=None, metadata=field_options(alias="labelId"))
    food_id: str | None = field(default=None, metadata=field_options(alias="foodId"))
    unit_id: str | None = field(default=None, metadata=field_options(alias="unitId"))

    class Config(BaseConfig):  # pylint: disable=too-few-public-methods
        """Mashumaro Config."""

        serialize_by_alias = True
        code_generation_options = ["TO_DICT_ADD_OMIT_NONE_FLAG"]


@dataclass
class ShoppingItemsResponse(DataClassORJSONMixin):
    """ShoppingItemsResponse model."""

    items: list[ShoppingItem]


@dataclass
class Statistics(DataClassORJSONMixin):
    """Statistics model."""

    total_recipes: int = field(metadata=field_options(alias="totalRecipes"))
    total_users: int = field(metadata=field_options(alias="totalUsers"))
    total_categories: int = field(metadata=field_options(alias="totalCategories"))
    total_tags: int = field(metadata=field_options(alias="totalTags"))
    total_tools: int = field(metadata=field_options(alias="totalTools"))
