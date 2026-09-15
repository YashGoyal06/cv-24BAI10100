"""Unit Tests for ErgoVision.
Student Name: Aditi Prakash
"""

import numpy as np
import pytest

from src.posture_detector import PostureDetector
from src.distance_estimator import DistanceEstimator
from src.fatigue_tracker import FatigueTracker, calculate_ear
from src.analytics import ErgoAnalytics


def test_calculate_ear_standard():
    eye_open = np.array([
        [0.0, 0.0],
        [5.0, 5.0],
        [10.0, 5.0],
        [15.0, 0.0],
        [10.0, -5.0],
        [5.0, -5.0],
    ])
    ear = calculate_ear(eye_open)
    assert ear > 0.25


def test_posture_detector_good():
    detector = PostureDetector()
    landmarks = np.zeros((468, 3))
    landmarks[1] = [320, 260, 0]    # Nose
    landmarks[152] = [320, 360, 0]  # Chin
    landmarks[10] = [320, 160, 0]   # Forehead
    landmarks[33] = [280, 240, 0]   # Left eye
    landmarks[263] = [360, 240, 0]  # Right eye

    res = detector.analyze_posture(landmarks, (480, 640, 3))
    assert res["is_slouching"] is False
    assert res["posture_status"] == "GOOD"


def test_distance_estimator():
    estimator = DistanceEstimator()
    landmarks = np.zeros((468, 3))
    # Close distance
    landmarks[234] = [100, 240, 0]
    landmarks[454] = [540, 240, 0]

    res = estimator.estimate_distance(landmarks, 640)
    assert res["distance_ratio"] > 0.45


def test_analytics_summary():
    analytics = ErgoAnalytics()
    analytics.start_session()
    analytics.update("GOOD", False, False, 0.32, 2)
    analytics.update("GOOD", False, False, 0.31, 2)
    analytics.end_session()

    summary = analytics.get_summary()
    assert summary["total_frames"] == 2
    assert summary["good_posture_pct"] == 100.0
