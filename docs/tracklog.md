# Track Log

This file is a running implementation log for the project.  
Format per step:
- **Did**: what was implemented
- **Failed/Issue**: what broke or did not meet expectation
- **Success**: what worked
- **Improvement**: what was changed to improve reliability/quality

---

## Step 1 - Architecture plan creation

- **Did**
  - Read `docs/problemstatement.md`.
  - Created `docs/architecture.md` with a phase-wise implementation plan from Phase 0 to Phase 6.
  - Included objective, deliverables, exit criteria, risks, and timeline.
- **Failed/Issue**
  - No blocking issue.
- **Success**
  - Architecture blueprint was finalized and used as execution reference.
- **Improvement**
  - Plan was structured to allow iterative implementation (phase by phase) rather than one-shot build.

---

## Step 2 - Phase 0 scaffold (foundation)

- **Did**
  - Created baseline backend/project scaffolding:
    - `app/` modules (`api`, `core`, `models`, `services`, `data`, `prompts`)
    - `tests/`
    - base docs and tooling files.
  - Added environment/config setup:
    - `.env.example`
    - `app/core/config.py` with typed settings.
  - Added FastAPI app bootstrap:
    - `app/main.py`
    - health route `GET /health` in `app/api/health.py`.
  - Added typed response model:
    - `app/models/health.py`.
  - Added LLM provider interface placeholder:
    - `app/services/llm.py`.
  - Added tooling/config:
    - `requirements.txt`
    - `ruff.toml`
    - `pytest.ini`
    - CI workflow `.github/workflows/ci.yml`
    - updated `README.md`.
- **Failed/Issue**
  - PowerShell rejected command chaining with `&&`.
  - `ruff` and `pytest` commands were not found directly on PATH.
  - Minor lint issue: import ordering in `app/main.py`.
- **Success**
  - Local checks passed after command and lint fixes.
  - Health endpoint test passed.
- **Improvement**
  - Switched command style to PowerShell-compatible `;`.
  - Standardized checks to:
    - `python -m ruff check .`
    - `python -m pytest`
  - Applied lint auto-fix to enforce import organization and keep CI stable.

---

## Step 3 - Phase 1 initial ingestion implementation

- **Did**
  - Added data ingestion pipeline in `app/data/ingestion.py`:
    - dataset fetch from Hugging Face (`ManikaSaini/zomato-restaurant-recommendation`)
    - schema alias mapping
    - normalization and cleaning helpers
    - cuisine parsing + service tags derivation
    - budget bucketing (`low/medium/high/unknown`)
    - quality report generation.
  - Added persistence to SQLite:
    - output table `restaurants_clean`
    - indexes on city, rating, budget, cuisines text.
  - Added runnable script:
    - `scripts/ingest_restaurants.py`
  - Added tests:
    - `tests/test_ingestion.py`
  - Added dependencies:
    - `pandas`
    - `datasets`
  - Updated `README.md` with ingestion command and artifacts.
- **Failed/Issue**
  - Column alias detection initially failed for names with spaces/special chars (example: `Restaurant Name`).
  - Ruff/Python compatibility mismatch:
    - rule suggested `datetime.UTC` (Py3.11 style) while runtime is Py3.10.
  - Script import path issue: `ModuleNotFoundError: No module named 'app'`.
  - Initial source-to-canonical mapping used wrong city-like field, causing weak city filtering behavior later.
- **Success**
  - End-to-end ingestion script executed and generated:
    - `app/data/restaurants.db`
    - `app/data/quality_report.json`
  - Tests passed for normalization and report logic.
- **Improvement**
  - Implemented resilient column matching by normalizing column keys (remove non-alphanumeric chars).
  - Set lint target to Python 3.10 in `ruff.toml` to align tooling with runtime.
  - Fixed script module resolution by adding project root to `sys.path`.
  - Improved formatting and line-length compliance for stable lint.

---

## Step 4 - Phase 1 data-mapping correction

