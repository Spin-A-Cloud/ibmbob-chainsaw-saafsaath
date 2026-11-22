"""
Temporary public image hosting helper.

Instagram's Graph API requires a *publicly accessible HTTPS URL* for the
image at container-creation time.  This module saves the raw bytes to a
local directory and serves them via FastAPI's StaticFiles mount.

In production you should swap this out for uploading to S3 / GCS / Azure Blob
and returning that URL instead.
"""
from __future__ import annotations

import uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Persist image bytes to the local upload directory.

    Returns the filename (not the full URL — the caller appends the base URL).
    """
    ext = mime_type.split("/")[-1].replace("jpeg", "jpg")
    filename = f"{uuid.uuid4().hex}.{ext}"
    (UPLOAD_DIR / filename).write_bytes(image_bytes)
    return filename
