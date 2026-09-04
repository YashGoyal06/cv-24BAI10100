"""Unit tests for RiskEngine multi-cue state aggregation."""

import pytest

from src.config import RiskEngineConfig
from src.risk_engine import RiskEngine


def test_risk_engine_safe_baseline():
    """Verify default state is SAFE when inputs are nominal."""
    engine = RiskEngine()
    eye_data = {"is_prolonged_closure": False, "closed_frames": 0, "is_eye_closed": False}
    yawn_data = {"is_yawning": False, "is_mouth_open": False}
    pose_data = {"is_distracted": False, "direction": "FORWARD"}

    result = engine.assess_risk(eye_data, yawn_data, pose_data, face_detected=True)
    assert result["state"] == "SAFE"
    assert result["risk_score"] < 20.0


def test_risk_engine_drowsy_transition():
    """Verify transition to DROWSY when prolonged eye closure occurs."""
    engine = RiskEngine()
    eye_data = {"is_prolonged_closure": True, "closed_frames": 20, "is_eye_closed": True}
    yawn_data = {"is_yawning": False, "is_mouth_open": False}
    pose_data = {"is_distracted": False, "direction": "FORWARD"}

    result = engine.assess_risk(eye_data, yawn_data, pose_data, face_detected=True)
    assert result["state"] == "DROWSY"
    assert result["instant_score"] >= 40.0


def test_risk_engine_distracted_transition():
    """Verify transition to DISTRACTED when head turned away."""
    engine = RiskEngine()
    eye_data = {"is_prolonged_closure": False, "closed_frames": 0, "is_eye_closed": False}
    yawn_data = {"is_yawning": False, "is_mouth_open": False}
    pose_data = {"is_distracted": True, "direction": "RIGHT"}

    result = engine.assess_risk(eye_data, yawn_data, pose_data, face_detected=True)
    assert result["state"] == "DISTRACTED"


def test_risk_engine_high_risk_compound():
    """Verify transition to HIGH RISK when both eye closed and distracted."""
    engine = RiskEngine()
    eye_data = {"is_prolonged_closure": True, "closed_frames": 25, "is_eye_closed": True}
    yawn_data = {"is_yawning": False, "is_mouth_open": False}
    pose_data = {"is_distracted": True, "direction": "RIGHT"}

    result = engine.assess_risk(eye_data, yawn_data, pose_data, face_detected=True)
    assert result["state"] == "HIGH RISK"
    assert result["is_high_risk"] is True


def test_risk_engine_no_face_handling():
    """Verify graceful handling when face disappears from camera."""
    engine = RiskEngine()
    result = engine.assess_risk({}, {}, {}, face_detected=False)
    assert result["state"] == "NO FACE"
    assert not result["is_high_risk"]
