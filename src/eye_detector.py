"""Eye and Blink Detection Module.

Calculates Eye Aspect Ratio (EAR) across left and right eyes, tracks instantaneous
and rolling blink frequencies, and identifies prolonged eye closure with temporal smoothing.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

from src.config import EyeConfig
from src.utils import calculate_ear


class EyeDetector:
    """Detects blinks and prolonged eye closures using Eye Aspect Ratio (EAR)."""

    def __init__(self, config: Optional[EyeConfig] = None):
        """Initialize eye detector with configuration.

        Args:
            config: Optional EyeConfig instance. Uses default values if omitted.
        """
        self.config = config or EyeConfig()

        # State tracking
        self.closed_frame_count: int = 0
        self.total_blinks: int = 0
        self.prolonged_closure_events: int = 0
        self.is_currently_closed: bool = False
        self.is_prolonged_closure: bool = False

        # History tracking for analysis
        self.ear_history: List[float] = []

    def reset(self) -> None:
        """Reset internal temporal counters and history."""
        self.closed_frame_count = 0
        self.total_blinks = 0
        self.prolonged_closure_events = 0
        self.is_currently_closed = False
        self.is_prolonged_closure = False
        self.ear_history.clear()

    def process_eyes(
        self, landmarks: Optional[np.ndarray]
    ) -> Dict[str, float]:
        """Analyze eyes from facial landmarks.

        Args:
            landmarks: Array of (N, 2) or (N, 3) facial landmark coordinates,
                       or None if no face is detected.

        Returns:
            Dictionary containing:
                - 'left_ear': EAR for left eye
                - 'right_ear': EAR for right eye
                - 'avg_ear': Average EAR
                - 'is_eye_closed': Boolean indicating closed eyes in current frame
                - 'is_prolonged_closure': Boolean indicating sustained closure (>threshold frames)
                - 'closed_frames': Consecutive frames eyes have been closed
                - 'total_blinks': Cumulative blink count
                - 'prolonged_events': Cumulative prolonged closure event count
        """
        if landmarks is None or len(landmarks) < 400:
            return {
                "left_ear": 0.0,
                "right_ear": 0.0,
                "avg_ear": 0.0,
                "is_eye_closed": False,
                "is_prolonged_closure": False,
                "closed_frames": 0,
                "total_blinks": self.total_blinks,
                "prolonged_events": self.prolonged_closure_events,
            }

        # Calculate EAR for both eyes
        left_ear = calculate_ear(landmarks, self.config.left_eye_indices)
        right_ear = calculate_ear(landmarks, self.config.right_eye_indices)
        avg_ear = float((left_ear + right_ear) / 2.0)

        self.ear_history.append(avg_ear)
        if len(self.ear_history) > 300:
            self.ear_history.pop(0)

        # Evaluate closure against configurable threshold
        eye_closed = avg_ear < self.config.ear_threshold

        if eye_closed:
            self.closed_frame_count += 1
            self.is_currently_closed = True

            # Check for prolonged eye closure
            if self.closed_frame_count >= self.config.eye_closed_consec_frames:
                if not self.is_prolonged_closure:
                    # New prolonged closure event triggered
                    self.prolonged_closure_events += 1
                self.is_prolonged_closure = True
            else:
                self.is_prolonged_closure = False
        else:
            # Eye opened: check if prior closure qualifies as a normal blink
            if (
                self.config.blink_consec_frames_min
                <= self.closed_frame_count
                <= self.config.blink_consec_frames_max
            ):
                self.total_blinks += 1

            self.closed_frame_count = 0
            self.is_currently_closed = False
            self.is_prolonged_closure = False

        return {
            "left_ear": left_ear,
            "right_ear": right_ear,
            "avg_ear": avg_ear,
            "is_eye_closed": eye_closed,
            "is_prolonged_closure": self.is_prolonged_closure,
            "closed_frames": self.closed_frame_count,
            "total_blinks": self.total_blinks,
            "prolonged_events": self.prolonged_closure_events,
        }
