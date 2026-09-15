"""Ocular Fatigue and Blink Rate Analysis for Screen Workers.

Monitors Eye Aspect Ratio (EAR), detects blinks, and computes
rolling blink rates to detect Computer Vision Syndrome (CVS).
"""

from typing import Dict, List, Optional
import time
import numpy as np

from src.config import FatigueConfig


def calculate_ear(eye_points: np.ndarray) -> float:
    """Calculates Soukupová and Čech Eye Aspect Ratio (EAR)."""
    if len(eye_points) != 6:
        return 0.0
    p1, p2, p3, p4, p5, p6 = eye_points[:, :2]
    d_v1 = np.linalg.norm(p2 - p6)
    d_v2 = np.linalg.norm(p3 - p5)
    d_h = np.linalg.norm(p1 - p4)
    if d_h < 1e-6:
        return 0.0
    return float((d_v1 + d_v2) / (2.0 * d_h))


class FatigueTracker:
    """Tracks blinks and alerts if user suffers from reduced blink frequency."""

    def __init__(self, config: Optional[FatigueConfig] = None):
        self.config = config or FatigueConfig()
        self.left_eye_indices = [33, 160, 158, 133, 153, 144]
        self.right_eye_indices = [362, 385, 387, 263, 373, 380]

        self.closed_frame_count = 0
        self.total_blinks = 0
        self.blink_timestamps: List[float] = []

    def reset(self):
        self.closed_frame_count = 0
        self.total_blinks = 0
        self.blink_timestamps.clear()

    def process_eyes(self, landmarks: Optional[np.ndarray]) -> Dict[str, any]:
        """Calculates EAR and updates rolling blink frequency."""
        now = time.time()

        if landmarks is None or len(landmarks) < 300:
            return {
                "ear": 0.0,
                "is_closed": False,
                "total_blinks": self.total_blinks,
                "blinks_per_min": 0.0,
                "fatigue_status": "NO_FACE",
            }

        left_pts = landmarks[self.left_eye_indices]
        right_pts = landmarks[self.right_eye_indices]
        ear_l = calculate_ear(left_pts)
        ear_r = calculate_ear(right_pts)
        avg_ear = (ear_l + ear_r) / 2.0

        is_closed = avg_ear < self.config.ear_threshold

        if is_closed:
            self.closed_frame_count += 1
        else:
            if 1 <= self.closed_frame_count <= 5:
                self.total_blinks += 1
                self.blink_timestamps.append(now)
            self.closed_frame_count = 0

        # Prune blink timestamps older than rolling window
        cutoff = now - self.config.rolling_window_sec
        self.blink_timestamps = [t for t in self.blink_timestamps if t >= cutoff]

        # Calculate blinks per minute
        blinks_per_min = (len(self.blink_timestamps) / (self.config.rolling_window_sec / 60.0))

        status = "NORMAL"
        if len(self.blink_timestamps) > 0 and blinks_per_min < self.config.min_blink_rate_per_min:
            status = "LOW BLINK RATE (DRY EYE RISK)"

        return {
            "ear": avg_ear,
            "is_closed": is_closed,
            "total_blinks": self.total_blinks,
            "blinks_per_min": blinks_per_min,
            "fatigue_status": status,
        }
