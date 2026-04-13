# dedupe_restaurants_by_business_key()

- **Type:** code
- **Source:** `src\phase_1_ingestion\data_ingestion.py` L123
- **Community:** 5

## Outgoing
- `calls` → [[dedupe_restaurants_table_in_sqlite()|dedupe_restaurants_table_in_sqlite()]]
- `calls` → [[normalize_restaurants()|normalize_restaurants()]]
- `rationale_for` → [[Keep one row per business key_ name + city + locality.      Tie-break order (a|Keep one row per business key: name + city + locality.      Tie-break order (a]]

## Incoming
- [[data_ingestion.py|data_ingestion.py]] → `contains`
