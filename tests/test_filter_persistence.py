"""Automated Streamlit AppTest tests for global filter persistence and behavior across pages."""
from __future__ import annotations

import datetime
from pathlib import Path
from streamlit.testing.v1 import AppTest

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


def test_filter_persistence_full_navigation_sequence():
    """Verify the exact 20-step sequence requested for filter persistence across all seven pages."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    # 1. Open Executive Overview
    assert at.sidebar.radio[0].value == "Executive overview"
    default_min = at.session_state["_default_min_date"]
    default_max = at.session_state["_default_max_date"]

    # 2. Select non-default purchase date range (e.g. 2017-09-01 to 2017-09-04)
    target_date_range = (datetime.date(2017, 9, 1), datetime.date(2017, 9, 4))
    at.sidebar.date_input[0].set_value(target_date_range).run()
    assert not at.exception

    # 3. Select customer states AM and SC
    at.sidebar.multiselect[0].select("AM").select("SC").run()
    assert not at.exception

    # 4. Select multiple order statuses (e.g. delivered, shipped)
    at.sidebar.multiselect[1].select("delivered").select("shipped").run()
    assert not at.exception

    # 5-16. Navigate across all pages and verify selections remain unchanged
    for page in PAGES[1:]:  # Sales & products, Customer intelligence, Operations & delivery, Geographical analytics, Experiment analytics, Data quality
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, f"Exception occurred on page {page}"
        assert at.sidebar.date_input[0].value == target_date_range, f"Date range lost on {page}"
        assert set(at.sidebar.multiselect[0].value) == {"AM", "SC"}, f"States lost on {page}"
        assert set(at.sidebar.multiselect[1].value) == {"delivered", "shipped"}, f"Statuses lost on {page}"

    # 17-18. Return to Executive overview and verify filters are still selected
    at.sidebar.radio[0].set_value("Executive overview").run()
    assert not at.exception
    assert at.sidebar.date_input[0].value == target_date_range
    assert set(at.sidebar.multiselect[0].value) == {"AM", "SC"}
    assert set(at.sidebar.multiselect[1].value) == {"delivered", "shipped"}

    # 19. Click Reset filters
    at.sidebar.button[0].click().run()
    assert not at.exception

    # 20. Verify date range returns to default and state/status selections are cleared
    assert at.sidebar.date_input[0].value == (default_min, default_max)
    assert at.sidebar.multiselect[0].value == []
    assert at.sidebar.multiselect[1].value == []


def test_repeated_navigation_and_reruns():
    """Verify filters withstand repeated page switches and script reruns."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    target_date_range = (datetime.date(2017, 6, 1), datetime.date(2017, 8, 31))
    at.sidebar.date_input[0].set_value(target_date_range).run()
    at.sidebar.multiselect[0].select("SP").run()
    at.sidebar.multiselect[1].select("delivered").run()

    # Repeat navigating back and forth multiple times with re-runs
    for _ in range(2):
        at.sidebar.radio[0].set_value("Experiment analytics").run()
        at.run()  # simulate extra rerun on page
        assert at.sidebar.date_input[0].value == target_date_range
        assert at.sidebar.multiselect[0].value == ["SP"]
        assert at.sidebar.multiselect[1].value == ["delivered"]

        at.sidebar.radio[0].set_value("Data quality").run()
        at.run()
        assert at.sidebar.date_input[0].value == target_date_range
        assert at.sidebar.multiselect[0].value == ["SP"]
        assert at.sidebar.multiselect[1].value == ["delivered"]

        at.sidebar.radio[0].set_value("Sales & products").run()
        assert at.sidebar.date_input[0].value == target_date_range
        assert at.sidebar.multiselect[0].value == ["SP"]
        assert at.sidebar.multiselect[1].value == ["delivered"]


def test_empty_and_single_and_multiple_filter_selections():
    """Verify single state, multiple states, empty states, and status variations."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    # Single state
    at.sidebar.multiselect[0].select("RJ").run()
    assert at.sidebar.multiselect[0].value == ["RJ"]

    # Multiple states
    at.sidebar.multiselect[0].select("MG").run()
    assert set(at.sidebar.multiselect[0].value) == {"RJ", "MG"}

    # Navigate to Geographical analytics
    at.sidebar.radio[0].set_value("Geographical analytics").run()
    assert set(at.sidebar.multiselect[0].value) == {"RJ", "MG"}

    # Deselect one state
    at.sidebar.multiselect[0].unselect("MG").run()
    assert at.sidebar.multiselect[0].value == ["RJ"]

    # Deselect all
    at.sidebar.multiselect[0].unselect("RJ").run()
    assert at.sidebar.multiselect[0].value == []


def test_reset_from_different_pages():
    """Verify that Reset filters works properly when clicked from different pages."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    default_min = at.session_state["_default_min_date"]
    default_max = at.session_state["_default_max_date"]

    # Select filters
    at.sidebar.multiselect[0].select("PR").run()
    at.sidebar.radio[0].set_value("Experiment analytics").run()
    assert at.sidebar.multiselect[0].value == ["PR"]

    # Click Reset on Experiment analytics
    at.sidebar.button[0].click().run()
    assert at.sidebar.date_input[0].value == (default_min, default_max)
    assert at.sidebar.multiselect[0].value == []
    assert at.sidebar.multiselect[1].value == []

    # Select again and reset from Data quality
    at.sidebar.multiselect[0].select("BA").run()
    at.sidebar.radio[0].set_value("Data quality").run()
    assert at.sidebar.multiselect[0].value == ["BA"]

    at.sidebar.button[0].click().run()
    assert at.sidebar.multiselect[0].value == []


def test_all_seven_pages_render_without_error():
    """Verify that all seven dashboard pages render completely without any uncaught exceptions."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    for page in PAGES:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, f"Render error on page {page}: {at.exception}"
