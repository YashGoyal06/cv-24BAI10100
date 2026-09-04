"""Unit tests for SessionAnalytics module and CSV/JSON persistence."""

import os
import tempfile
import pytest

from src.analytics import SessionAnalytics


def test_session_analytics_metrics_accumulation():
    """Verify accumulation of frame telemetry and state counts."""
    analytics = SessionAnalytics()
    analytics.start_session()

    # Simulate 10 frames: 6 SAFE, 2 CAUTION, 2 DROWSY
    for _ in range(6):
        analytics.update(
            state="SAFE",
            risk_score=10.0,
            ear=0.32,
            mar=0.20,
            blinks=2,
            yawns=0,
            prolonged_closures=0,
            distractions=0,
        )

    for _ in range(2):
        analytics.update(
            state="CAUTION",
            risk_score=35.0,
            ear=0.25,
            mar=0.55,
            blinks=3,
            yawns=1,
            prolonged_closures=0,
            distractions=0,
        )

    for _ in range(2):
        analytics.update(
            state="DROWSY",
            risk_score=65.0,
            ear=0.15,
            mar=0.20,
            blinks=4,
            yawns=1,
            prolonged_closures=1,
            distractions=0,
        )

    analytics.end_session()
    summary = analytics.get_summary()

    assert summary["total_frames_processed"] == 10
    assert summary["safe_time_percentage"] == 60.0
    assert summary["drowsy_time_percentage"] == 20.0
    assert summary["total_blinks"] == 4
    assert summary["total_yawns"] == 1
    assert summary["prolonged_closure_events"] == 1
    assert summary["peak_risk_score"] == 65.0


def test_session_analytics_exports():
    """Verify CSV and JSON file exports."""
    analytics = SessionAnalytics()
    analytics.start_session()
    analytics.update("SAFE", 10.0, 0.30, 0.20, 1, 0, 0, 0)
    analytics.end_session()

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "session.csv")
        json_path = os.path.join(tmpdir, "session.json")

        analytics.export_csv(csv_path)
        analytics.export_json(json_path)

        assert os.path.exists(csv_path)
        assert os.path.exists(json_path)
        assert os.path.getsize(csv_path) > 0
        assert os.path.getsize(json_path) > 0
