"""Disposable PostgreSQL integration checks; enabled in CI via RUN_POSTGRES_TESTS=1."""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from src.database.schema_manager import apply_migrations

pytestmark = pytest.mark.skipif(os.getenv("RUN_POSTGRES_TESTS") != "1", reason="requires disposable PostgreSQL")

@pytest.fixture(scope="module")
def integration_engine():
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.begin() as connection:
        apply_migrations(connection)
    yield engine
    engine.dispose()

def test_migration_and_fact_grain_are_available(integration_engine):
    with integration_engine.connect() as connection:
        assert connection.execute(text("SELECT to_regclass('analytics.dim_date')")).scalar() == "analytics.dim_date"
        assert connection.execute(text("SELECT COUNT(*) FROM analytics.schema_migrations")).scalar() >= 1

def test_postgres_accepts_parameterized_metric_query(integration_engine):
    with integration_engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE analytics.fact_orders"))
        connection.execute(text("INSERT INTO analytics.fact_orders(order_id, customer_id, order_status) VALUES ('order-1', 'customer-1', 'delivered')"))
        delivered = connection.execute(text("SELECT COUNT(*) FROM analytics.fact_orders WHERE order_status = :status"), {"status": "delivered"}).scalar()
    assert delivered == 1
