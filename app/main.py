"""
Main FastAPI application.

Flow
────
  1. Meta verifies the webhook endpoint (GET /webhook).
  2. WhatsApp sends message events (POST /webhook).
     ┌─ Image message  → download media bytes, store temporarily.
     └─ Location message → reverse-geocode to a human-readable address.
  3. When both an image AND a location have been received from the same
     sender (within the same session window), the server:
       a. Builds a caption (address + hashtags).
       b. Publishes the photo to Instagram via the Graph API.

Session tracking
────────────────
  A simple in-memory dict keyed by sender phone number holds pending
  image/location data.  In production, replace this with Redis or a DB.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.geocoding import reverse_geocode
from app.instagram import publish_photo
from app.storage import UPLOAD_DIR, save_image
from app.whatsapp import download_media, parse_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── In-memory session store ───────────────────────────────────────────────────
# { phone_number: { "image_bytes": bytes, "mime": str,
#                   "latitude": float, "longitude": float } }
_sessions: dict[str, dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    UPLOAD_DIR.mkdir(exist_ok=True)
    yield


app = FastAPI(
    title="WhatsApp → Instagram Bridge",
    description=(
        "Receives photos and location messages via WhatsApp Business Cloud API "
        "and publishes them to an Instagram Business account."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Serve uploaded images publicly so Instagram's API can reach them.
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# ── Webhook verification (GET) ────────────────────────────────────────────────

@app.get("/webhook", summary="WhatsApp webhook verification challenge")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode", default=""),
    hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    hub_challenge: str = Query(alias="hub.challenge", default=""),
):
    """
    Meta calls this endpoint once when you register the webhook.
    It passes hub.verify_token; we echo back hub.challenge if it matches.
    """
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verified successfully.")
        return int(hub_challenge)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token mismatch")


# ── Incoming messages (POST) ──────────────────────────────────────────────────

@app.post("/webhook", status_code=status.HTTP_200_OK, summary="Receive WhatsApp messages")
async def receive_message(request: Request):
    """
    Handles all incoming WhatsApp message events.

    - Image messages  → download, store in session.
    - Location messages → reverse-geocode, store in session.
    - If both exist for the same sender → publish to Instagram.
    """
    payload = await request.json()
    logger.debug("Received payload: %s", payload)

    msg = parse_message(payload)
    if msg is None:
        # Not a message type we handle; acknowledge receipt and move on.
        return {"status": "ignored"}

    sender = msg.from_number
    session = _sessions.setdefault(sender, {})

    # ── Handle image message ──────────────────────────────────────────────────
    if hasattr(msg, "_media_id") and msg._media_id:  # type: ignore[attr-defined]
        try:
            image_bytes, mime = await download_media(msg._media_id)  # type: ignore[attr-defined]
            session["image_bytes"] = image_bytes
            session["mime"] = mime
            logger.info("Image received from %s (%d bytes)", sender, len(image_bytes))
        except Exception as exc:
            logger.error("Failed to download media from %s: %s", sender, exc)
            return {"status": "error", "detail": str(exc)}

    # ── Handle location message ───────────────────────────────────────────────
    if msg.latitude is not None and msg.longitude is not None:
        session["latitude"] = msg.latitude
        session["longitude"] = msg.longitude
        logger.info("Location received from %s: (%s, %s)", sender, msg.latitude, msg.longitude)

    # ── Attempt to post when both pieces are ready ────────────────────────────
    if "image_bytes" in session and "latitude" in session:
        await _post_to_instagram(sender, session)
        _sessions.pop(sender, None)   # clear session after successful post

    return {"status": "ok"}


async def _post_to_instagram(sender: str, session: dict[str, Any]) -> None:
    """
    Reverse-geocode the stored location, build a caption, upload the image,
    and publish it to Instagram.
    """
    settings = get_settings()

    lat: float = session["latitude"]
    lon: float = session["longitude"]
    image_bytes: bytes = session["image_bytes"]
    mime: str = session.get("mime", "image/jpeg")

    # 1. Reverse-geocode
    address = await reverse_geocode(lat, lon)
    logger.info("Address resolved for %s: %s", sender, address)

    # 2. Save image and build its public URL
    #    The server must be reachable from the internet (use ngrok / a real
    #    domain in development; your cloud hostname in production).
    filename = save_image(image_bytes, mime)
    public_url = f"{settings.base_url.rstrip('/')}/uploads/{filename}"

    # 3. Build caption
    caption = f"📍 {address}\n\n{settings.instagram_hashtags}"

    # 4. Publish
    try:
        media_id = await publish_photo(public_url, caption)
        logger.info("Published to Instagram (media_id=%s) for sender %s", media_id, sender)
    except Exception as exc:
        logger.error("Instagram publish failed for %s: %s", sender, exc)
        raise
