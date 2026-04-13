# normalize_restaurants()

- **Type:** code
- **Source:** `src\phase_1_ingestion\data_ingestion.py` L239
- **Community:** 5

## Outgoing
- `calls` → [[run_ingestion()|run_ingestion()]]

## Incoming
- [[data_ingestion.py|data_ingestion.py]] → `contains`
- [[_pick_column()|_pick_column()]] → `calls`
- [[_normalize_text()|_normalize_text()]] → `calls`
- [[_city_from_url()|_city_from_url()]] → `calls`
- [[_parse_float()|_parse_float()]] → `calls`
- [[_parse_int()|_parse_int()]] → `calls`
- [[_parse_cuisines()|_parse_cuisines()]] → `calls`
- [[_derive_service_tags()|_derive_service_tags()]] → `calls`
- [[_budget_band()|_budget_band()]] → `calls`
- [[dedupe_restaurants_by_business_key()|dedupe_restaurants_by_business_key()]] → `calls`
