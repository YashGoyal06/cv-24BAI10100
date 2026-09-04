"""Unit tests for YawnDetector and Mouth Aspect Ratio (MAR) calculations."""

import numpy as np
import pytest

from src.config import YawnConfig
from src.utils import calculate_mar
from src.yawn_detector import YawnDetector


def test_calculate_mar():
    """Verify MAR formula computation."""
    landmarks = np.zeros((10, 2))
    # Indices: [left, right, top, bottom, mid_top, mid_bottom]
    # left (0, 0), right (10, 0) => h = 10
    # top (5, 4), bottom (5, -4) => v1 = 8
    # mid_top (5, 4), mid_bot (5, -4) => v2 = 8
    # MAR = (8 + 8) / (2 * 10) = 16 / 20 = 0.80
    indices = [0, 1, 2, 3, 4, 5]
    landmarks[0] = [0.0, 0.0]
    landmarks[1] = [10.0, 0.0]
    landmarks[2] = [5.0, 4.0]
    landmarks[3] = [5.0, -4.0]
    landmarks[4] = [5.0, 4.0]
    landmarks[5] = [5.0, -4.0]

    mar = calculate_mar(landmarks, indices)
    assert pytest.approx(mar, 1e-4) == 0.80


def test_yawn_detector_temporal_logic():
    """Verify temporal smoothing distinguishes yawn from speech."""
    cfg = YawnConfig(
        mar_threshold=0.60,
        yawn_consec_frames=4,
        yawn_cooldown_frames=5,
    )
    detector = YawnDetector(cfg)

    # Base landmarks
    closed_mouth = np.zeros((468, 3))
    # mouth indices: [61, 291, 0, 17, 13, 14]
    closed_mouth[61] = [0.0, 0.0, 0.0]
    closed_mouth[291] = [10.0, 0.0, 0.0]
    closed_mouth[0] = [5.0, 1.0, 0.0]
    closed_mouth[17] = [5.0, -1.0, 0.0]
    closed_mouth[13] = [5.0, 0.5, 0.0]
    closed_mouth[14] = [5.0, -0.5, 0.0]

    # Open mouth (yawn)
    open_mouth = closed_mouth.copy()
    open_mouth[0] = [5.0, 4.0, 0.0]
    open_mouth[17] = [5.0, -4.0, 0.0]
    open_mouth[13] = [5.0, 4.0, 0.0]
    open_mouth[14] = [5.0, -4.0, 0.0]

    # 1. Closed mouth
    res = detector.process_mouth(closed_mouth)
    assert not res["is_mouth_open"]
    assert not res["is_yawning"]

    # 2. Brief opening (speech: 2 frames)
    detector.process_mouth(open_mouth)
    detector.process_mouth(open_mouth)
    detector.process_mouth(closed_mouth)
    assert detector.total_yawns == 0

    # 3. Sustained opening (yawn: 4+ frames)
    for _ in range(4):
        res = detector.process_mouth(open_mouth)

    assert res["is_yawning"] is True
    assert detector.total_yawns == 1
