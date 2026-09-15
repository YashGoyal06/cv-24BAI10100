"""Ergonomic Posture, Alignment, and Neck Tilt Detection.

Uses 3D facial landmarks to calculate:
- Forward Neck Tilt (Slouch Angle)
- Lateral Head Tilt (Side Leaning)
- Ergonomic Posture Classification
"""

from typing import Dict, Optional, Tuple
import cv2
import numpy as np

from src.config import PostureConfig


class PostureDetector:
    """Estimates head and neck ergonomics using facial landmark geometry."""

    def __init__(self, config: Optional[PostureConfig] = None):
        self.config = config or PostureConfig()
        self.bad_posture_frames = 0
        self.total_slouch_events = 0
        self.is_slouching = False

    def reset(self):
        self.bad_posture_frames = 0
        self.total_slouch_events = 0
        self.is_slouching = False

    def analyze_posture(
        self, landmarks: Optional[np.ndarray], frame_shape: Tuple[int, int, int]
    ) -> Dict[str, any]:
        """Calculates neck tilt and lateral lean from landmarks.

        Args:
            landmarks: (N, 3) pixel landmark coordinates.
            frame_shape: (H, W, C)
        """
        if landmarks is None or len(landmarks) < 300:
            return {
                "neck_tilt_deg": 0.0,
                "lateral_tilt_deg": 0.0,
                "posture_status": "NO_FACE",
                "is_slouching": False,
                "slouch_events": self.total_slouch_events,
            }

        # Key landmark points:
        # Landmark 1: Nose tip
        # Landmark 152: Chin
        # Landmark 33: Left eye outer corner
        # Landmark 263: Right eye outer corner
        # Landmark 10: Forehead center
        nose = landmarks[1][:2]
        chin = landmarks[152][:2]
        forehead = landmarks[10][:2]
        left_eye = landmarks[33][:2]
        right_eye = landmarks[263][:2]

        # 1. Lateral Tilt: Angle between eye-line and horizontal axis
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        lateral_tilt_deg = float(np.degrees(np.arctan2(dy, dx)))

        # 2. Forward Head / Neck Tilt: Ratio of nose-to-chin vs forehead-to-nose projection
        # When user slouches/tilts head down, nose moves lower relative to eyes and chin distance compresses
        face_vertical = np.linalg.norm(chin - forehead)
        nose_to_chin = np.linalg.norm(chin - nose)
        tilt_ratio = (nose_to_chin / max(face_vertical, 1.0))

        # Standard upright calibrated baseline is ~0.45; tilting downward lowers ratio
        # Normalize to degrees:
        neck_tilt_deg = float(max(0.0, (0.46 - tilt_ratio) * 120.0))

        # Posture evaluation
        is_bad = (
            neck_tilt_deg > self.config.max_neck_tilt_deg
            or abs(lateral_tilt_deg) > self.config.max_lateral_tilt_deg
        )

        if is_bad:
            self.bad_posture_frames += 1
            if self.bad_posture_frames >= self.config.consec_bad_posture_frames:
                if not self.is_slouching:
                    self.total_slouch_events += 1
                self.is_slouching = True
        else:
            self.bad_posture_frames = 0
            self.is_slouching = False

        status = "GOOD"
        if self.is_slouching:
            if neck_tilt_deg > self.config.max_neck_tilt_deg:
                status = "SLOUCHING (FORWARD TILT)"
            else:
                status = "SLOUCHING (HEAD TILTED)"

        return {
            "neck_tilt_deg": neck_tilt_deg,
            "lateral_tilt_deg": lateral_tilt_deg,
            "posture_status": status,
            "is_slouching": self.is_slouching,
            "slouch_events": self.total_slouch_events,
        }
