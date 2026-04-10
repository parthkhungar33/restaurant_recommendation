# Phase-Wise Architecture Implementation Plan

## 1) Goal and Scope

Build an AI-powered restaurant recommendation system (Zomato-inspired) that:
- accepts user preferences (`location`, `budget`, `cuisine`, `min_rating`, `additional_preferences`)
- ingests and prepares restaurant data from the Hugging Face dataset
- combines deterministic filtering with LLM-based ranking and explanation
- returns clear, user-friendly recommendations

This plan is structured for incremental implementation so each phase is testable and practical for MVP delivery.

### MVP Constraints (Current Scope)
- This is **not** a full-blown scale project in the current phase.
- Target load for LLM calls is intentionally low: **20-30 API calls per minute**.
- System design should optimize for clarity, correctness, and demo reliability over horizontal scale.
- **Deployment target (current):** **Vercel** hosts the Vite SPA (`web/`); set **`VITE_API_BASE`** to the public **FastAPI** origin. **Render** hosts FastAPI via `render.yaml` (Web Service: `uvicorn src.phase_2_retrieval.main:app`, health check `/health`). **Optional:** `streamlit_app.py` on Streamlit Community Cloud for a Streamlit-only UI; it does **not** replace the JSON API the Vercel app needs. **Optional:** repo **`Dockerfile`** (nginx + uvicorn + Streamlit) for a single URL that serves both API and Streamlit. Details: `docs/project_handoff.md` §2 “Deployment architecture”, root `render.yaml`, `README.md`.
- Primary UX is a **Node.js (Vite) SPA** in `web/` styled from mockups in `design/`, calling the FastAPI backend. A minimal HTML UI remains at `/` for quick smoke tests without Node.

---

## 2) Target Architecture (High Level)

### Core Components
1. **Data Ingestion Pipeline**
   - pulls source data from Hugging Face
   - validates schema and quality
   - normalizes fields (location, cuisine, cost range, ratings)
   - stores clean data for serving

2. **Preference Intake API/UI**
   - captures user input with validation
   - transforms user-friendly values into queryable filters

3. **Candidate Retrieval Layer**
   - applies deterministic filters on structured fields
   - returns top candidate set for LLM ranking

4. **LLM Recommendation Layer**
   - prompt builder + context packager
   - ranking + explanation generation
   - optional safety/consistency checks

5. **Response Formatter**
   - outputs final cards/list with required fields and rationale

6. **Observability and Feedback**
   - request logging, latency, token usage, failures
   - user feedback capture for quality improvement

### Suggested Runtime Stack
- **Backend**: Python + FastAPI
- **Data processing**: Pandas + Pydantic
- **Storage**: SQLite/PostgreSQL (start SQLite, migrate to PostgreSQL)
- **LLM integration**: Groq LLM via API-based chat/completions
- **Primary UI**: Node.js **Vite** dev server (`web/`) — vanilla ES modules + CSS aligned to `design/*.png` (Culinary Curator layout: left filter rail, hero / skeleton loading / results grid). `npm run dev` / `npm run build` runs `scripts/sync-design.mjs`, which copies mockups from `design/` into `web/public/design/` for the hero image (PNGs are gitignored under `web/` to avoid duplicating binaries).
- **Fallback UI**: static HTML/CSS/JS served by FastAPI at `/` and `/ui/*` for zero-install checks.

### Frontend / Backend Integration
- Local dev runs **two processes**: `uvicorn ... --reload` (default port 8000) and `npm run dev` in `web/` (port 5173).
- Vite proxies `/recommendations`, `/metadata`, and `/health` to the API origin (override with `VITE_API_PROXY_TARGET` if the API is not on `127.0.0.1:8000`).
- FastAPI enables **CORS** for local Vite origins (`localhost` / `127.0.0.1` on 5173 and 4173). For **production**, set **`CORS_EXTRA_ORIGINS`** (exact Vercel URL) and/or **`CORS_ORIGIN_REGEX`** (e.g. `https://.*\.vercel\.app`) on the API host so the browser can call Render from Vercel.
- **Production split:** Vercel build must define **`VITE_API_BASE`** = Render (or other) FastAPI URL with **no trailing slash**. After changing env vars, **redeploy** Vercel so Vite embeds the new base.
- Design artifacts live in `design/` at repo root; the web app syncs them into `web/public/design/` on each `dev`/`build` (see `README` quickstart).

---

## 3) Phase-Wise Implementation Plan

### Current Progress Status
- **Completed:** Phase 0, Phase 1, Phase 2, Phase 3, Phase 4
- **Remaining:** Phase 5, Phase 6
- **Current focus:** quality/evaluation hardening for MVP under low-load constraints

## Phase 0: Foundation and Project Setup
**Objective:** Establish repository structure, conventions, and local environment.

### Deliverables
- Standardized project structure:
  - `app/api`
  - `app/services`
  - `app/data`
  - `app/models`
  - `app/prompts`
  - `tests/`
  - `docs/`
