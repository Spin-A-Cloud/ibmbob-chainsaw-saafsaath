"""
Reverse-geocoding service using the free OpenStreetMap Nominatim API.

No API key required.  Respects the usage policy by sending a descriptive
User-Agent header and caching results in memory for the process lifetime.
"""
from __future__ import annotations

import logging
from functools import lru_cache

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"


@lru_cache(maxsize=256)
def _cached_lookup(lat: float, lon: float) -> str:
    """Synchronous cached wrapper — called from the async helper below."""
    settings = get_settings()
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
    }
    headers = {"User-Agent": settings.nominatim_user_agent}

    with httpx.Client(timeout=10) as client:
        resp = client.get(NOMINATIM_URL, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # Build a short, human-readable address from the structured response
    addr = data.get("address", {})
    parts = [
        addr.get("road") or addr.get("pedestrian"),
        addr.get("suburb") or addr.get("neighbourhood"),
        addr.get("city") or addr.get("town") or addr.get("village"),
        addr.get("state"),
        addr.get("country"),
    ]
    return ", ".join(p for p in parts if p)


async def reverse_geocode(lat: float, lon: float) -> str:
    """
    Return a human-readable address string for the given coordinates.

    Falls back to a plain coordinate string if the lookup fails.
    """
    try:
        # _cached_lookup is synchronous; run it directly (network I/O is
        # short and results are cached, so blocking the event loop briefly
        # is acceptable for this use-case).
        return _cached_lookup(lat, lon)
    except Exception as exc:
        logger.warning("Reverse geocoding failed for (%s, %s): %s", lat, lon, exc)
        return f"{lat:.5f}, {lon:.5f}"