- **Did**
  - Investigated actual dataset schema via quick inspection command.
  - Updated mapping to handle dataset-specific columns:
    - `rate` for rating
    - `approx_cost(for two people)` for cost
    - `listed_in(city)` and URL extraction for city.
  - Added city extraction from Zomato URL path for accurate `location_city`.
- **Failed/Issue**
  - Initial canonical city mapping produced locality-like values, reducing query relevance for user city inputs (e.g., `Bangalore`).
- **Success**
  - Re-ingestion produced meaningful city-aligned canonical data.
  - Quality report stabilized with realistic null and distribution stats.
- **Improvement**
  - Added URL-based city derivation fallback chain:
    - URL city first, then configured city column fallback.
  - Re-ran ingestion to regenerate DB with corrected city field.

---

## Step 5 - Phase 2 deterministic retrieval API

- **Did**
  - Added Phase 2 typed contracts in `app/models/recommendation.py`:
    - request validation (location, budget, cuisine, min_rating, limit)
    - response schema with applied filters, recommendations, notes.
  - Added retrieval engine in `app/services/retrieval.py`:
    - required location filter
    - optional budget/cuisine/min_rating filters
    - deterministic SQL retrieval from `restaurants_clean`
    - sorted by rating/votes/cost.
  - Implemented fallback relaxation sequence if candidates are too few:
    1. relax `min_rating`
    2. relax `cuisine`
    3. relax `budget`
  - Added reason tags + notes for transparency.
  - Added API route:
    - `POST /recommendations/query` in `app/api/recommendations.py`
  - Registered router in `app/main.py`.
  - Added DB path setting in `app/core/config.py`.
  - Added API tests in `tests/test_recommendations_api.py`.
- **Failed/Issue**
  - First verification call returned 0 candidates for expected city query due to earlier city mapping issue (not retrieval logic itself).
  - Minor lint line-length violations in retrieval module.
- **Success**
  - After city-mapping correction and re-ingestion:
    - endpoint returned status 200
    - candidate pool populated
    - top-N recommendations returned correctly.
  - Full test and lint suite passed.
- **Improvement**
  - Tightened request normalization/validation (non-empty normalized location).
  - Kept fallback path explicit and inspectable via `relaxed_constraints`.
  - Ensured behavior remains deterministic and testable before LLM phase.

---

## Current Status Snapshot

- **Completed**
  - Phase 0: foundation/project setup
  - Phase 1: ingestion + canonical store + quality reporting
  - Phase 2: deterministic query API with fallback relaxation
- **Verified**
  - Lint passes (`python -m ruff check .`)
  - Tests pass (`python -m pytest`)
  - Ingestion command works and artifacts exist
  - `POST /recommendations/query` works on ingested DB
- **Next Recommended**
  - Phase 3: LLM ranking + explanation layer on top of Phase 2 candidate set.

---

## Logging Rule for Future Steps

For every new implementation step, append one section with:
1. **Did**
2. **Failed/Issue**
3. **Success**
4. **Improvement**

Keep entries concise, factual, and diff-oriented so regressions and fixes remain auditable.

---

## Step 6 - Phase-wise `src` reorganization

- **Did**
  - Created `src/` as a phase-oriented inspection layer.
  - Added:
    - `src/phase_0_foundation/`
    - `src/phase_1_ingestion/`
    - `src/phase_2_retrieval/`
  - Added phase files that map to implemented modules using thin references, so each phase has a clear file group without changing runtime behavior.
  - Added `src/README.md` to document phase layout.
- **Failed/Issue**
  - No functional/runtime issue encountered.
- **Success**
  - Phase artifacts are now grouped under `src` for easier review and audit.
  - Existing application imports and tests remain unaffected.
- **Improvement**
  - Used reference modules instead of moving core runtime files, avoiding accidental breakage while still achieving phase-wise organization.

---

## Step 7 - Hard move to phase-owned runtime code

