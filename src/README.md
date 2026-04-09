# Source Organization by Phase

- `web/` (repo root): **Culinary Curator** Vite frontend; pairs with FastAPI for local demo.

- `src/phase_0_foundation`: project bootstrap, config, base API health, interface scaffolding
- `src/phase_1_ingestion`: dataset ingestion, normalization, persistence, quality reporting
- `src/phase_2_retrieval`: deterministic recommendation query API and retrieval logic
- `src/phase_3_llm`: Groq LLM ranking, prompt templates, output parsing, and fallback behavior
- `src/phase_4_api_ux`: stable user-facing API response contract and metadata endpoints
- `src/phase_5_evaluation`: representative query set, scoring helpers, and evaluation reporting

These folders are the runtime source of truth for phase-wise inspection and implementation.
