"""
WhatsApp Business Cloud API service.

Responsibilities:
  - Verify the webhook subscription challenge (GET /webhook)
  - Parse incoming message payloads to extract image media IDs and location
  - Download the binary image bytes using the media URL endpoint
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v19.0"


@dataclass
class IncomingMessage:
    """Normalised representation of a WhatsApp message we care about."""
    from_number: str
    image_bytes: Optional[bytes] = None      # raw JPEG/PNG from WhatsApp
    image_mime: str = "image/jpeg"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


async def download_media(media_id: str) -> tuple[bytes, str]:
    """
    Resolve a WhatsApp media_id to its download URL, then fetch the bytes.

    Returns (raw_bytes, mime_type).
    """
    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.whatsapp_api_token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1 – get the temporary download URL
        meta_resp = await client.get(
            f"{GRAPH_BASE}/{media_id}",
            headers=headers,
        )
        meta_resp.raise_for_status()
        meta = meta_resp.json()
        download_url: str = meta["url"]
        mime_type: str = meta.get("mime_type", "image/jpeg")

        # Step 2 – download the actual binary
        img_resp = await client.get(download_url, headers=headers)
        img_resp.raise_for_status()
        return img_resp.content, mime_type


def parse_message(payload: dict) -> Optional[IncomingMessage]:
    """
    Parse a WhatsApp Cloud API webhook payload.

    The payload may contain an image message, a location message, or both
    sent in quick succession.  We parse a *single* message event at a time;
    the caller is responsible for iterating over multiple entries/changes.

    Returns an IncomingMessage if the payload contains image or location data,
    otherwise None.
    """
    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
        messages = value.get("messages", [])
        if not messages:
            return None

        msg = messages[0]
        from_number: str = msg.get("from", "")
        result = IncomingMessage(from_number=from_number)

        msg_type = msg.get("type")

        if msg_type == "image":
            result.image_bytes = None          # will be downloaded asynchronously
            result._media_id = msg["image"]["id"]  # type: ignore[attr-defined]
            result.image_mime = msg["image"].get("mime_type", "image/jpeg")

        elif msg_type == "location":
            loc = msg["location"]
            result.latitude = loc["latitude"]
            result.longitude = loc["longitude"]

        else:
            return None

        return result

    except (KeyError, IndexError) as exc:
        logger.warning("Could not parse WhatsApp payload: %s", exc)
        return None