- Environment and dependency setup (`requirements.txt` / `pyproject.toml`)
- Config management (`.env`, settings module)
- Basic CI checks (lint + unit test run)

### Key Decisions
- Use typed request/response contracts (Pydantic)
- Isolate LLM provider client behind an interface for easy swap
- Keep prompt templates versioned in `app/prompts`

### Exit Criteria
- App runs locally
- Health endpoint works
- CI passes for base skeleton

---

## Phase 1: Data Ingestion and Canonical Restaurant Store
**Objective:** Build a robust ingestion path from Hugging Face to clean, query-ready data.

### Inputs
- Source dataset: `ManikaSaini/zomato-restaurant-recommendation`

### Workstreams
1. **Dataset Connector**
   - fetch dataset snapshot
   - maintain ingestion timestamp/version

2. **Schema Normalization**
   - canonical fields:
     - `restaurant_id`
     - `name`
     - `location_city`
     - `locality`
     - `cuisines` (list)
     - `avg_cost_for_two`
     - `rating`
     - `votes` (if available)
     - `service_tags` (optional derived tags)

3. **Data Cleaning**
   - handle nulls and malformed ratings/cost
   - standardize city/locality strings
   - convert multi-cuisine text to tokenized list

4. **Budget Bucketing**
   - derive:
     - `low`, `medium`, `high` from cost thresholds
   - keep thresholds configurable by city if needed

5. **Persistence**
   - write clean table for retrieval (`restaurants_clean`)
   - create indexes for `location_city`, `rating`, `budget_band`, and cuisines field strategy

### Outputs
- Reproducible ingestion script
- Validated canonical dataset
- Data quality report (row counts, missing values, outliers)

### Exit Criteria
- Ingestion completes end-to-end reliably
- >=95% records meet required schema completeness
- Querying by city/cuisine/cost/rating is performant for MVP scale

---

## Phase 2: Preference Intake and Deterministic Candidate Retrieval
**Objective:** Implement reliable filtering before LLM involvement.

### API Contract (Example)
- `POST /recommendations/query`
  - input:
    - `location` (required)
    - `budget` (`low|medium|high`, optional)
    - `cuisine` (optional single or list)
    - `min_rating` (optional float)
    - `additional_preferences` (optional free text)
    - `limit` (default 5)

### Workstreams
1. **Validation Layer**
   - enforce valid ranges/types
   - normalize user text (case/spacing/synonyms)

2. **Filtering Service**
   - mandatory location filter
   - optional budget/cuisine/rating filters
   - scoring fallback when strict filter returns too few results:
     - relax one constraint at a time with explicit reason tags

3. **Candidate Set Builder**
   - output top N candidates (e.g., 20) for LLM ranking
   - include structured metadata used in prompts

### Outputs
- Deterministic retrieval service with unit tests
- Clear no-result and low-result behaviors

### Exit Criteria
- Stable filtered candidate retrieval
- Response time target met (e.g., <300 ms retrieval, local DB)
- Edge cases handled (invalid location, sparse data)

---

## Phase 3: LLM Ranking and Explanation Layer
**Objective:** Add personalization and human-like rationale generation.

### Prompt Architecture
1. **System Prompt**
   - role: recommendation expert
   - constraints: factual grounding only in provided candidates
   - output format: strict JSON schema

2. **User Context Block**
   - normalized user preferences
   - additional_preferences text

3. **Candidate Context Block**
   - compact table/list of candidate restaurants
   - include only necessary attributes

### LLM Responsibilities
- rank shortlisted candidates
- provide brief explanation for each recommendation
- mention trade-offs when constraints are partially relaxed

### Provider and Secrets
- Use **Groq LLM** as the primary provider for ranking and explanation.
- Store API key in `.env` (example: `GROK_API_KEY=...`).
- Load secrets through the settings module; never hardcode keys in source code.

### Guardrails
- JSON schema validation on output
- hallucination control: disallow attributes not present in candidate context
- fallback path:
  - if LLM output invalid -> retry once with correction prompt
  - if still invalid -> deterministic ranking + template explanation

### Outputs
- `llm_recommender` service
- prompt templates (`v1`)
- parser/validator for LLM responses

### Exit Criteria
- >=90% valid structured LLM responses without manual intervention
- Explanation quality acceptable on curated test set
- Latency and token usage within configured budget

---

## Phase 4: Recommendation API and User Experience
**Objective:** Deliver end-user consumable recommendation flow.

### API Endpoints
- `POST /recommendations`
  - full pipeline: validate -> retrieve -> LLM rank -> format response
- `GET /health`
- `GET /metadata/locations` (optional helper for UI)

### Response Schema (Example)
- `request_id`
- `applied_filters`
- `recommendations[]`:
  - `restaurant_name`
  - `cuisine`
  - `rating`
  - `estimated_cost`
  - `ai_explanation`
- `notes` (e.g., relaxed filters applied)

### UI Considerations
- input widgets for preferences
- recommendation cards with explanation text
- “Why this?” expansion for transparency
- low-result messaging with actionable alternatives

