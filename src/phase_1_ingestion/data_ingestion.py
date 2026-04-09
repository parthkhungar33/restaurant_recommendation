from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

SOURCE_DATASET = "ManikaSaini/zomato-restaurant-recommendation"


@dataclass(frozen=True)
class BudgetThresholds:
    low_max: float = 600.0
    medium_max: float = 1500.0


def _pick_column(df: pd.DataFrame, aliases: list[str], required: bool = False) -> str | None:
    def normalize_key(text: str) -> str:
        return re.sub(r"[^a-z0-9]", "", text.lower())

    lower_map = {normalize_key(col): col for col in df.columns}
    for alias in aliases:
        key = normalize_key(alias)
        if key in lower_map:
            return lower_map[key]
    if required:
        raise ValueError(f"Required column missing. Tried aliases: {aliases}")
    return None


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None
    return " ".join(text.split())


def _city_from_url(value: Any) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None
    match = re.search(r"zomato\.com/([^/]+)/", text.lower())
    if not match:
        return None
    city = match.group(1).replace("-", " ").strip()
    return city.title() if city else None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"[^0-9.]", "", text)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_int(value: Any) -> int | None:
    parsed = _parse_float(value)
    return int(parsed) if parsed is not None else None


def _parse_cuisines(value: Any) -> list[str]:
    text = _normalize_text(value)
    if not text:
        return []
    raw_parts = re.split(r"[,/|;]+", text)
    cuisines: list[str] = []
    seen: set[str] = set()
    for part in raw_parts:
        item = part.strip().title()
        if not item:
            continue
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cuisines.append(item)
    return cuisines


def _derive_service_tags(name: str | None, cuisines: list[str], locality: str | None) -> list[str]:
    tags: list[str] = []
    joined = " ".join([name or "", locality or "", " ".join(cuisines)]).lower()
    mapping = {
        "family": "family-friendly",
        "quick": "quick-service",
        "fast": "quick-service",
        "cafe": "casual",
        "fine": "fine-dine",
        "bar": "nightlife",
    }
    for key, tag in mapping.items():
        if key in joined and tag not in tags:
            tags.append(tag)
    return tags


def _budget_band(avg_cost_for_two: float | None, thresholds: BudgetThresholds) -> str:
    if avg_cost_for_two is None:
        return "unknown"
    if avg_cost_for_two <= thresholds.low_max:
        return "low"
    if avg_cost_for_two <= thresholds.medium_max:
        return "medium"
    return "high"


def dedupe_restaurants_by_business_key(df: pd.DataFrame) -> pd.DataFrame:
    """Keep one row per business key: name + city + locality.

    Tie-break order (all descending preference): non-null rating, higher votes,
    non-null avg_cost_for_two, non-empty locality, longer cuisines_text,
    latest ingested_at.
    """
    if df.empty:
        return df
    work = df.copy()
    work["_has_rating"] = work["rating"].notna().astype(int)
    work["_votes"] = pd.to_numeric(work["votes"], errors="coerce").fillna(-1.0)
    work["_has_cost"] = work["avg_cost_for_two"].notna().astype(int)
    loc_str = work["locality"].fillna("").astype(str).str.strip()
    work["_has_locality"] = (loc_str != "").astype(int)
    work["_cuisines_len"] = work["cuisines_text"].fillna("").astype(str).map(len)
    work["_ingested_ts"] = pd.to_datetime(work["ingested_at"], utc=True, errors="coerce")
    epoch = pd.Timestamp("1970-01-01", tz="UTC")
    work["_ingested_ts"] = work["_ingested_ts"].fillna(epoch)

    work["_key_name"] = work["name"].fillna("").astype(str).str.strip().str.lower()
    work["_key_city"] = work["location_city"].fillna("").astype(str).str.strip().str.lower()
    work["_key_locality"] = work["locality"].fillna("").astype(str).str.strip().str.lower()

    work = work.sort_values(
        by=[
            "_key_name",
            "_key_city",
            "_key_locality",
            "_has_rating",
            "_votes",
            "_has_cost",
            "_has_locality",
            "_cuisines_len",
            "_ingested_ts",
        ],
        ascending=[True, True, True, False, False, False, False, False, False],
    )
    result = work.drop_duplicates(subset=["_key_name", "_key_city", "_key_locality"], keep="first")
    drop_cols = [c for c in result.columns if c.startswith("_")]
    result = result.drop(columns=drop_cols)
    return result.reset_index(drop=True)


