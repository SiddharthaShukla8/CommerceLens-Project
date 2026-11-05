"""Orchestrates validation, cleaning, exports, and optional database loading."""
from __future__ import annotations
import json
from datetime import datetime, timezone
import pandas as pd
from config.settings import RAW_DIR, PROCESSED_DIR, EXPORT_DIR
from src.ingestion.reader import read_sources
from src.cleaning.cleaner import clean_sources
from src.validation.quality import validate
from src.analytics.mart import build_order_mart
from src.analytics.rfm import build_rfm
from src.analytics.cohort import build_cohorts
from src.database.loader import load_to_postgres

def run(validate_only: bool = False, database: bool = False) -> dict:
    frames = read_sources(RAW_DIR)
    clean, audit = clean_sources(frames)
    quality = validate(clean)
    if validate_only:
        return {"quality": quality, "audit": audit}
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True); EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in clean.items(): frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
    mart = build_order_mart(clean); rfm = build_rfm(mart); cohorts = build_cohorts(mart)
    mart.to_csv(EXPORT_DIR / "order_mart.csv", index=False); rfm.to_csv(EXPORT_DIR / "rfm_segments.csv", index=False); cohorts.to_csv(EXPORT_DIR / "cohort_retention.csv", index=False)
    audit.to_csv(EXPORT_DIR / "cleaning_audit.csv", index=False); quality.to_csv(EXPORT_DIR / "data_quality.csv", index=False)
    metadata = {"last_successful_etl": datetime.now(timezone.utc).isoformat(), "source_rows": {k: len(v) for k,v in frames.items()}, "quality_statuses": quality.status.value_counts().to_dict()}
    (EXPORT_DIR / "pipeline_metadata.json").write_text(json.dumps(metadata, indent=2))
    if database: load_to_postgres(clean, mart)
    return {"quality": quality, "audit": audit, "mart": mart, "rfm": rfm, "cohorts": cohorts}
