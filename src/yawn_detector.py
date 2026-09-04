"""Yawn Detection Module.

Calculates Mouth Aspect Ratio (MAR) from facial landmarks and detects yawning
events using temporal thresholding to eliminate transient speech artifacts.
"""

from typing import Dict, List, Optional
import numpy as np

from src.config import YawnConfig
from src.utils import calculate_mar


class YawnDetector:
    """Detects driver yawning via Mouth Aspect Ratio (MAR) temporal smoothing."""

    def __init__(self, config: Optional[YawnConfig] = None):
        """Initialize yawn detector.

        Args:
            config: Optional YawnConfig instance. Uses default values if omitted.
        """
        self.config = config or YawnConfig()

        # State tracking
        self.open_frame_count: int = 0
        self.total_yawns: int = 0
        self.is_currently_yawning: bool = False
        self.cooldown_counter: int = 0

        # History tracking
        self.mar_history: List[float] = []

    def reset(self) -> None:
        """Reset temporal counters and history."""
        self.open_frame_count = 0
        self.total_yawns = 0
        self.is_currently_yawning = False
        self.cooldown_counter = 0
        self.mar_history.clear()

    def process_mouth(
        self, landmarks: Optional[np.ndarray]
    ) -> Dict[str, float]:
        """Analyze mouth aperture from facial landmarks.

        Args:
            landmarks: Array of (N, 2) or (N, 3) facial landmark coordinates,
                       or None if no face is detected.

        Returns:
            Dictionary containing:
                - 'mar': Current Mouth Aspect Ratio
                - 'is_mouth_open': Boolean indicating mouth aperture above threshold
                - 'is_yawning': Boolean indicating confirmed sustained yawn
                - 'open_frames': Consecutive frames mouth has been open
                - 'total_yawns': Cumulative yawn count
        """
        if landmarks is None or len(landmarks) < 300:
            return {
                "mar": 0.0,
                "is_mouth_open": False,
                "is_yawning": False,
                "open_frames": 0,
                "total_yawns": self.total_yawns,
            }

        mar = calculate_mar(landmarks, self.config.mouth_indices)
        self.mar_history.append(mar)
        if len(self.mar_history) > 300:
            self.mar_history.pop(0)

        # Decrement cooldown counter if active
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

        is_open = mar >= self.config.mar_threshold

        if is_open:
            self.open_frame_count += 1

            # Check if open duration surpasses threshold and cooldown is expired
            if (
                self.open_frame_count >= self.config.yawn_consec_frames
                and self.cooldown_counter == 0
            ):
                if not self.is_currently_yawning:
                    self.total_yawns += 1
                    self.cooldown_counter = self.config.yawn_cooldown_frames
                self.is_currently_yawning = True
        else:
            self.open_frame_count = 0
            self.is_currently_yawning = False

        return {
            "mar": mar,
            "is_mouth_open": is_open,
            "is_yawning": self.is_currently_yawning,
            "open_frames": self.open_frame_count,
            "total_yawns": self.total_yawns,
        }
