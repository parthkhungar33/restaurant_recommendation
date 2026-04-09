from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from src.phase_2_retrieval.main import app

EVAL_QUERIES_PATH = Path("src/phase_5_evaluation/data/eval_queries.json")
EVAL_OUTPUT_DIR = Path("src/phase_5_evaluation/results")


def _load_queries(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _score_explanation_quality(text: str) -> float:
    if not text:
        return 0.0
    words = text.split()
    if len(words) < 8:
        return 2.0
    if len(words) < 14:
        return 3.0
    return 4.0


def _score_relevance(query: dict[str, Any], recommendation: dict[str, Any]) -> float:
    score = 0.0
    cuisine = str(query.get("cuisine", "")).lower()
    budget = query.get("budget")
    max_budget = query.get("max_budget")
    min_rating = query.get("min_rating")

    rec_cuisine = str(recommendation.get("cuisine") or "").lower()
    rec_cost = recommendation.get("estimated_cost")
    rec_rating = recommendation.get("rating")

    if cuisine and cuisine in rec_cuisine:
        score += 2.0

    if isinstance(rec_cost, (int, float)):
        if isinstance(max_budget, (int, float)):
            if rec_cost <= float(max_budget):
                score += 1.0
        elif budget:
            if budget == "low" and rec_cost <= 600:
                score += 1.0
            elif budget == "medium" and 600 < rec_cost <= 1500:
                score += 1.0
            elif budget == "high" and rec_cost > 1500:
                score += 1.0

    if isinstance(rec_rating, (int, float)) and isinstance(min_rating, (int, float)):
        if rec_rating >= float(min_rating):
            score += 2.0

    return min(score, 5.0)


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(round((p / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


def run_phase5_evaluation(max_queries: int | None = None) -> dict[str, Any]:
    queries = _load_queries(EVAL_QUERIES_PATH)
    if max_queries is not None:
        queries = queries[:max_queries]

    client = TestClient(app)
    latencies_ms: list[float] = []
    success_count = 0
    empty_count = 0
    fallback_note_count = 0
    comparison_overlap_count = 0
    relevance_scores: list[float] = []
    explanation_scores: list[float] = []
    rows: list[dict[str, Any]] = []

    for idx, query in enumerate(queries, start=1):
        start = time.perf_counter()
        response = client.post("/recommendations", json=query)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies_ms.append(elapsed_ms)

        row: dict[str, Any] = {
            "query_index": idx,
            "query": query,
            "status_code": response.status_code,
            "latency_ms": round(elapsed_ms, 2),
        }

        if response.status_code != 200:
            row["error"] = response.text
            rows.append(row)
            continue

        success_count += 1
        payload = response.json()
        recs = payload.get("recommendations", [])
        notes = payload.get("notes", [])
        if not recs:
            empty_count += 1
        if any("relaxed" in str(n).lower() for n in notes):
            fallback_note_count += 1

        # Compare deterministic and llm routes for quick overlap check.
        deterministic = client.post("/recommendations/query", json=query).json()
        det_ids = {r.get("restaurant_id") for r in deterministic.get("recommendations", [])}
        llm_ids = {r.get("restaurant_id") for r in recs}
        overlap = len(det_ids.intersection(llm_ids))
        if overlap > 0:
            comparison_overlap_count += 1

        if recs:
            top = recs[0]
            rel_score = _score_relevance(query, top)
            exp_score = _score_explanation_quality(str(top.get("ai_explanation") or ""))
            relevance_scores.append(rel_score)
            explanation_scores.append(exp_score)
            row["top1_relevance_score_0_5"] = rel_score
            row["top1_explanation_score_0_5"] = exp_score
            row["top1_name"] = top.get("restaurant_name")
        row["result_count"] = len(recs)
        row["has_relaxed_filters_note"] = any("relaxed" in str(n).lower() for n in notes)
        row["deterministic_overlap_count"] = overlap
        rows.append(row)

    total = len(queries)
    report = {
        "total_queries": total,
        "success_rate": round(success_count / total, 4) if total else 0.0,
        "empty_result_rate": round(empty_count / total, 4) if total else 0.0,
        "fallback_note_rate": round(fallback_note_count / total, 4) if total else 0.0,
        "deterministic_overlap_rate": round(comparison_overlap_count / total, 4) if total else 0.0,
        "latency_ms": {
            "p50": round(_percentile(latencies_ms, 50), 2),
            "p95": round(_percentile(latencies_ms, 95), 2),
            "mean": round(statistics.mean(latencies_ms), 2) if latencies_ms else 0.0,
        },
        "scoring_summary_0_5": {
            "relevance_mean": round(statistics.mean(relevance_scores), 2)
            if relevance_scores
            else 0.0,
            "explanation_mean": round(statistics.mean(explanation_scores), 2)
            if explanation_scores
            else 0.0,
        },
        "manual_review_required": True,
        "rows": rows,
    }

    EVAL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = EVAL_OUTPUT_DIR / "phase5_eval_report.json"
    output_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
