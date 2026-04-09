from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from src.phase_1_ingestion.script_ingest_restaurants import main as phase_1_main

    phase_1_main()


if __name__ == "__main__":
    main()