- **Did**
  - Replaced `src/phase_*` reference modules with full runtime implementations:
    - Phase 0: config, health API/model, LLM interface
    - Phase 1: ingestion pipeline/model/script
    - Phase 2: recommendation models, retrieval service, recommendations API, app entrypoint
  - Created `src/phase_2_retrieval/main.py` as the new FastAPI app root.
  - Updated tests to import from `src.phase_2_retrieval.main` and `src.phase_1_ingestion.data_ingestion`.
  - Updated `scripts/ingest_restaurants.py` to delegate to `src.phase_1_ingestion.script_ingest_restaurants`.
  - Updated defaults and docs:
    - `.env.example` now includes `DB_PATH=src/phase_1_ingestion/data/restaurants.db`
    - `README.md` now points to `uvicorn src.phase_2_retrieval.main:app --reload`
    - ingestion artifact paths moved to `src/phase_1_ingestion/data/`.
  - Deleted old `app/` implementation files to avoid duplicate source of truth.
- **Failed/Issue**
  - Primary risk was import/runtime breakage during path migration.
- **Success**
  - Re-ingestion completed at new location and generated:
    - `src/phase_1_ingestion/data/restaurants.db`
    - `src/phase_1_ingestion/data/quality_report.json`
  - Lint and tests passed after migration.
- **Improvement**
  - Established phase folders as the canonical runtime ownership model, making future debugging and phase-level inspection significantly easier.

---

## Step 8 - Phase 3 LLM ranking implementation

- **Did**
  - Added Phase 3 module `src/phase_3_llm/` with:
    - `api_llm_recommendations.py`
    - `service_llm_recommender.py`
    - `model_llm_recommendation.py`
    - `prompts/system_v1.txt`
  - Implemented Groq client integration in service layer using `httpx`.
  - Added strict JSON output parsing and validation via Pydantic models.
  - Added one-retry correction path for invalid LLM output.
  - Added deterministic fallback explanations when LLM output remains invalid.
  - Added `POST /recommendations` endpoint for deterministic retrieval + LLM ranking.
  - Registered Phase 3 router in `src/phase_2_retrieval/main.py`.
  - Added settings and env support for Groq:
    - `groq_api_key`, `groq_model`, `groq_base_url` in config
    - `.env.example` updated with `GROQ_API_KEY` and `GROQ_MODEL`.
  - Added tests for LLM ranking service with mocked client behavior.
- **Failed/Issue**
  - Initial Phase 3 files failed lint on import ordering, line lengths, and extraneous f-strings.
- **Success**
  - Lint and test suite both pass after fixes.
  - Phase 3 behavior now includes:
    - schema-validated LLM ranking
    - retry on malformed output
    - fallback path to keep endpoint reliable
- **Improvement**
  - Introduced prompt template versioning in `src/phase_3_llm/prompts/` for controlled iteration.
  - Kept LLM calls behind a dedicated client abstraction to simplify future provider/model changes.

---

## Step 9 - Remove manual model selection from env

- **Did**
  - Removed `groq_model` from settings so model is no longer configured via `.env`.
  - Updated Groq client to use internal default/fallback model chain automatically.
  - Updated API wiring and live test setup to stop passing model from config.
  - Removed `GROQ_MODEL` from `.env.example`.
- **Failed/Issue**
  - No blocking issue.
- **Success**
  - Lint and LLM tests (including live integration) passed after the change.
- **Improvement**
  - Simplified configuration: only API key is required from `.env`, reducing setup errors and model-deprecation friction.

---

## Step 10 - Live LLM connectivity and dummy-flow validation

- **Did**
  - Added live integration tests:
    - `tests/test_llm_live_integration.py`
    - direct Groq connectivity test
    - end-to-end `/recommendations` flow test
  - Added safe env diagnostics test:
    - `tests/test_env_diagnostics.py`
    - validates key presence without exposing secret value
  - Added runnable dummy request script:
    - `scripts/run_dummy_llm_request.py`
  - Executed live endpoint with dummy payload (`Bangalore`, `medium`, `Italian`, `min_rating=4.0`, `limit=3`).
