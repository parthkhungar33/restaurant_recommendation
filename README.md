# Restaurant Recommender

Phase 0 foundation for an AI-powered restaurant recommendation backend.

## Quickstart

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy env file:
   - `copy .env.example .env` (Windows)
   - set `GROQ_API_KEY` in `.env` for LLM ranking
4. Run API:
   - `uvicorn src.phase_2_retrieval.main:app --reload` (listens on `http://127.0.0.1:8000` by default)
5. Run **Culinary Curator** UI (Node.js / Vite):
   - `cd web`
   - `npm install` (first time)
   - `npm run dev` → open `http://localhost:5173`
   - Vite proxies API routes to port 8000; set `VITE_API_PROXY_TARGET` in `web/.env.development` if needed (see `web/.env.example`).
   - If cities do not load, start `uvicorn` first. The SPA probes `8000` / `8010` in dev to find a live API when `VITE_API_BASE` is unset.
   - Mockups in `design/` are copied into `web/public/design/` automatically before `dev` / `build` (`npm run sync-design` runs manually).
6. Run checks:
   - `python -m ruff check .`
   - `python -m pytest`

## Phase 1 Ingestion

Run data ingestion from Hugging Face and persist canonical data:

- `python scripts/ingest_restaurants.py`
- To dedupe an existing SQLite file in-place (same rules as ingestion, key = `name + location_city + locality`): `python scripts/dedupe_restaurants_db.py`

Artifacts generated:
- SQLite DB: `src/phase_1_ingestion/data/restaurants.db` with table `restaurants_clean`
- Data quality report: `src/phase_1_ingestion/data/quality_report.json`

## Phase 3 LLM Ranking

- `POST /recommendations` runs deterministic retrieval + Groq LLM ranking/explanations.
- `GET /metadata/locations` returns available cities for UI helper dropdowns.
- Basic web UI (HTML/CSS/JS) is served at `/` for quick validation **without Node**.
- Production build of the Vite app: `cd web && npm run build` → static files in `web/dist`.

## Deployment (Vercel + Streamlit / unified Docker)

- **Vercel (frontend):** In the Vercel project, set the **root directory** to `web/`. Add build env **`VITE_API_BASE`** with the public URL of your Python backend (no trailing slash). Current value: `https://restaurantrecommendation-parth3.streamlit.app`. `web/vercel.json` configures SPA fallback routing for the Vite build.
- **Streamlit Community Cloud:** Deploy `streamlit_app.py` from this repo. Add secrets (`GROQ_API_KEY`, optional `DB_PATH`) in the Streamlit dashboard. Commit or otherwise provide `restaurants.db` (or run ingestion in CI before deploy). **Note:** Streamlit Cloud only exposes the Streamlit process; it does **not** publish a separate public port for the FastAPI API, so the Vercel SPA still needs a host that serves `/health`, `/metadata/*`, and `POST /recommendations`.
- **Recommended backend URL for the Vite client:** Build and run the **`Dockerfile`** on Fly.io, Railway, Render, or similar. It runs **nginx** on port **8080**: JSON routes go to **FastAPI**, everything else to **Streamlit**. Set **`CORS_ORIGIN_REGEX=`** `https://.*\.vercel\.app` (or list your production domain in **`CORS_EXTRA_ORIGINS`**) on the container so the browser can call the API from Vercel. Pass **`GROQ_API_KEY`** at runtime.

## Phase 5 Evaluation

- Run evaluation report:
  - `python scripts/run_phase5_evaluation.py`
- Optional smaller run:
  - `python scripts/run_phase5_evaluation.py --max-queries 10`
- Output file:
  - `src/phase_5_evaluation/results/phase5_eval_report.json`
