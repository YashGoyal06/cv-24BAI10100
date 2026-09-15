"""User-to-Screen Distance and Proximity Estimation Module.

Uses perspective pinhole geometry and inter-ocular landmark distance
to detect if the user is sitting dangerously close to the monitor.
"""

from typing import Dict, Optional
import numpy as np

from src.config import DistanceConfig


class DistanceEstimator:
    """Estimates distance to screen using perspective inter-ocular distance."""

    def __init__(self, config: Optional[DistanceConfig] = None):
        self.config = config or DistanceConfig()
        self.too_close_frames = 0
        self.total_proximity_alerts = 0
        self.is_too_close = False

    def reset(self):
        self.too_close_frames = 0
        self.total_proximity_alerts = 0
        self.is_too_close = False

    def estimate_distance(
        self, landmarks: Optional[np.ndarray], frame_width: int
    ) -> Dict[str, any]:
        """Calculates relative distance and proximity status.

        Args:
            landmarks: (N, 3) pixel coordinates.
            frame_width: Width of image frame in pixels.
        """
        if landmarks is None or len(landmarks) < 300 or frame_width <= 0:
            return {
                "distance_ratio": 0.0,
                "estimated_distance_cm": 0.0,
                "proximity_status": "NO_FACE",
                "is_too_close": False,
                "proximity_alerts": self.total_proximity_alerts,
            }

        # MediaPipe landmark 234 (Left cheek edge) and 454 (Right cheek edge)
        # Or landmark 33 and 263 (Inter-ocular distance)
        p_left = landmarks[234][:2]
        p_right = landmarks[454][:2]
        face_width_px = float(np.linalg.norm(p_right - p_left))

        face_width_ratio = face_width_px / float(frame_width)

        # Approximate physical distance in cm using standard webcam focal length:
        # Distance = (Real_Face_Width_cm * Focal_px) / Face_Width_px
        # With standard webcam: 14cm adult face width * 600px focal ~ 8400 / px
        estimated_cm = max(20.0, min(120.0, 8400.0 / max(face_width_px, 1.0)))

        is_close = face_width_ratio > self.config.max_face_width_ratio

        if is_close:
            self.too_close_frames += 1
            if self.too_close_frames >= self.config.consec_too_close_frames:
                if not self.is_too_close:
                    self.total_proximity_alerts += 1
                self.is_too_close = True
        else:
            self.too_close_frames = 0
            self.is_too_close = False

        status = "OPTIMAL"
        if self.is_too_close:
            status = "TOO CLOSE (<45 cm)"
        elif face_width_ratio < self.config.min_face_width_ratio:
            status = "TOO FAR (>85 cm)"

        return {
            "distance_ratio": face_width_ratio,
            "estimated_distance_cm": estimated_cm,
            "proximity_status": status,
            "is_too_close": self.is_too_close,
            "proximity_alerts": self.total_proximity_alerts,
        }