- **Failed/Issue**
  - Initial live tests failed with `400 Bad Request` from Groq.
  - Root cause: configured model was decommissioned (`model_decommissioned`).
  - Encountered PowerShell quoting issues while running inline Python one-liners.
  - Dummy script initially failed with `ModuleNotFoundError: No module named 'src'`.
- **Success**
  - Implemented model fallback handling in Groq client and updated defaults.
  - Live integration tests passed after fix.
  - Dummy end-to-end run succeeded:
    - status `200`
    - `total_candidates=80`
    - `recommendations_count=3`
    - returned ranked restaurant recommendations with valid IDs.
- **Improvement**
  - Added robust model fallback to reduce outages from provider deprecations.
  - Added reusable diagnostics and dummy-run tooling for quick future verification.
  - Added script path bootstrap (`sys.path`) to keep local script execution reliable.

---

## Step 11 - Phase 4 API and UX implementation

- **Did**
  - Added new phase module `src/phase_4_api_ux/` with:
    - `model_api_ux.py`
    - `service_api_ux.py`
    - `api_api_ux.py`
  - Implemented user-facing `POST /recommendations` contract with:
    - `request_id`
    - `applied_filters`
    - recommendation cards containing `restaurant_name`, `cuisine`, `rating`, `estimated_cost`, `ai_explanation`, `fit_score`
    - `notes`
  - Implemented `GET /metadata/locations` endpoint for UI helper dropdowns.
  - Wired Phase 4 router into app entrypoint so Phase 4 is primary UX API layer.
  - Added tests in `tests/test_phase4_api_ux.py`:
    - metadata endpoint shape check
    - mocked LLM route validating stable response schema
  - Updated `README.md` and `src/README.md` for Phase 4 endpoint/module visibility.
- **Failed/Issue**
  - One lint issue in `scripts/run_dummy_llm_request.py` (`E402` import placement).
- **Success**
  - Full lint and test suite passed after fix.
  - Phase 4 endpoints now present and validated.
- **Improvement**
  - Added explicit API response shaping layer to decouple UI contract from lower-level retrieval/LLM internals.
  - Added metadata endpoint to support better front-end UX and reduce hardcoded location values.

---

## Step 12 - Phase 5 quality and evaluation implementation

- **Did**
  - Added `src/phase_5_evaluation/` module with:
    - representative query set (`data/eval_queries.json`, 30 queries)
    - evaluation service (`service_evaluation.py`)
    - output artifact directory (`results/`)
  - Implemented automated evaluation pipeline that:
    - runs queries through `POST /recommendations`
    - computes success/empty/fallback rates
    - computes latency p50/p95/mean
    - computes heuristic top-1 relevance and explanation quality scores
    - compares deterministic vs LLM route overlap
    - writes report to `src/phase_5_evaluation/results/phase5_eval_report.json`
  - Added runner script:
    - `scripts/run_phase5_evaluation.py`
    - supports `--max-queries` for smaller validation runs
  - Added tests:
    - `tests/test_phase5_evaluation.py`
    - validates percentile and scoring helpers
  - Updated docs:
    - `README.md` with phase-5 command usage
    - `src/README.md` with phase-5 module description
- **Failed/Issue**
  - Initial lint violations (line length and import placement in new script/service).
  - `ModuleNotFoundError: src` in evaluation runner before path bootstrap adjustment.
- **Success**
  - Full lint and test suite passed after fixes.
  - Sample evaluation run (`--max-queries 5`) executed and generated report successfully.
- **Improvement**
  - Added practical, repeatable baseline metrics for relevance, explanation quality, reliability, and performance.
  - Added lightweight query limiting to keep evaluation fast and cost-controlled during iteration.

---

## Step 13 - Basic frontend validation UI (HTML/CSS/JS)

