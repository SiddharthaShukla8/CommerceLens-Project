from pathlib import Path
import pytest
from src.ingestion.reader import missing_sources
from src.utils.run_lock import exclusive_lock

def test_missing_source_lists_all_required_files(tmp_path: Path):
    missing = missing_sources(tmp_path)
    assert len(missing) == 9

def test_etl_lock_rejects_concurrent_run(tmp_path: Path):
    lock_path = tmp_path / "pipeline.lock"
    with exclusive_lock(lock_path):
        with pytest.raises(RuntimeError, match="already in progress"):
            with exclusive_lock(lock_path):
                pass
