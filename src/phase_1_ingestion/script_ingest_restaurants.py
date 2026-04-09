from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.phase_1_ingestion.data_ingestion import run_ingestion


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest and normalize restaurants dataset.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("src/phase_1_ingestion/data/restaurants.db"),
        help="Output SQLite file path.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("src/phase_1_ingestion/data/quality_report.json"),
        help="Output data quality report path.",
    )
    args = parser.parse_args()

    report = run_ingestion(output_db_path=args.db_path, report_path=args.report_path)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
