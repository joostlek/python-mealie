"""Models for Mealie."""
from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class StartupInfo(DataClassORJSONMixin):
    """StartupInfo model."""

    is_first_login: bool = field(metadata=field_options(alias="isFirstLogin"))


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
