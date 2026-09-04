"""Unit tests for EyeDetector and Eye Aspect Ratio (EAR) mathematics."""

import numpy as np
import pytest

from src.config import EyeConfig
from src.eye_detector import EyeDetector
from src.utils import calculate_ear, euclidean_distance


def test_euclidean_distance_known_values():
    """Verify 2D Euclidean distance computation."""
    p1 = np.array([0.0, 0.0])
    p2 = np.array([3.0, 4.0])
    assert pytest.approx(euclidean_distance(p1, p2), 1e-4) == 5.0

    p3 = np.array([1.0, 1.0, 0.0])
    p4 = np.array([4.0, 5.0, 0.0])
    assert pytest.approx(euclidean_distance(p3, p4), 1e-4) == 5.0


def test_calculate_ear_open_eye():
    """Test EAR on synthetic wide-open eye landmarks."""
    # Build 6 landmarks:
    # p1 (0, 0), p4 (10, 0) -> horizontal width = 10
    # p2 (3, 4), p6 (3, -4) -> vertical 1 = 8
    # p3 (7, 4), p5 (7, -4) -> vertical 2 = 8
    # EAR = (8 + 8) / (2 * 10) = 16 / 20 = 0.80
    landmarks = np.zeros((10, 2))
    indices = [0, 1, 2, 3, 4, 5]
    landmarks[0] = [0.0, 0.0]    # p1
    landmarks[1] = [3.0, 4.0]    # p2
    landmarks[2] = [7.0, 4.0]    # p3
    landmarks[3] = [10.0, 0.0]   # p4
    landmarks[4] = [7.0, -4.0]   # p5
    landmarks[5] = [3.0, -4.0]   # p6

    ear = calculate_ear(landmarks, indices)
    assert pytest.approx(ear, 1e-4) == 0.80


def test_calculate_ear_closed_eye():
    """Test EAR on synthetic closed eye landmarks."""
    # p1 (0, 0), p4 (10, 0) -> width = 10
    # vertical points close to zero:
    landmarks = np.zeros((10, 2))
    indices = [0, 1, 2, 3, 4, 5]
    landmarks[0] = [0.0, 0.0]
    landmarks[1] = [3.0, 0.5]
    landmarks[2] = [7.0, 0.5]
    landmarks[3] = [10.0, 0.0]
    landmarks[4] = [7.0, -0.5]
    landmarks[5] = [3.0, -0.5]

    # v1 = 1.0, v2 = 1.0, h = 10.0 => EAR = 2.0 / 20.0 = 0.10
    ear = calculate_ear(landmarks, indices)
    assert pytest.approx(ear, 1e-4) == 0.10


def test_calculate_ear_invalid_input():
    """Verify ValueError is raised if indices length is not 6."""
    landmarks = np.zeros((10, 2))
    with pytest.raises(ValueError):
        calculate_ear(landmarks, [0, 1, 2])


def test_eye_detector_blink_and_prolonged_closure():
    """Test EyeDetector state transitions for blinks and prolonged closure."""
    cfg = EyeConfig(
        ear_threshold=0.22,
        blink_consec_frames_min=1,
        blink_consec_frames_max=3,
        eye_closed_consec_frames=5,
    )
    detector = EyeDetector(cfg)

    # Synthetic open eye landmarks (468 points)
    open_landmarks = np.zeros((468, 3))
    for i in range(468):
        open_landmarks[i] = [float(i), float(i), 0.0]

    # Configure specific eye points to give open eye
    # Left eye: [33, 160, 158, 133, 153, 144]
    open_landmarks[33] = [0.0, 0.0, 0.0]
    open_landmarks[160] = [3.0, 3.0, 0.0]
    open_landmarks[158] = [7.0, 3.0, 0.0]
    open_landmarks[133] = [10.0, 0.0, 0.0]
    open_landmarks[153] = [7.0, -3.0, 0.0]
    open_landmarks[144] = [3.0, -3.0, 0.0]

    # Right eye: [362, 385, 387, 263, 373, 380]
    open_landmarks[362] = [0.0, 0.0, 0.0]
    open_landmarks[385] = [3.0, 3.0, 0.0]
    open_landmarks[387] = [7.0, 3.0, 0.0]
    open_landmarks[263] = [10.0, 0.0, 0.0]
    open_landmarks[373] = [7.0, -3.0, 0.0]
    open_landmarks[380] = [3.0, -3.0, 0.0]

    # Closed eye landmarks (collapsed vertical aperture)
    closed_landmarks = open_landmarks.copy()
    closed_landmarks[160] = [3.0, 0.2, 0.0]
    closed_landmarks[158] = [7.0, 0.2, 0.0]
    closed_landmarks[153] = [7.0, -0.2, 0.0]
    closed_landmarks[144] = [3.0, -0.2, 0.0]
    closed_landmarks[385] = [3.0, 0.2, 0.0]
    closed_landmarks[387] = [7.0, 0.2, 0.0]
    closed_landmarks[373] = [7.0, -0.2, 0.0]
    closed_landmarks[380] = [3.0, -0.2, 0.0]

    # Process 1 open frame
    res = detector.process_eyes(open_landmarks)
    assert not res["is_eye_closed"]
    assert res["total_blinks"] == 0

    # Simulate 2 frames closed (normal blink)
    detector.process_eyes(closed_landmarks)
    detector.process_eyes(closed_landmarks)
    # Re-open eye
    res = detector.process_eyes(open_landmarks)
    assert res["total_blinks"] == 1
    assert not res["is_prolonged_closure"]

    # Simulate 6 consecutive closed frames (exceeds threshold 5)
    for _ in range(6):
        res = detector.process_eyes(closed_landmarks)

    assert res["is_prolonged_closure"] is True
    assert res["prolonged_events"] == 1
