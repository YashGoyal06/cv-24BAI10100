"""Risk Assessment Engine Module.

Synthesizes multiple Computer Vision cues (eye closure, yawning, head pose distraction,
and blinking irregularities) into a unified, mathematically bounded real-time Risk Score
and discrete Safety State.
"""

from typing import Dict, Optional
from src.config import RiskEngineConfig


class RiskEngine:
    """Multi-cue driver safety risk assessment engine."""

    def __init__(self, config: Optional[RiskEngineConfig] = None):
        """Initialize risk engine with configurable weights and thresholds.

        Args:
            config: Optional RiskEngineConfig instance. Uses default values if omitted.
        """
        self.config = config or RiskEngineConfig()

        # Smoothed exponential moving average risk score
        self.smoothed_risk_score: float = 0.0
        self.current_state: str = "SAFE"

    def reset(self) -> None:
        """Reset internal smoothed score and status."""
        self.smoothed_risk_score = 0.0
        self.current_state = "SAFE"

    def assess_risk(
        self,
        eye_data: Dict[str, any],
        yawn_data: Dict[str, any],
        pose_data: Dict[str, any],
        face_detected: bool = True,
    ) -> Dict[str, any]:
        """Compute composite hazard score and determine current driver safety state.

        Formula:
            InstantHazard = (W_eye * EyeFactor + W_yawn * YawnFactor +
                             W_dist * DistractFactor + W_blink * BlinkFactor) * 100
            SmoothedScore_t = alpha * InstantHazard + (1 - alpha) * SmoothedScore_{t-1}

        Safety State Classification:
            - If no face detected: 'NO FACE'
            - If eye_closed prolonged AND distracted: 'HIGH RISK'
            - If prolonged eye closure: 'DROWSY'
            - If sustained head turned away: 'DISTRACTED'
            - Else if SmoothedScore >= score_drowsy_threshold: 'DROWSY'
            - Else if SmoothedScore >= score_caution_threshold: 'CAUTION'
            - Else: 'SAFE'

        Args:
            eye_data: Output dictionary from EyeDetector.
            yawn_data: Output dictionary from YawnDetector.
            pose_data: Output dictionary from HeadPoseEstimator.
            face_detected: Whether a driver's face was detected in current frame.

        Returns:
            Dictionary containing:
                - 'state': Driver safety classification
                - 'instant_score': Raw instant risk score [0, 100]
                - 'risk_score': Smoothed risk score [0, 100]
                - 'is_high_risk': Boolean indicating critical hazard
        """
        if not face_detected:
            self.current_state = "NO FACE"
            return {
                "state": "NO FACE",
                "instant_score": 0.0,
                "risk_score": self.smoothed_risk_score,
                "is_high_risk": False,
            }

        # 1. Eye Closure Component [0.0, 1.0]
        # Scales linearly with duration of closure up to 1.0
        closed_frames = eye_data.get("closed_frames", 0)
        eye_factor = min(closed_frames / 15.0, 1.0)
        if eye_data.get("is_prolonged_closure", False):
            eye_factor = 1.0

        # 2. Yawning Component [0.0, 1.0]
        yawn_factor = 1.0 if yawn_data.get("is_yawning", False) else (
            0.5 if yawn_data.get("is_mouth_open", False) else 0.0
        )

        # 3. Distraction Component [0.0, 1.0]
        distract_factor = 1.0 if pose_data.get("is_distracted", False) else (
            0.4 if pose_data.get("direction", "FORWARD") != "FORWARD" else 0.0
        )

        # 4. Blink Irregularity / Frequency factor [0.0, 1.0]
        # Sudden rapid blinking or zero blinking over prolonged periods
        blink_factor = 0.0
        if eye_data.get("is_eye_closed", False):
            blink_factor = 0.5

        # Weighted Linear Combination [0.0, 100.0]
        instant_score = (
            self.config.weight_eye_closure * eye_factor
            + self.config.weight_yawn * yawn_factor
            + self.config.weight_distraction * distract_factor
            + self.config.weight_blink_irregularity * blink_factor
        ) * 100.0

        instant_score = min(max(instant_score, 0.0), 100.0)

        # Exponential Moving Average (EMA) temporal smoothing
        alpha = self.config.ema_alpha
        self.smoothed_risk_score = (alpha * instant_score) + ((1.0 - alpha) * self.smoothed_risk_score)

        # State Decision Hierarchy
        is_prolonged_eye = eye_data.get("is_prolonged_closure", False)
        is_distracted = pose_data.get("is_distracted", False)
        is_yawning = yawn_data.get("is_yawning", False)

        if is_prolonged_eye and is_distracted:
            state = "HIGH RISK"
        elif is_prolonged_eye:
            state = "DROWSY"
        elif is_distracted:
            state = "DISTRACTED"
        elif is_yawning:
            state = "CAUTION"
        elif self.smoothed_risk_score >= self.config.score_high_risk_threshold:
            state = "HIGH RISK"
        elif self.smoothed_risk_score >= self.config.score_drowsy_threshold:
            state = "DROWSY"
        elif self.smoothed_risk_score >= self.config.score_caution_threshold:
            state = "CAUTION"
        else:
            state = "SAFE"

        self.current_state = state

        return {
            "state": state,
            "instant_score": instant_score,
            "risk_score": float(self.smoothed_risk_score),
            "is_high_risk": state == "HIGH RISK",
        }
