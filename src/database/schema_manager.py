"""Apply additive, tracked SQL migrations without resetting user data."""
from __future__ import annotations

from pathlib import Path
from sqlalchemy import Connection, text
from config.settings import ROOT

MIGRATIONS_DIR = ROOT / "database" / "migrations"
BASE_SCHEMA_FILES = ("schema.sql", "indexes.sql", "views.sql")

def apply_migrations(connection: Connection) -> list[str]:
    for filename in BASE_SCHEMA_FILES:
        schema_file = ROOT / "database" / filename
        connection.execute(text(schema_file.read_text()))
    connection.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
    connection.execute(text("CREATE TABLE IF NOT EXISTS analytics.schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"))
    applied = {row[0] for row in connection.execute(text("SELECT version FROM analytics.schema_migrations"))}
    completed: list[str] = []
    for migration in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if migration.name in applied:
            continue
        connection.execute(text(migration.read_text()))
        connection.execute(text("INSERT INTO analytics.schema_migrations(version) VALUES (:version)"), {"version": migration.name})
        completed.append(migration.name)
    return completed
