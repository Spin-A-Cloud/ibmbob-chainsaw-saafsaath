"""
Instagram Graph API service.

Posts a photo to an Instagram Business / Creator account using the
two-step container-create → publish flow required by the Graph API.

Docs: https://developers.facebook.com/docs/instagram-api/guides/content-publishing
"""
from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.facebook.com/v19.0"


async def publish_photo(image_url: str, caption: str) -> str:
    """
    Publish a photo to Instagram in two steps:
      1. Create a media container (returns a container_id)
      2. Publish the container

    `image_url` must be a publicly accessible HTTPS URL.

    Returns the published media ID.
    Raises httpx.HTTPStatusError on API failure.
    """
    settings = get_settings()
    account_id = settings.instagram_account_id
    access_token = settings.instagram_access_token

    async with httpx.AsyncClient(timeout=60) as client:
        # ── Step 1: Create container ──────────────────────────────────────────
        container_resp = await client.post(
            f"{GRAPH_BASE}/{account_id}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token,
            },
        )
        container_resp.raise_for_status()
        container_id: str = container_resp.json()["id"]
        logger.info("Instagram container created: %s", container_id)

        # ── Step 2: Publish container ─────────────────────────────────────────
        publish_resp = await client.post(
            f"{GRAPH_BASE}/{account_id}/media_publish",
            params={
                "creation_id": container_id,
                "access_token": access_token,
            },
        )
        publish_resp.raise_for_status()
        media_id: str = publish_resp.json()["id"]
        logger.info("Instagram post published: %s", media_id)
        return media_id