def create_restaurants_indexes(conn: sqlite3.Connection) -> None:
    """Create retrieval indexes and a unique constraint on business key."""
    conn.execute("DROP INDEX IF EXISTS ux_restaurants_restaurant_id")
    conn.execute("DROP INDEX IF EXISTS ux_restaurants_name_city_locality")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_restaurants_name_city_locality "
        "ON restaurants_clean(name, location_city, COALESCE(locality, ''))"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants_clean(location_city)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants_clean(rating)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_restaurants_budget ON restaurants_clean(budget_band)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_restaurants_cuisines_text "
        "ON restaurants_clean(cuisines_text)"
    )


def dedupe_restaurants_table_in_sqlite(sqlite_path: Path) -> dict[str, Any]:
    """Rewrite `restaurants_clean` in-place so business key appears once."""
    sqlite_path = Path(sqlite_path)
    if not sqlite_path.exists():
        raise FileNotFoundError(f"Database not found: {sqlite_path}")

    with sqlite3.connect(sqlite_path) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            ("restaurants_clean",),
        ).fetchone()
        if not tables:
            raise ValueError("Table restaurants_clean does not exist.")

        df = pd.read_sql_query("SELECT * FROM restaurants_clean", conn)
        before_rows = len(df)
        key_df = df.copy()
        key_df["_key_name"] = key_df["name"].fillna("").astype(str).str.strip().str.lower()
        key_df["_key_city"] = key_df["location_city"].fillna("").astype(str).str.strip().str.lower()
        key_df["_key_locality"] = key_df["locality"].fillna("").astype(str).str.strip().str.lower()
        duplicate_rows = int(
            key_df.duplicated(subset=["_key_name", "_key_city", "_key_locality"], keep=False).sum()
        )

        deduped = dedupe_restaurants_by_business_key(df)
        after_rows = len(deduped)

        deduped.to_sql("restaurants_clean__deduped", conn, if_exists="replace", index=False)
        conn.execute("DROP TABLE restaurants_clean")
        conn.execute("ALTER TABLE restaurants_clean__deduped RENAME TO restaurants_clean")
        create_restaurants_indexes(conn)
        conn.commit()

    return {
        "db_path": str(sqlite_path),
        "rows_before": before_rows,
        "rows_after": after_rows,
        "rows_removed": before_rows - after_rows,
        "rows_in_duplicate_groups": duplicate_rows,
        "dedupe_key": ["name", "location_city", "locality"],
    }


def fetch_source_dataframe() -> pd.DataFrame:
    dataset = load_dataset(SOURCE_DATASET)
    split_name = "train" if "train" in dataset else list(dataset.keys())[0]
    return dataset[split_name].to_pandas()


