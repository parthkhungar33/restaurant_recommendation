# Graph Report - .  (2026-04-13)

## Corpus Check
- 62 files · ~95,226 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 357 nodes · 480 edges · 50 communities detected
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 62 edges (avg confidence: 0.71)
- Token cost: 1,200 input · 950 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Architecture Phase Pipeline|Architecture Phase Pipeline]]
- [[_COMMUNITY_Frontend JS Application Logic|Frontend JS Application Logic]]
- [[_COMMUNITY_Design System & UI Integration|Design System & UI Integration]]
- [[_COMMUNITY_API Data Models (Pydantic)|API Data Models (Pydantic)]]
- [[_COMMUNITY_Culinary Curator UI Screens|Culinary Curator UI Screens]]
- [[_COMMUNITY_Data Processing & Deduplication|Data Processing & Deduplication]]
- [[_COMMUNITY_Recommendation UI Components|Recommendation UI Components]]
- [[_COMMUNITY_Discover Tab UI (Loading State)|Discover Tab UI (Loading State)]]
- [[_COMMUNITY_Core Architecture Components|Core Architecture Components]]
- [[_COMMUNITY_Package Init Files|Package Init Files]]
- [[_COMMUNITY_LLM Ranking Service|LLM Ranking Service]]
- [[_COMMUNITY_LLM Unit Tests|LLM Unit Tests]]
- [[_COMMUNITY_UX Service Layer|UX Service Layer]]
- [[_COMMUNITY_Frontend DOM Utilities|Frontend DOM Utilities]]
- [[_COMMUNITY_Evaluation Service|Evaluation Service]]
- [[_COMMUNITY_LLM Provider Interface|LLM Provider Interface]]
- [[_COMMUNITY_Deduplication Tests|Deduplication Tests]]
- [[_COMMUNITY_Regression Gate Tests|Regression Gate Tests]]
- [[_COMMUNITY_Streamlit Host App|Streamlit Host App]]
- [[_COMMUNITY_Live Integration Tests|Live Integration Tests]]
- [[_COMMUNITY_Evaluation Tests|Evaluation Tests]]
- [[_COMMUNITY_App Configuration|App Configuration]]
- [[_COMMUNITY_UX API Endpoints|UX API Endpoints]]
- [[_COMMUNITY_Ingestion Tests|Ingestion Tests]]
- [[_COMMUNITY_Phase 4 API Tests|Phase 4 API Tests]]
- [[_COMMUNITY_Preference Prompt Tests|Preference Prompt Tests]]
- [[_COMMUNITY_Retrieval API Tests|Retrieval API Tests]]
- [[_COMMUNITY_Rating Guard Tests|Rating Guard Tests]]
- [[_COMMUNITY_API Contracts & Config Docs|API Contracts & Config Docs]]
- [[_COMMUNITY_Dedupe Script|Dedupe Script]]
- [[_COMMUNITY_Ingest Script|Ingest Script]]
- [[_COMMUNITY_LLM Smoke Test Script|LLM Smoke Test Script]]
- [[_COMMUNITY_Eval Runner Script|Eval Runner Script]]
- [[_COMMUNITY_Health Check API|Health Check API]]
- [[_COMMUNITY_Phase 0 Bootstrap|Phase 0 Bootstrap]]
- [[_COMMUNITY_Ingestion Script|Ingestion Script]]
- [[_COMMUNITY_Retrieval API|Retrieval API]]
- [[_COMMUNITY_Streamlit UI Home|Streamlit UI Home]]
- [[_COMMUNITY_LLM API Endpoint|LLM API Endpoint]]
- [[_COMMUNITY_Environment Diagnostics|Environment Diagnostics]]
- [[_COMMUNITY_Health Endpoint Test|Health Endpoint Test]]
- [[_COMMUNITY_PostCSS Config|PostCSS Config]]
- [[_COMMUNITY_Tailwind Config|Tailwind Config]]
- [[_COMMUNITY_Vite Config|Vite Config]]
- [[_COMMUNITY_Streamlit Dependency|Streamlit Dependency]]
- [[_COMMUNITY_Preference Intake Component|Preference Intake Component]]
- [[_COMMUNITY_Response Formatter Component|Response Formatter Component]]
- [[_COMMUNITY_Observability Component|Observability Component]]
- [[_COMMUNITY_Top Picks UI Section|Top Picks UI Section]]
- [[_COMMUNITY_Refresh CTA Button|Refresh CTA Button]]

