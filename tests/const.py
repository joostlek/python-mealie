"""Constants for tests."""
from importlib import metadata

MEALIE_URL = "https://demo.mealie.io:443"

version = metadata.version("aiomealie")

HEADERS = {
    "User-Agent": f"AioMealie/{version}",
    "Accept": "application/json, text/plain, */*",
}
