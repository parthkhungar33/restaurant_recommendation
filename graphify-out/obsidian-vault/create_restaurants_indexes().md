# create_restaurants_indexes()

- **Type:** code
- **Source:** `src\phase_1_ingestion\data_ingestion.py` L167
- **Community:** 5

## Outgoing
- `calls` → [[dedupe_restaurants_table_in_sqlite()|dedupe_restaurants_table_in_sqlite()]]
- `calls` → [[persist_to_sqlite()|persist_to_sqlite()]]
- `rationale_for` → [[Create retrieval indexes and a unique constraint on business key.|Create retrieval indexes and a unique constraint on business key.]]

## Incoming
- [[data_ingestion.py|data_ingestion.py]] → `contains`
