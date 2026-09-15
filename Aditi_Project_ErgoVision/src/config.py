"""ErgoVision Configuration Module.

Centralized configuration for Ergonomic Posture, Screen Distance,
and Ocular Fatigue monitoring.
Student Name: Aditi Prakash
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class PostureConfig:
    """Parameters for ergonomic posture & alignment detection."""
    # Thresholds for neck forward tilt and lateral head tilt (degrees)
    max_neck_tilt_deg: float = 22.0
    max_lateral_tilt_deg: float = 15.0

    # Consecutive frames with bad posture before triggering alert (~0.6s at 30 FPS)
    consec_bad_posture_frames: int = 18


@dataclass
class DistanceConfig:
    """Parameters for user-to-screen perspective distance estimation."""
    # Calibration baseline: expected inter-pupillary / face width ratio
    min_face_width_ratio: float = 0.18  # Too far
    max_face_width_ratio: float = 0.45  # Too close to screen (<45 cm)

    consec_too_close_frames: int = 20


@dataclass
class FatigueConfig:
    """Parameters for ocular blink rate and eye fatigue analysis."""
    ear_threshold: float = 0.22
    min_blink_rate_per_min: float = 10.0  # Normal is 15-20 blinks/min
    rolling_window_sec: float = 60.0


@dataclass
class ErgoAppConfig:
    """Master application configuration."""
    posture: PostureConfig = field(default_factory=PostureConfig)
    distance: DistanceConfig = field(default_factory=DistanceConfig)
    fatigue: FatigueConfig = field(default_factory=FatigueConfig)

    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    target_fps: int = 30
