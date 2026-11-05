"""Prevent concurrent ETL runs from writing the same exports or tables."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import fcntl

@contextmanager
def exclusive_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise RuntimeError("Another CommerceLens ETL run is already in progress.") from exc
    try:
        yield
    finally:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()