### UI Scope Clarification (Current Stage)
- **`web/` (Vite)**: Primary demo UI—two-column shell (filters + main stage), loading skeletons, results grid with “smart match” affordances, sort controls, and AI-style notes banner when constraints relax—visual language tracks `design/screen.png`, `screen2.png`, `screen3.png`.
- **`/` FastAPI static**: Lightweight parity UI for API validation without Node.
- Map integration and “Collections” nav are **placeholders** until data supports coordinates and saved lists.

### Exit Criteria
- End-to-end usable UX
- API contract stable
- Basic acceptance testing complete

---

## Phase 5: Quality, Evaluation, and Iterative Improvement (Next)
**Objective:** Build confidence in recommendation relevance and reliability.

### Evaluation Dimensions
1. **Relevance**
   - manual rubric scoring (fit to location/budget/cuisine/rating)
2. **Explanation Quality**
   - clarity, specificity, groundedness
3. **System Reliability**
   - success rate, retries, timeout behavior
4. **Performance**
   - p50/p95 latency and token cost

### Workstreams
- Create offline evaluation set of representative queries
- Compare deterministic-only vs deterministic+LLM outcomes
- Add regression tests for prompts and parser
- Instrument logs/metrics dashboards

### Exit Criteria
- Defined baseline metrics and measurable improvement plan
- No critical failures across evaluation scenarios

---

## Phase 6: Production Hardening and Scale Readiness (Later)
**Objective:** Prepare for real usage and future feature expansion.

> Note: This phase is intentionally deferred for now because the current goal is MVP validation under low load (20-30 LLM calls/min).

### Hardening Checklist
- auth/rate limiting (if public API)
- caching frequent query patterns
- async processing for heavier LLM workloads
- robust timeout/retry/circuit breaker settings
- structured audit logging
- secrets management and secure deployment

### Scalability Extensions
- vector search for semantic matching on additional preferences
- hybrid ranking: weighted deterministic + LLM reranker
- user profile memory and personalization over time
- feedback loop to tune ranking/prompt behavior

### Exit Criteria
- production deployment checklist complete
- SLOs defined for availability, latency, and quality

---

## 4) Cross-Cutting Engineering Standards

### Data Contracts
- Strict typed schemas for:
  - ingestion records
  - candidate records
  - LLM outputs
  - API responses

### Error Handling
- clear user-facing messages
- internal error taxonomy:
  - validation errors
  - data access errors
  - LLM errors
  - timeout errors

### Security and Privacy
- do not log sensitive user-identifying payloads in plain text
- sanitize and validate free-text preference inputs

### Testing Strategy
- Unit tests: normalization, filters, prompt builder, parser
- Integration tests: end-to-end recommendation flow
- Golden tests: fixed prompts + expected structured response shape

---

## 5) Implementation Timeline (Suggested)

- **Week 1:** Phase 0 + Phase 1 (completed)
- **Week 2:** Phase 2 (completed)
- **Week 3:** Phase 3 (completed)
- **Week 4:** Phase 4 (completed)
- **Week 5:** Phase 5 (in progress / next)
- **Week 6+:** Phase 6 (deferred until post-MVP validation)

Current MVP implementation has reached Phase 4; remaining work is Phase 5 validation and selective Phase 6 hardening only if needed.

---

## 6) MVP Definition and Review Checklist

### MVP Includes
- dataset ingestion and cleaning
- deterministic candidate filtering
- LLM ranking with grounded explanations
- single API endpoint and simple UI display

### Review Checklist
- Are recommendations aligned with user constraints?
- Are explanations concise and factual?
- Are low/no-result scenarios handled clearly?
- Is p95 latency acceptable for interactive use?
- Are logs sufficient to debug failures quickly?

---

## 7) Risks and Mitigations

1. **Sparse/dirty data in some locations**
   - mitigation: fallback logic and transparency notes
2. **LLM output format drift**
   - mitigation: strict schema validation + retry/fallback path
3. **Prompt over-tokenization**
   - mitigation: candidate compression and top-N cap
4. **Cost growth with traffic**
   - mitigation: cache common requests and tune model usage policy
5. **User trust issues on recommendations**
   - mitigation: clear “why recommended” rationale and constraints shown

---

## 8) Immediate Next Actions

1. Build a Phase 5 evaluation set (30-50 representative queries across cities, budgets, cuisines).
2. Define scoring rubric for relevance + explanation quality and run baseline evaluation.
3. Add prompt/parser regression tests for common failure cases.
4. Capture p50/p95 latency and LLM error-rate metrics under target load (20-30 LLM calls/min).
5. Run Phase 5 evaluation baselines; optionally harden prompts from findings.
6. When deploying, use **`render.yaml`** for FastAPI on Render + Vercel for `web/`, or serve `web/dist` behind FastAPI, or use the **`Dockerfile`** unified stack; always set **`GROQ_API_KEY`** on the API host and **`VITE_API_BASE`** on Vercel, and tighten CORS for cross-origin browser calls.