## God Nodes (most connected - your core abstractions)
1. `Restaurant Recommender Project` - 13 edges
2. `normalize_restaurants()` - 11 edges
3. `AppliedFilters` - 10 edges
4. `Search Results Page` - 10 edges
5. `_FakeClient` - 8 edges
6. `buildResultCard()` - 8 edges
7. `Filter Panel (Sidebar)` - 8 edges
8. `Phase 5 evaluation artifacts.` - 7 edges
9. `RecommendationQueryRequest` - 7 edges
10. `GroqChatClient` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Streamlit host for the restaurant recommender (deploy on Streamlit Community Clo` --uses--> `RecommendationQueryRequest`  [INFERRED]
  streamlit_app.py → src\phase_2_retrieval\model_recommendation.py
- `Chef's Kiss Recommendation Card Component` --semantically_similar_to--> `Recommendation Card Image Strategy (Cuisine-Aware + Fallback)`  [INFERRED] [semantically similar]
  design/DESIGN.md → docs/project_handoff.md
- `Three-Layer Deduplication Strategy` --semantically_similar_to--> `No Duplicate Restaurants Rule in Prompt`  [INFERRED] [semantically similar]
  docs/improvements.md → src/phase_3_llm/prompts/system_v1.txt
- `_FakeClient` --uses--> `RecommendationQueryRequest`  [INFERRED]
  tests\test_llm_recommender.py → src\phase_2_retrieval\model_recommendation.py
- `_FakeClient` --uses--> `RecommendationItem`  [INFERRED]
  tests\test_llm_recommender.py → src\phase_2_retrieval\model_recommendation.py

## Hyperedges (group relationships)
- **Deterministic Retrieval + LLM Ranking + Response Formatting Pipeline** — arch_candidate_retrieval, arch_llm_recommendation_layer, arch_response_formatter [EXTRACTED 0.95]
- **Split-Origin Production Deployment (Vercel SPA + Render FastAPI + Groq LLM)** — readme_vercel_deploy, readme_render_deploy, readme_groq_llm [EXTRACTED 0.95]
- **Improvement Phases A-D as Quality Gate for MVP UX** — improvements_phase_a, improvements_phase_c, improvements_phase_d [EXTRACTED 0.88]

## Communities

### Community 0 - "Architecture Phase Pipeline"
Cohesion: 0.07
Nodes (39): Constraint Relaxation Strategy (Filter Fallback), LLM Guardrails (JSON Validation, Retry, Fallback), Phase 0: Foundation and Project Setup, Phase 1: Data Ingestion and Canonical Store, Phase 2: Preference Intake and Deterministic Retrieval, Phase 3: LLM Ranking and Explanation Layer, Phase 4: Recommendation API and User Experience, Phase 5: Quality, Evaluation, and Iterative Improvement (+31 more)

### Community 1 - "Frontend JS Application Logic"
Cohesion: 0.1
Nodes (31): apiFetch(), buildFriendlyRelaxedMessage(), buildPayload(), buildResultCard(), buildSkeleton(), cardImageUrl(), collectAdditionalPreferences(), collectCuisinePayload() (+23 more)

### Community 2 - "Design System & UI Integration"
Cohesion: 0.07
Nodes (36): Frontend/Backend Integration (Vite Proxy + CORS), Chef's Kiss Recommendation Card Component, Color Palette (Sun-Drenched Tones), Design System: Culinary Concierge, Elevation & Depth System, No-Line Rule (Color-Shift Boundaries), Soft Minimalism Design Philosophy, Typography System (Plus Jakarta Sans, Be Vietnam Pro) (+28 more)

### Community 3 - "API Data Models (Pydantic)"
Cohesion: 0.13
Nodes (22): BaseModel, LocationsResponse, UXRecommendationItem, UXRecommendationResponse, HealthResponse, LLMRankedItem, LLMRankedList, LLMRecommendationResponse (+14 more)

### Community 4 - "Culinary Curator UI Screens"
Cohesion: 0.17
Nodes (22): Culinary Curator App, Explore Indiranagar Map Section, Cuisine Filter, Dining Type Filter, Filter Panel, Rating Filter, Smart Tags Filter, Indiranagar Location Filter (+14 more)

### Community 5 - "Data Processing & Deduplication"
Cohesion: 0.19
Nodes (20): _budget_band(), BudgetThresholds, build_quality_report(), _city_from_url(), create_restaurants_indexes(), dedupe_restaurants_by_business_key(), dedupe_restaurants_table_in_sqlite(), _derive_service_tags() (+12 more)

### Community 6 - "Recommendation UI Components"
Cohesion: 0.18
Nodes (18): AI Concierge Pod (LLM Explanation Widget), AI Concierge Pod LLM Explanation, Show Me Great Places CTA Button, The Culinary Concierge App, The Culinary Concierge App, Budget Range Slider Filter, Location Filter Input, Mood/Cuisine Filter (Italian, Fast Food) (+10 more)

### Community 7 - "Discover Tab UI (Loading State)"
Cohesion: 0.19
Nodes (15): Bangalore Location Context, Cuisine Filter, Culinary Curator App, Dining Type Filter, Discover Tab, Filter Panel (Sidebar), Indiranagar Locality Selection, LLM-Powered Search Message (+7 more)

### Community 8 - "Core Architecture Components"
Cohesion: 0.25
Nodes (11): Core Component: Candidate Retrieval Layer, Core Component: Data Ingestion Pipeline, Architecture Goal: AI-Powered Restaurant Recommendation, Core Component: LLM Recommendation Layer, MVP Constraints (Low Load, Clarity Focus), Risks and Mitigations, Rationale: Rules-Based + LLM Blend for Trust, Problem Statement: AI Restaurant Recommendation System (+3 more)

### Community 9 - "Package Init Files"
Cohesion: 0.25
Nodes (1): Phase 5 evaluation artifacts.

### Community 10 - "LLM Ranking Service"
Cohesion: 0.43
Nodes (6): _build_user_prompt(), _extract_json(), _fallback_rank(), _load_system_prompt(), rank_candidates_with_llm(), _validate_ranked_list()

### Community 11 - "LLM Unit Tests"
Cohesion: 0.46
Nodes (5): _FakeClient, _sample_candidates(), test_llm_rank_dedupes_duplicate_ids(), test_llm_rank_fallback_after_invalid_outputs(), test_llm_rank_valid_json()

### Community 12 - "UX Service Layer"
Cohesion: 0.4
Nodes (2): build_recommendation_response(), _signature()

### Community 13 - "Frontend DOM Utilities"
Cohesion: 0.33
Nodes (0): 

### Community 14 - "Evaluation Service"
Cohesion: 0.6
Nodes (5): _load_queries(), _percentile(), run_phase5_evaluation(), _score_explanation_quality(), _score_relevance()

### Community 15 - "LLM Provider Interface"
Cohesion: 0.5
Nodes (3): ABC, LLMProvider, Provider interface for future LLM integrations.

### Community 16 - "Deduplication Tests"
Cohesion: 0.4
Nodes (0): 

### Community 17 - "Regression Gate Tests"
Cohesion: 0.6
Nodes (3): _seed_test_db(), test_max_budget_filter_behavior(), test_same_name_different_locality_not_deduped()

### Community 18 - "Streamlit Host App"
Cohesion: 0.5
Nodes (1): Streamlit host for the restaurant recommender (deploy on Streamlit Community Clo

### Community 19 - "Live Integration Tests"
Cohesion: 0.83
Nodes (3): _require_live_env(), test_live_groq_connectivity_returns_text(), test_live_recommendations_endpoint_llm_flow()

### Community 20 - "Evaluation Tests"
Cohesion: 0.5
Nodes (0): 

### Community 21 - "App Configuration"
Cohesion: 0.67
Nodes (2): BaseSettings, Settings

### Community 22 - "UX API Endpoints"
Cohesion: 0.67
Nodes (0): 

### Community 23 - "Ingestion Tests"
Cohesion: 0.67
Nodes (0): 

### Community 24 - "Phase 4 API Tests"
Cohesion: 0.67
Nodes (0): 

### Community 25 - "Preference Prompt Tests"
Cohesion: 0.67
Nodes (0): 

### Community 26 - "Retrieval API Tests"
Cohesion: 0.67
Nodes (0): 

### Community 27 - "Rating Guard Tests"
Cohesion: 1.0
Nodes (2): _make_test_db(), test_min_rating_not_relaxed_when_partial_results_exist()

### Community 28 - "API Contracts & Config Docs"
Cohesion: 0.67
Nodes (3): API Contract Reference, Config and Environment Variables, User Journey with API Timing

### Community 29 - "Dedupe Script"
Cohesion: 1.0
Nodes (0): 

### Community 30 - "Ingest Script"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "LLM Smoke Test Script"
Cohesion: 1.0
Nodes (0): 

### Community 32 - "Eval Runner Script"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Health Check API"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Phase 0 Bootstrap"
Cohesion: 1.0
Nodes (1): Phase 0 contains foundational modules consumed by later phases.

### Community 35 - "Ingestion Script"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Retrieval API"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Streamlit UI Home"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "LLM API Endpoint"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Environment Diagnostics"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Health Endpoint Test"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "PostCSS Config"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Tailwind Config"
Cohesion: 1.0
Nodes (0): 

### Community 43 - "Vite Config"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Streamlit Dependency"
Cohesion: 1.0
Nodes (1): streamlit dependency

### Community 45 - "Preference Intake Component"
Cohesion: 1.0
Nodes (1): Core Component: Preference Intake API/UI

### Community 46 - "Response Formatter Component"
Cohesion: 1.0
Nodes (1): Core Component: Response Formatter

### Community 47 - "Observability Component"
Cohesion: 1.0
Nodes (1): Core Component: Observability and Feedback

### Community 48 - "Top Picks UI Section"
Cohesion: 1.0
Nodes (1): Top Picks For You Section

### Community 49 - "Refresh CTA Button"
Cohesion: 1.0
Nodes (1): Refresh Recommendations CTA Button

## Knowledge Gaps
- **50 isolated node(s):** `Phase 0 contains foundational modules consumed by later phases.`, `Provider interface for future LLM integrations.`, `BudgetThresholds`, `Keep one row per business key: name + city + locality.      Tie-break order (a`, `Create retrieval indexes and a unique constraint on business key.` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Dedupe Script`** (2 nodes): `main()`, `dedupe_restaurants_db.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ingest Script`** (2 nodes): `main()`, `ingest_restaurants.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LLM Smoke Test Script`** (2 nodes): `main()`, `run_dummy_llm_request.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Eval Runner Script`** (2 nodes): `main()`, `run_phase5_evaluation.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Health Check API`** (2 nodes): `health()`, `api_health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Phase 0 Bootstrap`** (2 nodes): `Phase 0 contains foundational modules consumed by later phases.`, `main.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ingestion Script`** (2 nodes): `main()`, `script_ingest_restaurants.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Retrieval API`** (2 nodes): `recommendations_query()`, `api_recommendations.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Streamlit UI Home`** (2 nodes): `ui_home()`, `main.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LLM API Endpoint`** (2 nodes): `recommendations_llm()`, `api_llm_recommendations.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Environment Diagnostics`** (2 nodes): `test_groq_api_key_presence_flag()`, `test_env_diagnostics.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Health Endpoint Test`** (2 nodes): `test_health_endpoint_returns_ok()`, `test_health.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PostCSS Config`** (1 nodes): `postcss.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tailwind Config`** (1 nodes): `tailwind.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Vite Config`** (1 nodes): `vite.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Streamlit Dependency`** (1 nodes): `streamlit dependency`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Preference Intake Component`** (1 nodes): `Core Component: Preference Intake API/UI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Response Formatter Component`** (1 nodes): `Core Component: Response Formatter`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Observability Component`** (1 nodes): `Core Component: Observability and Feedback`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Top Picks UI Section`** (1 nodes): `Top Picks For You Section`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Refresh CTA Button`** (1 nodes): `Refresh Recommendations CTA Button`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Restaurant Recommender Project` connect `Design System & UI Integration` to `Architecture Phase Pipeline`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `Hugging Face Zomato Dataset` connect `Design System & UI Integration` to `Architecture Phase Pipeline`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `AppliedFilters` (e.g. with `FilterState` and `Copy for when we widen filters so results are not empty or too sparse.`) actually correct?**
  _`AppliedFilters` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Phase 0 contains foundational modules consumed by later phases.`, `Provider interface for future LLM integrations.`, `BudgetThresholds` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Architecture Phase Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Frontend JS Application Logic` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `Design System & UI Integration` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._