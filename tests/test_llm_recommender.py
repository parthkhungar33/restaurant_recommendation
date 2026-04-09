from src.phase_2_retrieval.model_recommendation import (
    RecommendationItem,
    RecommendationQueryRequest,
)
from src.phase_3_llm.service_llm_recommender import rank_candidates_with_llm


class _FakeClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.idx = 0

    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        _ = system_prompt
        _ = user_prompt
        out = self.outputs[min(self.idx, len(self.outputs) - 1)]
        self.idx += 1
        return out


def _sample_candidates() -> list[RecommendationItem]:
    return [
        RecommendationItem(
            restaurant_id="r1",
            restaurant_name="Alpha",
            cuisine="North Indian",
            rating=4.3,
            estimated_cost=1000,
            locality="Banashankari",
            reason_tags=["location_match"],
        ),
        RecommendationItem(
            restaurant_id="r2",
            restaurant_name="Beta",
            cuisine="Chinese",
            rating=4.1,
            estimated_cost=900,
            locality="Indiranagar",
            reason_tags=["location_match"],
        ),
    ]


def test_llm_rank_valid_json() -> None:
    client = _FakeClient(
        [
            (
                '{"recommendations":[{"restaurant_id":"r2","restaurant_name":"Beta",'
                '"ai_explanation":"Great fit","llm_rank":1}]}'
            )
        ]
    )
    result = rank_candidates_with_llm(
        request=RecommendationQueryRequest(location="Bangalore", limit=2),
        candidates=_sample_candidates(),
        client=client,  # type: ignore[arg-type]
    )
    assert result[0].restaurant_id == "r2"


def test_llm_rank_fallback_after_invalid_outputs() -> None:
    client = _FakeClient(["invalid json", "still invalid"])
    result = rank_candidates_with_llm(
        request=RecommendationQueryRequest(location="Bangalore", limit=2),
        candidates=_sample_candidates(),
        client=client,  # type: ignore[arg-type]
    )
    assert len(result) == 2
    assert result[0].llm_rank == 1


def test_llm_rank_dedupes_duplicate_ids() -> None:
    client = _FakeClient(
        [
            (
                '{"recommendations":['
                '{"restaurant_id":"r1","restaurant_name":"Alpha","ai_explanation":"x","llm_rank":1},'
                '{"restaurant_id":"r1","restaurant_name":"Alpha","ai_explanation":"y","llm_rank":2},'
                '{"restaurant_id":"r2","restaurant_name":"Beta","ai_explanation":"z","llm_rank":3}'
                "]} "
            )
        ]
    )
    result = rank_candidates_with_llm(
        request=RecommendationQueryRequest(location="Bangalore", limit=3),
        candidates=_sample_candidates(),
        client=client,  # type: ignore[arg-type]
    )
    ids = [item.restaurant_id for item in result]
    assert ids == ["r1", "r2"]