- **Did**
  - Added a basic frontend using plain web stack:
    - `src/phase_4_api_ux/frontend/index.html`
    - `src/phase_4_api_ux/frontend/styles.css`
    - `src/phase_4_api_ux/frontend/app.js`
  - Frontend supports:
    - location loading via `GET /metadata/locations`
    - preference form submission to `POST /recommendations`
    - recommendation cards (`name`, `cuisine`, `rating`, `estimated_cost`, `fit_score`, `ai_explanation`)
    - request id display, notes display, and error state handling
  - Wired frontend into FastAPI:
    - mounted static assets at `/ui`
    - root route `/` now serves `index.html`
  - Updated `README.md` to mention UI availability at `/`.
- **Failed/Issue**
  - No blocking issue.
- **Success**
  - Lint and test suite passed after integration.
  - Runtime verification succeeded:
    - `/` returns HTML (`200`)
    - `/metadata/locations` returns location list (`200`)
- **Improvement**
  - Established a minimal browser-based validation surface to test end-to-end flow quickly before building a richer frontend.

---

## Step 14 - Phase A implementation (max budget + rating cap)

- **Did**
  - Replaced budget-band input with numeric `max_budget` in core query model:
    - `src/phase_2_retrieval/model_recommendation.py`
  - Updated retrieval filtering from `budget_band` matching to numeric filter:
    - `avg_cost_for_two <= max_budget`
    - applied-filter and relaxed-constraint tracking now uses `max_budget`
  - Updated Phase 3 prompt payload to send `max_budget` in user preferences.
  - Updated frontend form:
    - removed Low/Medium/High dropdown
    - added numeric "Max Budget (for two)" input
    - payload now sends `max_budget`
  - Updated tests and dummy scripts to use `max_budget` instead of `budget`.
  - Updated Phase 5 scoring helper to support both legacy `budget` and new `max_budget` for compatibility.
- **Failed/Issue**
  - Minor lint issue surfaced after model update (import ordering), auto-fixed.
- **Success**
  - Full lint and test suite passed after the migration.
  - Rating cap remained enforced via schema (`min_rating <= 5.0`), so no additional fix was required.
- **Improvement**
  - Input model now better matches real user intent (numeric max spend).
  - Reduced ambiguity from budget bands and improved filter precision.

---

## Step 15 - Phase B implementation (controlled additional preferences)

- **Did**
  - Converted `additional_preferences` from free-text to normalized list in request model:
    - accepts string or list input
    - lowercases, trims, deduplicates values
  - Added controlled preference mapping in LLM layer:
    - `date` -> `romantic`, `ambience`, `quiet`
    - `group friendly` -> `group-friendly`, `large-seating`
    - and similar mappings for other predefined options
  - Updated prompt context to include:
    - raw selected preferences
    - normalized `preference_tags` for consistent LLM interpretation
  - Updated frontend input from text field to **multi-select dropdown** with fixed options:
    - date, family-friendly, quick service, casual, fine dine, outdoor seating, veg friendly, group friendly
  - Updated frontend payload to send selected preferences as an array.
  - Added tests:
    - `tests/test_phaseb_preferences.py`
    - covers normalization/dedup and prompt tag presence.
- **Failed/Issue**
  - No blocking issues.
- **Success**
  - Lint and full test suite passed after Phase B changes.
- **Improvement**
  - Preference input is now constrained and predictable.
  - LLM receives more structured preference signals, reducing noisy interpretation from open text input.

---

## Step 16 - Phase C implementation (dedup + friendly explanations + fit score removal)

- **Did**
  - Added retrieval-layer deduplication in Phase 2:
    - unique by `restaurant_id`
    - additional signature dedup on `(name + locality + cuisines)` to catch repeated same-restaurant rows
  - Strengthened LLM-layer deduplication:
    - dedup by `restaurant_id`
    - secondary dedup by normalized `restaurant_name`
  - Added final response-layer deduplication in Phase 4:
    - dedup before returning cards to frontend
    - guards against duplicate IDs/signatures even if upstream repeats occur
  - Updated prompt instructions and fallback explanation style to be more user-friendly and less robotic.
  - Removed `fit_score` from Phase 4 response model and frontend cards.
  - Added/updated tests to ensure duplicate LLM results collapse to unique cards and UI payload no longer contains `fit_score`.
