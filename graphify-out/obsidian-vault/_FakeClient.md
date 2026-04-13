# _FakeClient

- **Type:** code
- **Source:** `tests\test_llm_recommender.py` L8
- **Community:** 11

## Outgoing
- `method` → [[.__init__()_1|.__init__()]]
- `method` → [[.complete()_1|.complete()]]
- `calls` → [[test_llm_rank_valid_json()|test_llm_rank_valid_json()]]
- `calls` → [[test_llm_rank_fallback_after_invalid_outputs()|test_llm_rank_fallback_after_invalid_outputs()]]
- `calls` → [[test_llm_rank_dedupes_duplicate_ids()|test_llm_rank_dedupes_duplicate_ids()]]

## Incoming
- [[RecommendationQueryRequest|RecommendationQueryRequest]] → `uses`
- [[RecommendationItem|RecommendationItem]] → `uses`
- [[test_llm_recommender.py|test_llm_recommender.py]] → `contains`
