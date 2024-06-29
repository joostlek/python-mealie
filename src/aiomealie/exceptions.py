"""Asynchronous Python client for Mealie."""


class MealieError(Exception):
    """Generic exception."""


class MealieConnectionError(MealieError):
    """Mealie connection exception."""


class MealieAuthenticationError(MealieError):
    """Mealie authentication exception."""


class MealieValidationError(MealieError):
    """Mealie validation exception."""


class MealieNotFoundError(MealieError):
    """Mealie not found exception."""


class MealieBadRequestError(MealieError):
    """Mealie bad request exception."""
