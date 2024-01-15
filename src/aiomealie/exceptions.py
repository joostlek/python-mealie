"""Asynchronous Python client for Mealie."""


class MealieError(Exception):
    """Generic exception."""


class MealieConnectionError(MealieError):
    """Mealie connection exception."""
