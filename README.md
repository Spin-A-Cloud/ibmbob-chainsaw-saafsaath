# SaafSaath — Getting Started

## Prerequisites
- **Python 3.11+**
- **Node.js 20+** (with npm)

---

## Backend (FastAPI)

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### Demo credentials (seed data)
| Role | Email | Password |
|---|---|---|
| Customer | customer@example.com | customer123 |
| Company | company@example.com | company123 |

---

## Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

App will be available at `http://localhost:5173`.

The Vite dev server proxies `/api/*` requests to `http://localhost:8000`,
so both services must be running simultaneously.

---

## Project structure

```
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   ├── core/
│   │   └── security.py   # JWT helpers
│   ├── db/
│   │   └── store.py      # In-memory user store (replace with DB later)
│   ├── models/
│   │   └── schemas.py    # Pydantic request/response schemas
│   └── routers/
│       └── auth.py       # /api/login  /api/register
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── api/           # fetch wrappers
│       ├── components/    # ProtectedRoute
│       ├── context/       # AuthContext
│       ├── pages/         # LoginPage, HomePage
│       └── types/         # TypeScript types
│
└── PROJECT.md             # Full product spec
```
