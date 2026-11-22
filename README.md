# WhatsApp → Instagram Bridge

> **IBM BOB | CleanBengaluru** — Solving Bengaluru's waste & scrap management problem.

Receives a photo and a location shared via **WhatsApp Business Cloud API**, reverse-geocodes the location to a human-readable address, and publishes the photo with a caption to an **Instagram Business account** using the Instagram Graph API.

---

## Architecture

```
WhatsApp User
    │  sends photo + location
    ▼
WhatsApp Business Cloud API
    │  POST /webhook
    ▼
FastAPI Server  (this repo)
    ├─ download image bytes
    ├─ reverse-geocode lat/lon  →  Nominatim (OSM)
    ├─ build caption (address + hashtags)
    └─ publish photo  →  Instagram Graph API
                              │
                              ▼
                        Instagram Business Page
```

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.11+ | |
| WhatsApp Business Cloud API access | Via [Meta for Developers](https://developers.facebook.com/docs/whatsapp/cloud-api) |
| Instagram Business or Creator account | Linked to a Facebook Page |
| Instagram Graph API access token | With `instagram_basic` + `instagram_content_publish` scopes |
| Public HTTPS URL | Use [ngrok](https://ngrok.com) locally; your server URL in production |

---

## Setup

### 1. Clone & install

```bash
git clone <this-repo>
cd ibmbob-chainsaw-saafsaath
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

> `pydantic-settings` is pulled in as a transitive dependency of FastAPI.  
> If it isn't, add it manually: `pip install pydantic-settings`.

### 2. Configure environment

```bash
cp .env.example .env
# edit .env and fill in every value
```

| Variable | Description |
|---|---|
| `WHATSAPP_VERIFY_TOKEN` | A secret string you choose; paste the same value in Meta's webhook settings |
| `WHATSAPP_API_TOKEN` | Permanent or temporary access token from your Meta App |
| `WHATSAPP_PHONE_NUMBER_ID` | Phone Number ID from the WhatsApp Cloud API dashboard |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived access token with content-publish scope |
| `INSTAGRAM_ACCOUNT_ID` | Your Instagram Business account ID (numeric) |
| `BASE_URL` | Public HTTPS URL of this server (e.g. `https://abc.ngrok.io`) |
| `INSTAGRAM_HASHTAGS` | Space-separated hashtags appended to every post |
| `NOMINATIM_USER_AGENT` | Descriptive name for the Nominatim reverse-geocoding requests |

### 3. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

For local development, expose port 8000 publicly:

```bash
ngrok http 8000
# copy the https://... URL into BASE_URL in .env
```

### 4. Register the WhatsApp webhook

1. Go to **Meta for Developers → Your App → WhatsApp → Configuration**.
2. Set the **Callback URL** to `https://<your-domain>/webhook`.
3. Set the **Verify Token** to the same value as `WHATSAPP_VERIFY_TOKEN` in `.env`.
4. Subscribe to the **messages** field.

---

## Message flow

The bridge handles **two separate WhatsApp messages** from the same sender:

1. **Photo message** – the user sends an image (taken with the camera or picked from gallery).  
   The server downloads the image and stores it in memory, keyed by the sender's phone number.

2. **Location message** – the user sends their current location using WhatsApp's native location share.  
   The server resolves the GPS coordinates to a street address using OpenStreetMap Nominatim.

When both messages have been received from the same sender, the server:
- Saves the image to the `uploads/` directory (served publicly at `/uploads/<filename>`).
- Builds the caption: `📍 <address>\n\n<hashtags>`.
- Posts to Instagram via the two-step container-create → publish Graph API flow.
- Clears the sender's session.

> **Order doesn't matter** — photo first or location first, both work.

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/webhook` | WhatsApp webhook verification challenge |
| `POST` | `/webhook` | Receive WhatsApp message events |
| `GET` | `/uploads/{filename}` | Serve uploaded images (StaticFiles) |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

---

## Project structure

```
app/
├── __init__.py      re-exports app for uvicorn
├── main.py          FastAPI app, webhook handlers, session logic
├── config.py        Pydantic Settings (loads .env)
├── whatsapp.py      WhatsApp Cloud API — parse messages, download media
├── geocoding.py     Nominatim reverse geocoding
├── instagram.py     Instagram Graph API — publish photos
└── storage.py       Save image bytes, serve as static files
uploads/             Auto-created; holds temporary image files
requirements.txt
.env.example
```

---

## Production notes

- **Replace in-memory sessions** with Redis or a database to survive restarts.
- **Replace `uploads/` static hosting** with S3 / GCS / Azure Blob Storage.  
  Update `storage.py` to upload bytes and return the cloud URL directly.
- **Rotate access tokens** — Instagram long-lived tokens expire every 60 days;  
  implement a token-refresh cron job.
- **Secure the webhook** — validate the `X-Hub-Signature-256` header on every POST  
  to prevent spoofed requests (add to `app/whatsapp.py`).