def normalize_restaurants(
    raw_df: pd.DataFrame,
    ingest_version: str,
    thresholds: BudgetThresholds = BudgetThresholds(),
) -> pd.DataFrame:
    id_col = _pick_column(raw_df, ["restaurant_id", "res_id", "id"], required=False)
    name_col = _pick_column(raw_df, ["restaurant_name", "name", "res_name"], required=True)
    city_col = _pick_column(
        raw_df,
        ["city", "listed_in(city)", "listed_in_city", "location_city"],
        required=True,
    )
    url_col = _pick_column(raw_df, ["url"], required=False)
    locality_col = _pick_column(raw_df, ["locality", "location", "address", "area"], required=False)
    cuisines_col = _pick_column(raw_df, ["cuisines", "cuisine"], required=False)
    cost_col = _pick_column(
        raw_df,
        ["average_cost_for_two", "avg_cost_for_two", "cost_for_two", "cost"],
        required=False,
    )
    if cost_col is None:
        cost_col = _pick_column(raw_df, ["approx_cost(for two people)"], required=False)
    rating_col = _pick_column(
        raw_df,
        ["aggregate_rating", "rating", "ratings", "rate"],
        required=False,
    )
    votes_col = _pick_column(raw_df, ["votes", "num_votes", "vote_count"], required=False)

    rows: list[dict[str, Any]] = []
    ingested_at = datetime.now(timezone.utc).isoformat()
    next_id = 1
    for _, row in raw_df.iterrows():
        name = _normalize_text(row[name_col])
        city = _city_from_url(row[url_col]) if url_col else None
        if not city:
            city = _normalize_text(row[city_col])
        if not name or not city:
            continue

        source_id = _normalize_text(row[id_col]) if id_col else None
        restaurant_id = source_id or f"gen-{next_id}"
        next_id += 1

        locality = _normalize_text(row[locality_col]) if locality_col else None
        cuisines = _parse_cuisines(row[cuisines_col]) if cuisines_col else []
        avg_cost_for_two = _parse_float(row[cost_col]) if cost_col else None
        rating = _parse_float(row[rating_col]) if rating_col else None
        votes = _parse_int(row[votes_col]) if votes_col else None
        tags = _derive_service_tags(name=name, cuisines=cuisines, locality=locality)

        rows.append(
            {
                "restaurant_id": restaurant_id,
                "name": name,
                "location_city": city.title(),
                "locality": locality.title() if locality else None,
                "cuisines": json.dumps(cuisines),
                "cuisines_text": ", ".join(cuisines),
                "avg_cost_for_two": avg_cost_for_two,
                "budget_band": _budget_band(avg_cost_for_two, thresholds),
                "rating": rating,
                "votes": votes,
                "service_tags": json.dumps(tags),
                "source_dataset": SOURCE_DATASET,
                "ingest_version": ingest_version,
                "ingested_at": ingested_at,
            }
        )

    canonical_df = dedupe_restaurants_by_business_key(pd.DataFrame(rows))
    return canonical_df


def build_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    total = len(df)
    required = ["restaurant_id", "name", "location_city"]
    required_non_null = df[required].notna().all(axis=1).sum() if total else 0
    completeness = (required_non_null / total * 100.0) if total else 0.0

    has_rating = "rating" in df and df["rating"].notna().any()
    if total:
        key_df = df.assign(
            _key_name=df["name"].fillna("").astype(str).str.strip().str.lower(),
            _key_city=df["location_city"].fillna("").astype(str).str.strip().str.lower(),
            _key_locality=(
                df["locality"].fillna("").astype(str).str.strip().str.lower()
                if "locality" in df
                else ""
            ),
        )
        unique_business_key = not key_df.duplicated(
            subset=["_key_name", "_key_city", "_key_locality"], keep=False
        ).any()
    else:
        unique_business_key = True

    return {
        "total_rows": total,
        "required_field_completeness_pct": round(completeness, 2),
        "null_counts": {
            "locality": int(df["locality"].isna().sum()) if "locality" in df else 0,
            "avg_cost_for_two": int(df["avg_cost_for_two"].isna().sum())
            if "avg_cost_for_two" in df
            else 0,
            "rating": int(df["rating"].isna().sum()) if "rating" in df else 0,
            "votes": int(df["votes"].isna().sum()) if "votes" in df else 0,
        },
        "budget_band_distribution": df["budget_band"].value_counts(dropna=False).to_dict()
        if "budget_band" in df
        else {},
        "rating_summary": {
            "min": float(df["rating"].min()) if has_rating else None,
            "max": float(df["rating"].max()) if has_rating else None,
            "mean": float(df["rating"].mean()) if has_rating else None,
        },
        "unique_business_key": bool(unique_business_key),
    }


def persist_to_sqlite(df: pd.DataFrame, sqlite_path: Path) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(sqlite_path) as conn:
        df.to_sql("restaurants_clean", conn, if_exists="replace", index=False)
        create_restaurants_indexes(conn)
        conn.commit()


def run_ingestion(output_db_path: Path, report_path: Path) -> dict[str, Any]:
    ingest_version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    raw_df = fetch_source_dataframe()
    canonical_df = normalize_restaurants(raw_df=raw_df, ingest_version=ingest_version)
    persist_to_sqlite(canonical_df, output_db_path)

    report = build_quality_report(canonical_df)
    report["source_dataset"] = SOURCE_DATASET
    report["ingest_version"] = ingest_version
    report["output_table"] = "restaurants_clean"
    report["output_db_path"] = str(output_db_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
