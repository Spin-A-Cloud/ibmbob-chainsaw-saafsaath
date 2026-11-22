from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers import auth

app = FastAPI(title="SaafSaath API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # only needed during Vite dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ── Static frontend serving ───────────────────────────────────────────────────
# The React build outputs to backend/static/ (configured in vite.config.ts).
# All /assets/* files are served directly; every other non-API path falls back
# to index.html so that React Router can handle client-side navigation.

STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.is_dir():
    # Serve hashed JS/CSS/image assets
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:
        """Return index.html for any path that isn't an API route."""
        return FileResponse(STATIC_DIR / "index.html")
