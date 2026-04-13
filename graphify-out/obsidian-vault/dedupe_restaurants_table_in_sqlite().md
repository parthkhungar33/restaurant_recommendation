# dedupe_restaurants_table_in_sqlite()

- **Type:** code
- **Source:** `src\phase_1_ingestion\data_ingestion.py` L190
- **Community:** 5

## Outgoing
- `rationale_for` → [[Rewrite `restaurants_clean` in-place so business key appears once.|Rewrite `restaurants_clean` in-place so business key appears once.]]

## Incoming
- [[data_ingestion.py|data_ingestion.py]] → `contains`
- [[dedupe_restaurants_by_business_key()|dedupe_restaurants_by_business_key()]] → `calls`
- [[create_restaurants_indexes()|create_restaurants_indexes()]] → `calls`
