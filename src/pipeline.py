"""Orchestrates validation, cleaning, exports, and optional database loading."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from time import perf_counter
import pandas as pd
from config.settings import RAW_DIR, PROCESSED_DIR, EXPORT_DIR
from src.ingestion.reader import read_sources
from src.cleaning.cleaner import clean_sources
from src.validation.quality import validate
from src.analytics.mart import build_order_mart
from src.analytics.rfm import build_rfm
from src.analytics.cohort import build_cohorts
from src.database.loader import load_to_postgres
from src.utils.run_lock import exclusive_lock

def run(validate_only: bool = False, database: bool = False) -> dict:
    started_at, timer = datetime.now(timezone.utc), perf_counter()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with exclusive_lock(EXPORT_DIR / ".etl.lock"):
        try:
            frames = read_sources(RAW_DIR)
            clean, audit = clean_sources(frames)
            quality = validate(clean)
            if validate_only:
                return {"quality": quality, "audit": audit}
            mart = build_order_mart(clean)
            rfm, cohorts = build_rfm(mart), build_cohorts(mart)
            if database:
                load_to_postgres(clean, mart)
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            for name, frame in clean.items():
                frame.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)
            mart.to_csv(EXPORT_DIR / "order_mart.csv", index=False)
            rfm.to_csv(EXPORT_DIR / "rfm_segments.csv", index=False)
            cohorts.to_csv(EXPORT_DIR / "cohort_retention.csv", index=False)
            audit.to_csv(EXPORT_DIR / "cleaning_audit.csv", index=False)
            quality.to_csv(EXPORT_DIR / "data_quality.csv", index=False)
            metadata = {"status": "SUCCESS", "started_at": started_at.isoformat(), "last_successful_etl": datetime.now(timezone.utc).isoformat(), "duration_seconds": round(perf_counter() - timer, 2), "source_rows": {k: len(v) for k,v in frames.items()}, "cleaned_rows": {k: len(v) for k,v in clean.items()}, "quality_statuses": quality.status.value_counts().to_dict(), "database_loaded": database}
            (EXPORT_DIR / "pipeline_metadata.json").write_text(json.dumps(metadata, indent=2))
            return {"quality": quality, "audit": audit, "mart": mart, "rfm": rfm, "cohorts": cohorts}
        except Exception as exc:
            failure = {"status": "FAILED", "started_at": started_at.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(), "duration_seconds": round(perf_counter() - timer, 2), "error_type": type(exc).__name__}
            (EXPORT_DIR / "pipeline_last_failure.json").write_text(json.dumps(failure, indent=2))
            raise