- **Failed/Issue**
  - No blocking issue.
- **Success**
  - Lint and full test suite passed after Phase C changes.
  - Duplicate handling now exists at three layers (retrieval, LLM parse, final formatter), significantly reducing repeated-card issues.
- **Improvement**
  - Output quality and UX are improved:
    - friendlier explanations
    - cleaner non-repetitive recommendation cards
    - less confusing presentation for users.

---

## Step 17 - Phase D regression coverage and quality gate

- **Did**
  - Added dedicated regression test suite:
    - `tests/test_phase_d_regression_gate.py`
  - Covered required Phase D checks:
    - numeric `max_budget` behavior
    - API validation for `min_rating > 5` rejection
    - retrieval dedup behavior including same-name different-locality handling
  - Extended LLM regression coverage:
    - `tests/test_llm_recommender.py` now verifies duplicate IDs in LLM output are deduped
  - Tightened response contract test:
    - `tests/test_phase4_api_ux.py` now asserts exact result keys and confirms `fit_score` is absent
  - Existing Phase B mapping integration tests remain active:
    - `tests/test_phaseb_preferences.py` validates normalized preference tags in prompt.
- **Failed/Issue**
  - Initial test case for `max_budget` failed because fallback relaxation can intentionally remove budget constraint when result count is low.
  - Minor lint line-length issues in new regression test file.
- **Success**
  - Adjusted budget test to isolate strict budget behavior without fallback-trigger conditions.
  - Resolved lint issues and all tests now pass.
- **Improvement**
  - Added a reliable quality gate that protects key UX fixes (no duplicate cards, strict response contract, bounded validation) from regression.

---

## Step 18 - Culinary Curator SPA (`web/`) from `design/` mockups + docs alignment

- **Did**
  - Added **Node.js (Vite 6)** frontend at repo root `web/`:
    - Vanilla ES modules (`web/src/main.js`) + `web/src/styles.css` (Plus Jakarta Sans, coral/red/peach/purple tokens aligned to `design/screen*.png`).
    - Shell: top nav, left filter rail (city pill, locality select, max-price slider, cuisine chips, rating pills, dining checkboxes, CTA + reset).
    - Views: hero (mockup image), skeleton loading state, results grid (featured first card, smart-match badge heuristic, sort, filter chip bar, AI banner when notes/relaxed constraints exist, map CTA placeholder).
    - wired to existing API: `POST /recommendations`, `GET /metadata/locations`.
  - **Vite proxy** (`vite.config.js`): forwards `/recommendations`, `/metadata`, `/health` to `127.0.0.1:8000` (override via `VITE_API_PROXY_TARGET`).
  - **Design sync**: `web/scripts/sync-design.mjs` + `predev`/`prebuild` copy `design/*.png` → `web/public/design/`; `web/public/design/*.png` gitignored to avoid duplicate binaries.
  - **FastAPI CORS** in `src/phase_2_retrieval/main.py` for `localhost`/`127.0.0.1` ports **5173** and **4173**.
  - Updated **`docs/architecture.md`**: primary UI = Vite SPA, integration section (two-process dev, proxy, CORS), Phase 4 UI scope vs fallback `/` static UI; removed stale `fit_score` from example schema; refreshed immediate next actions.
  - Updated **`README.md`** and **`src/README.md`** with `web/` quickstart and production build note.
  - Verified `npm run build` and spot `pytest` on health + phase4 tests.
- **Failed/Issue**
  - None blocking; initial mockups live under `design/` only (glob tools can miss OneDrive paths; on-disk folder confirmed).
- **Success**
  - Build pipeline works end-to-end; mockups sync before dev/build; backend tests still pass for exercised modules.
- **Improvement**
  - **Dual UI strategy**: rich **Culinary Curator** experience for demos (`web/`) while FastAPI **static** UI at `/` remains for zero-Node smoke tests.
  - Single source of truth for PNG mockups in `design/` with automated copy into `web/public/design/`.
