"""Streamlit host for the restaurant recommender (deploy on Streamlit Community Cloud).

The Vite SPA on Vercel calls the FastAPI JSON API. Streamlit Community Cloud does not expose a
second public port for that API on the same deployment, so for one public backend URL use the
Docker image (nginx + uvicorn + streamlit) at the repo `Dockerfile`.
"""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent


def _apply_secrets_to_environ() -> None:
    try:
        secrets = st.secrets
    except (FileNotFoundError, RuntimeError):
        return
    if "GROQ_API_KEY" in secrets and secrets["GROQ_API_KEY"]:
        os.environ["GROQ_API_KEY"] = str(secrets["GROQ_API_KEY"])
    if "DB_PATH" in secrets and secrets["DB_PATH"]:
        os.environ["DB_PATH"] = str(secrets["DB_PATH"])


_apply_secrets_to_environ()

if "DB_PATH" not in os.environ:
    _candidate = ROOT / "src/phase_1_ingestion/data/restaurants.db"
    if _candidate.is_file():
        os.environ["DB_PATH"] = str(_candidate)

from src.phase_0_foundation.core_config import settings
from src.phase_2_retrieval.model_recommendation import RecommendationQueryRequest
from src.phase_4_api_ux.service_api_ux import (
    build_recommendation_response,
    get_locations,
    get_top_cuisines,
    get_top_experiences,
)

st.set_page_config(page_title="Restaurant Recommender", layout="wide")
st.title("Restaurant Recommender")
st.caption("Deterministic retrieval + Groq LLM ranking — same services as the FastAPI backend.")

locations = get_locations(settings.db_path)
if not locations:
    st.error(
        "SQLite database not found. On Streamlit Cloud, commit `restaurants.db` "
        "or run ingestion in CI and ship the file with the app. "
        "Local path: `src/phase_1_ingestion/data/restaurants.db`."
    )
    st.stop()

cuisine_options = [str(c["value"]) for c in get_top_cuisines()]
experience_rows = get_top_experiences()
exp_labels = {str(r["value"]): str(r["label"]) for r in experience_rows}
exp_values = list(exp_labels.keys())

with st.sidebar:
    st.header("Filters")
    location = st.selectbox("City", locations, index=0)
    max_budget = st.slider(
        "Max budget (₹ for two)",
        min_value=300,
        max_value=6000,
        value=1800,
        step=100,
    )
    selected_cuisines = st.multiselect("Cuisines", cuisine_options)
    rating_label = st.selectbox("Minimum rating", ["Any", "3★+", "4★+", "4.5★+"])
    min_rating_map = {"Any": None, "3★+": 3.0, "4★+": 4.0, "4.5★+": 4.5}
    min_rating = min_rating_map[rating_label]

    def _exp_label(v: str) -> str:
        return exp_labels.get(v, v)

    selected_experience = st.multiselect(
        "Experience / mood",
        exp_values,
        format_func=_exp_label,
    )
    pref_extra = st.text_area(
        "Additional preferences (optional)",
        placeholder="e.g. outdoor seating, quiet",
    )

run = st.button("Show recommendations", type="primary")

if run:
    extras: list[str] = list(selected_experience)
    if pref_extra.strip():
        extras.extend([p.strip() for p in pref_extra.replace("\n", ",").split(",") if p.strip()])
    payload = RecommendationQueryRequest(
        location=location,
        max_budget=float(max_budget),
        cuisine=selected_cuisines or None,
        min_rating=min_rating,
        additional_preferences=extras or None,
        limit=10,
    )
    try:
        with st.spinner("Retrieving and ranking…"):
            response = build_recommendation_response(payload)
    except RuntimeError as exc:
        st.error(str(exc))
    except FileNotFoundError as exc:
        st.error(str(exc))
    else:
        st.subheader("Applied filters")
        st.json(response.applied_filters.model_dump())
        if response.notes:
            for note in response.notes:
                st.info(note)
        if not response.recommendations:
            st.warning("No restaurants matched. Try relaxing filters.")
        else:
            st.subheader(f"Top picks ({len(response.recommendations)})")
            for item in response.recommendations:
                with st.expander(f"{item.restaurant_name} — {item.rating or '—'}★", expanded=False):
                    st.write(f"**Cuisine:** {item.cuisine}")
                    if item.estimated_cost is not None:
                        st.write(f"**Estimated cost (two):** ₹{item.estimated_cost:,.0f}")
                    st.write(item.ai_explanation or "_No explanation._")
