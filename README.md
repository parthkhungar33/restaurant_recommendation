# Restaurant Recommender

AI-assisted restaurant discovery: users filter by city, budget, cuisine, rating, and mood-style preferences. The system combines **deterministic SQLite retrieval** (trustworthy, grounded candidates) with **Groq LLM re-ranking and short explanations** for the final shortlist.

## Latest progress

- Improved responsive behavior for the Vite SPA (`web/`) so mobile and desktop share the same core UX flow.
- Removed non-functional UI elements (profile button, fake discover strip, mobile bottom nav) to keep the experience clean and consistent.
- Removed the voice/mic affordance from preferences and simplified the input UI.
- Tightened mobile spacing, typography, card layouts, and grid behavior; added `overflow-x-hidden` to reduce narrow-screen overflow.
- Build verified after the UI updates: `cd web && npm run build`.

## Tech stack

| Area | Stack |
| ---- | ----- |
| **API** | Python 3.11+, **FastAPI**, Pydantic, Uvicorn |
| **Data** | **SQLite** (`restaurants_clean`), **Pandas**, Hugging Face **`datasets`** |
| **LLM** | **Groq** (OpenAI-compatible chat completions), `httpx`; validation, retry, deterministic fallback |
| **Primary UI** | **Vite 6** + vanilla JS/CSS — **Culinary Curator** SPA in `web/` |
| **Alt UI** | Static HTML/JS served by FastAPI at `/` and `/ui/*`; optional **`streamlit_app.py`** |
| **CI** | **GitHub Actions** — Ruff + pytest (see `.github/workflows/ci.yml`) |
| **Deploy** | **Vercel** (frontend), **Render** (FastAPI via `render.yaml`); optional **Dockerfile** (nginx + API + Streamlit) |

## Dataset (Hugging Face)

- **Dataset:** [`ManikaSaini/zomato-restaurant-recommendation`](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- **Ingestion:** `python scripts/ingest_restaurants.py` → canonical table `restaurants_clean` and `quality_report.json` under `src/phase_1_ingestion/data/`.

## LLM integration

- **Endpoint:** `POST /recommendations` — retrieval expands the candidate pool, then the LLM ranks and adds `ai_explanation` per card.
- **Config:** set `GROQ_API_KEY` in `.env` (local) or in your host’s environment (Render, etc.). See `.env.example`.
- **Reliability:** JSON-shaped outputs are validated; invalid responses trigger a stricter retry, then a deterministic ordering + template-style fallback.

## Deployment

**Production pattern:** static SPA on **Vercel** + JSON API on **Render** (recommended).

1. **Render:** New **Blueprint** from this repo → uses root **`render.yaml`**. Set secret **`GROQ_API_KEY`**. Verify JSON at `https://<render-service>/health` and `/metadata/locations`.
2. **Vercel:** Project **root directory** = `web/`. Set **`VITE_API_BASE=https://<render-service>`** (no trailing slash). **Redeploy** after env changes so the build picks up the API URL.
3. **CORS:** FastAPI reads **`CORS_EXTRA_ORIGINS`** and **`CORS_ORIGIN_REGEX`** (e.g. `https://.*\.vercel\.app` for previews). Defaults for Render are seeded in `render.yaml`.

**Important:** The Vercel app must call a **FastAPI** base URL. A **Streamlit Cloud** URL alone serves HTML, not `/metadata/locations` JSON — use Streamlit for an optional separate UI, not as `VITE_API_BASE`.

**Optional:** Run the repo **`Dockerfile`** on Fly/Railway/Render with **`GROQ_API_KEY`** and CORS env vars — nginx routes API paths to uvicorn and `/` to Streamlit.

More detail: `docs/project_handoff.md`, `docs/architecture.md`.

## Quickstart (local)

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy env file:
   - `copy .env.example .env` (Windows) / `cp .env.example .env` (Unix)
   - set `GROQ_API_KEY` in `.env` for LLM ranking
4. Run API:
   - `uvicorn src.phase_2_retrieval.main:app --reload` (default `http://127.0.0.1:8000`)
5. Run **Culinary Curator** UI (Vite):
   - `cd web`
   - `npm install` (first time)
   - `npm run dev` → `http://localhost:5173`
   - Vite proxies `/recommendations`, `/metadata`, `/health` to port 8000; override with `VITE_API_PROXY_TARGET` (see `web/.env.example`).
   - If cities do not load, start `uvicorn` first. With `VITE_API_BASE` unset in dev, the SPA probes common local API ports.
   - Mockups in `design/` copy to `web/public/design/` on `predev` / `prebuild`.
6. Run checks:
   - `python -m ruff check .`
   - `python -m pytest`

## Phase 1 Ingestion

- `python scripts/ingest_restaurants.py`
- Dedupe in place: `python scripts/dedupe_restaurants_db.py`

Artifacts:
- SQLite: `src/phase_1_ingestion/data/restaurants.db` (`restaurants_clean`)
- Quality report: `src/phase_1_ingestion/data/quality_report.json`

## Phase 3 LLM ranking (API)

- `POST /recommendations` — deterministic retrieval + Groq ranking/explanations.
- `GET /metadata/locations` — cities + helper chips for the UI.
- FastAPI also serves a minimal HTML UI at `/` (no Node required).
- Production Vite build: `cd web && npm run build` → `web/dist`.

## Phase 5 Evaluation

- `python scripts/run_phase5_evaluation.py`
- Smaller run: `python scripts/run_phase5_evaluation.py --max-queries 10`
- Output: `src/phase_5_evaluation/results/phase5_eval_report.json`
