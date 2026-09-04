"""VisionGuard Configuration Module.

Centralized configuration for Computer Vision thresholds, landmark indices,
temporal windows, risk assessment weights, and UI display settings.
All magic numbers are eliminated and documented mathematically.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class EyeConfig:
    """Parameters for Eye Aspect Ratio (EAR) and blink analysis."""

    # Default EAR threshold below which the eye is considered closed
    # Soukupová and Čech (2016): typical open eye EAR is 0.28-0.38, closed is < 0.20
    ear_threshold: float = 0.22

    # Number of consecutive frames the eye must be closed to count as a deliberate blink
    blink_consec_frames_min: int = 1
    blink_consec_frames_max: int = 4

    # Number of consecutive frames with closed eyes to trigger a prolonged closure alert
    # At ~30 FPS, 15 frames corresponds to ~0.5 seconds of sustained closure
    eye_closed_consec_frames: int = 15

    # Rolling window (in seconds) over which blink frequency is computed
    blink_window_seconds: float = 60.0

    # MediaPipe FaceMesh Landmark Indices for Left and Right Eyes
    # Standard 6-point formulation per eye: [p1, p2, p3, p4, p5, p6]
    # p1: Outer corner, p4: Inner corner, p2/p6: Upper/Lower lateral, p3/p5: Upper/Lower medial
    left_eye_indices: List[int] = field(
        default_factory=lambda: [33, 160, 158, 133, 153, 144]
    )
    right_eye_indices: List[int] = field(
        default_factory=lambda: [362, 385, 387, 263, 373, 380]
    )


@dataclass
class YawnConfig:
    """Parameters for Mouth Aspect Ratio (MAR) and yawning analysis."""

    # Default MAR threshold above which mouth is considered open
    # Typical resting MAR is 0.15-0.30; yawning reaches 0.60-0.90
    mar_threshold: float = 0.60

    # Number of consecutive frames the mouth must stay open to distinguish
    # an involuntary yawn from normal speech or laughter (~15 frames ≈ 0.5s at 30 FPS)
    yawn_consec_frames: int = 15

    # Minimum cooldown frames before recording another distinct yawn event
    yawn_cooldown_frames: int = 60

    # MediaPipe FaceMesh landmark indices for mouth aperture measurement
    # Outer/inner corners and upper/lower vermilion borders
    # [left_corner, right_corner, upper_lip_top, lower_lip_bottom, upper_lip_mid, lower_lip_mid]
    mouth_indices: List[int] = field(
        default_factory=lambda: [61, 291, 0, 17, 13, 14]
    )


@dataclass
class HeadPoseConfig:
    """Parameters for 3D Head Pose Estimation via SolvePnP."""

    # Yaw angle threshold (degrees) beyond which head is turned left or right
    yaw_threshold: float = 25.0

    # Pitch angle threshold (degrees) beyond which head is tilted up or down
    pitch_threshold: float = 20.0

    # Number of consecutive frames in non-forward pose to trigger distraction alert
    # 20 frames ≈ 0.67s of looking away from the road
    distraction_consec_frames: int = 20

    # Canonical 3D facial model keypoint coordinates (in millimeters, origin at nose bridge)
    # Reference: anthropometric 3D facial model
    model_points_3d: List[Tuple[float, float, float]] = field(
        default_factory=lambda: [
            (0.0, 0.0, 0.0),          # Nose tip (landmark 1)
            (0.0, -330.0, -65.0),     # Chin (landmark 152)
            (-225.0, 170.0, -135.0),  # Left eye left corner (landmark 33)
            (225.0, 170.0, -135.0),   # Right eye right corner (landmark 263)
            (-150.0, -150.0, -125.0), # Left Mouth corner (landmark 61)
            (150.0, -150.0, -125.0),  # Right mouth corner (landmark 291)
        ]
    )

    # Corresponding MediaPipe landmark indices for the 6 canonical points above
    pnp_landmark_indices: List[int] = field(
        default_factory=lambda: [1, 152, 33, 263, 61, 291]
    )


@dataclass
class RiskEngineConfig:
    """Weights and thresholds for the multi-cue risk assessment engine."""

    # Weights summing to 1.0 for multi-cue linear hazard estimation
    weight_eye_closure: float = 0.40
    weight_yawn: float = 0.25
    weight_distraction: float = 0.25
    weight_blink_irregularity: float = 0.10

    # Risk score boundaries [0, 100]
    score_caution_threshold: float = 30.0
    score_drowsy_threshold: float = 60.0
    score_high_risk_threshold: float = 80.0

    # Exponential moving average smoothing factor alpha (0 < alpha <= 1)
    ema_alpha: float = 0.25


@dataclass
class AlertConfig:
    """Parameters for visual indicators and auditory alarm cues."""

    # Enable audio alarms (plays non-blocking audio bell/synth tone)
    enable_audio: bool = True

    # Cooldown time (seconds) between repeated audio alerts to prevent audio clutter
    audio_cooldown_seconds: float = 2.0


@dataclass
class AppConfig:
    """Master application configuration aggregate."""

    eye: EyeConfig = field(default_factory=EyeConfig)
    yawn: YawnConfig = field(default_factory=YawnConfig)
    head_pose: HeadPoseConfig = field(default_factory=HeadPoseConfig)
    risk: RiskEngineConfig = field(default_factory=RiskEngineConfig)
    alert: AlertConfig = field(default_factory=AlertConfig)

    # Video stream configuration
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    target_fps: int = 30

    # Detection confidence
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
