"""Automated Streamlit AppTest tests for global filter persistence and behavior across pages.

Uses deterministic fixture mode (COMMERCELENS_TEST_MODE=1) to ensure tests run reliably
and independently of production databases, credentials, or external CSV exports.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

# Ensure test mode is active for all tests in this module
os.environ["COMMERCELENS_TEST_MODE"] = "1"

APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")

PAGES = [
    "Executive overview",
    "Sales & products",
    "Customer intelligence",
    "Operations & delivery",
    "Geographical analytics",
    "Experiment analytics",
    "Data quality",
]


def _get_widgets(at: AppTest):
    """Retrieve shared sidebar widgets deterministically via stable keys and fallback positions."""
    # Navigation
    nav = at.sidebar.radio(key="dashboard_page") if at.sidebar.radio(key="dashboard_page") else at.sidebar.radio[0]
    # Date range
    date_w = at.sidebar.date_input(key="global_date_range") if at.sidebar.date_input(key="global_date_range") else at.sidebar.date_input[0]
    # Customer states
    states_w = at.sidebar.multiselect(key="global_customer_states") if at.sidebar.multiselect(key="global_customer_states") else at.sidebar.multiselect[0]
    # Order statuses
    status_w = at.sidebar.multiselect(key="global_order_statuses") if at.sidebar.multiselect(key="global_order_statuses") else at.sidebar.multiselect[1]
    # Reset button
    btn_w = at.sidebar.button[0]
    return nav, date_w, states_w, status_w, btn_w


def test_filter_persistence_full_navigation_sequence():
    """Verify the exact 20-step sequence requested for filter persistence across all seven pages."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # 1. Open Executive Overview
    assert nav.value == "Executive overview"
    initial_default_range = date_w.value
    assert isinstance(initial_default_range, tuple) and len(initial_default_range) == 2

    # 2. Select non-default purchase date range (e.g. 2017-09-01 to 2017-09-04)
    target_date_range = (datetime.date(2017, 9, 1), datetime.date(2017, 9, 4))
    date_w.set_value(target_date_range).run()
    assert not at.exception

    # Re-fetch widget references after rerun
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # 3. Select customer states AM and SC
    states_w.select("AM").select("SC").run()
    assert not at.exception
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # 4. Select multiple order statuses (delivered, shipped)
    status_w.select("delivered").select("shipped").run()
    assert not at.exception
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # 5-16. Navigate across all seven pages and verify selections remain unchanged
    for page in PAGES[1:]:
        nav.set_value(page).run()
        assert not at.exception, f"Exception occurred on page {page}"
        nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
        assert date_w.value == target_date_range, f"Date range lost on {page}"
        assert set(states_w.value) == {"AM", "SC"}, f"States lost on {page}"
        assert set(status_w.value) == {"delivered", "shipped"}, f"Statuses lost on {page}"

    # 17-18. Return to Executive overview and verify filters are still selected
    nav.set_value("Executive overview").run()
    assert not at.exception
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert date_w.value == target_date_range
    assert set(states_w.value) == {"AM", "SC"}
    assert set(status_w.value) == {"delivered", "shipped"}

    # 19. Click Reset filters
    btn_w.click().run()
    assert not at.exception
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # 20. Verify date range returns to default and state/status selections are cleared
    assert date_w.value == initial_default_range
    assert states_w.value == []
    assert status_w.value == []


def test_repeated_navigation_and_reruns():
    """Verify filters withstand repeated page switches and script reruns."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    target_date_range = (datetime.date(2017, 9, 1), datetime.date(2017, 9, 3))
    date_w.set_value(target_date_range).run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    states_w.select("SP").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    status_w.select("delivered").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # Repeat navigating back and forth multiple times with re-runs
    for _ in range(2):
        nav.set_value("Experiment analytics").run()
        at.run()  # simulate extra rerun on page
        nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
        assert date_w.value == target_date_range
        assert states_w.value == ["SP"]
        assert status_w.value == ["delivered"]

        nav.set_value("Data quality").run()
        at.run()
        nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
        assert date_w.value == target_date_range
        assert states_w.value == ["SP"]
        assert status_w.value == ["delivered"]

        nav.set_value("Sales & products").run()
        nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
        assert date_w.value == target_date_range
        assert states_w.value == ["SP"]
        assert status_w.value == ["delivered"]


def test_empty_and_single_and_multiple_filter_selections():
    """Verify single state, multiple states, empty states, and status variations."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)

    # Single state
    states_w.select("RJ").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert states_w.value == ["RJ"]

    # Multiple states
    states_w.select("PR").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert set(states_w.value) == {"RJ", "PR"}

    # Navigate to Geographical analytics
    nav.set_value("Geographical analytics").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert set(states_w.value) == {"RJ", "PR"}

    # Deselect one state
    states_w.unselect("PR").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert states_w.value == ["RJ"]

    # Deselect all
    states_w.unselect("RJ").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert states_w.value == []


def test_reset_from_different_pages():
    """Verify that Reset filters works properly when clicked from different pages."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    initial_default_range = date_w.value

    # Select filters
    states_w.select("PR").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    nav.set_value("Experiment analytics").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert states_w.value == ["PR"]

    # Click Reset on Experiment analytics
    btn_w.click().run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert date_w.value == initial_default_range
    assert states_w.value == []
    assert status_w.value == []

    # Select again and reset from Data quality
    states_w.select("BA").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    nav.set_value("Data quality").run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert states_w.value == ["BA"]

    btn_w.click().run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    assert states_w.value == []


def test_all_seven_pages_render_without_error():
    """Verify that all seven dashboard pages render completely without any uncaught exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
    for page in PAGES:
        nav.set_value(page).run()
        assert not at.exception, f"Render error on page {page}: {at.exception}"
        nav, date_w, states_w, status_w, btn_w = _get_widgets(at)
