import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    from src.phase_2_retrieval.main import app

    client = TestClient(app)
    payload = {
        "location": "Bangalore",
        "max_budget": 1200,
        "cuisine": "Italian",
        "min_rating": 4.0,
        "additional_preferences": "family-friendly, quick service",
        "limit": 3,
    }
    response = client.post("/recommendations", json=payload)
    print("status=", response.status_code)
    data = response.json()
    print("total_candidates=", data.get("total_candidates"))
    recs = data.get("recommendations", [])
    print("recommendations_count=", len(recs))
    for row in recs[:3]:
        print(
            "-",
            {
                "llm_rank": row.get("llm_rank"),
                "restaurant_name": row.get("restaurant_name"),
                "restaurant_id": row.get("restaurant_id"),
            },
        )
    print("notes=", data.get("notes"))


if __name__ == "__main__":
    main()
