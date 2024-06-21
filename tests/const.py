"""Constants for tests."""

from aiomealie.mealie import VERSION

MEALIE_URL = "https://demo.mealie.io"

HEADERS = {
    "User-Agent": f"AioMealie/{VERSION}",
    "Accept": "application/json, text/plain, */*",
}
