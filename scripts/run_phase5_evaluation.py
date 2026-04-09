from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from src.phase_5_evaluation.service_evaluation import run_phase5_evaluation

    parser = argparse.ArgumentParser(description="Run Phase 5 evaluation report.")
    parser.add_argument(
        "--max-queries",
        type=int,
        default=None,
        help="Optional limit for number of evaluation queries.",
    )
    args = parser.parse_args()

    report = run_phase5_evaluation(max_queries=args.max_queries)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
