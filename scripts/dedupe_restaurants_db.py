from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from src.phase_1_ingestion.data_ingestion import dedupe_restaurants_table_in_sqlite

    parser = argparse.ArgumentParser(
        description=(
            "Deduplicate restaurants_clean by name + location_city + locality in SQLite (in-place)."
        ),
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("src/phase_1_ingestion/data/restaurants.db"),
        help="Path to SQLite database containing restaurants_clean.",
    )
    args = parser.parse_args()

    stats = dedupe_restaurants_table_in_sqlite(args.db_path)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
