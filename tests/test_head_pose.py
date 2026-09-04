"""Unit tests for HeadPoseEstimator and 3D SolvePnP."""

import numpy as np
import pytest

from src.config import HeadPoseConfig
from src.head_pose import HeadPoseEstimator


def test_head_pose_estimator_initialization():
    """Verify estimator loads model points properly."""
    estimator = HeadPoseEstimator()
    assert estimator.model_points_3d.shape == (6, 3)
    assert estimator.total_distraction_events == 0


def test_head_pose_none_landmarks():
    """Verify graceful handling when no landmarks are provided."""
    estimator = HeadPoseEstimator()
    result = estimator.estimate_pose(None, (480, 640, 3))
    assert result["direction"] == "FORWARD"
    assert result["is_distracted"] is False
    assert result["pitch"] == 0.0
    assert result["yaw"] == 0.0


def test_head_pose_synthetic_face():
    """Test pose estimation on canonical frontal face 2D projection."""
    estimator = HeadPoseEstimator()
    # Mock 468 landmarks with frontal alignment
    # indices: [1, 152, 33, 263, 61, 291]
    # Nose (320, 240), Chin (320, 350), Left Eye (220, 180), Right Eye (420, 180),
    # Left mouth (260, 300), Right mouth (380, 300)
    landmarks = np.zeros((468, 3))
    landmarks[1] = [320.0, 240.0, 0.0]
    landmarks[152] = [320.0, 350.0, 0.0]
    landmarks[33] = [220.0, 180.0, 0.0]
    landmarks[263] = [420.0, 180.0, 0.0]
    landmarks[61] = [260.0, 300.0, 0.0]
    landmarks[291] = [380.0, 300.0, 0.0]

    result = estimator.estimate_pose(landmarks, (480, 640, 3))
    assert "direction" in result
    assert "yaw" in result
    assert "pitch" in result
    assert "roll" in result
    assert result["nose_2d"] is not None
