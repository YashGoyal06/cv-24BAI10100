"""Alert Management Module.

Handles visual indicator dispatch, rate-limiting, and debounced auditory
warning signals for driver drowsiness, distraction, and critical hazards.
"""

import logging
import platform
import subprocess
import threading
import time
from typing import Optional

from src.config import AlertConfig

logger = logging.getLogger(__name__)


class AlertManager:
    """Dispatches visual state changes and debounced audio alarm cues."""

    def __init__(self, config: Optional[AlertConfig] = None):
        """Initialize alert manager.

        Args:
            config: Optional AlertConfig instance. Uses default values if omitted.
        """
        self.config = config or AlertConfig()
        self.last_audio_time: float = 0.0
        self.current_state: str = "SAFE"
        self._lock = threading.Lock()

    def _play_audio_beep(self, frequency: int = 1000, duration_ms: int = 400) -> None:
        """Play a non-blocking system alert beep depending on OS platform.

        Args:
            frequency: Frequency of beep in Hz (where applicable).
            duration_ms: Duration of beep in milliseconds.
        """
        if not self.config.enable_audio:
            return

        def _sound_worker():
            try:
                system_name = platform.system()
                if system_name == "Darwin":
                    # macOS terminal visual/audio bell or afplay standard alert
                    # /System/Library/Sounds/Glass.aiff or Tink.aiff or Ping.aiff
                    sound_path = "/System/Library/Sounds/Ping.aiff"
                    subprocess.run(
                        ["afplay", sound_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=1.0,
                    )
                elif system_name == "Windows":
                    import winsound  # type: ignore
                    winsound.Beep(frequency, duration_ms)
                else:
                    # Linux or generic Unix: ASCII bell
                    print("\a", end="", flush=True)
            except Exception as ex:
                logger.debug("Audio play skipped or failed: %s", ex)

        # Fire and forget in background thread to never stall real-time video frames
        threading.Thread(target=_sound_worker, daemon=True).start()

    def update_alert(self, state: str, risk_score: float) -> dict:
        """Evaluate state and trigger rate-limited auditory warnings if warranted.

        Args:
            state: Driver safety state ('SAFE', 'CAUTION', 'DROWSY', 'DISTRACTED', 'HIGH RISK').
            risk_score: Current smoothed risk score.

        Returns:
            Dictionary containing:
                - 'state': Current alert state
                - 'audio_triggered': Whether an audible warning fired on this frame
                - 'alert_level': Numerical alert priority (0: None, 1: Low, 2: Medium, 3: Critical)
        """
        self.current_state = state
        now = time.time()
        audio_triggered = False

        level_map = {
            "SAFE": 0,
            "NO FACE": 0,
            "CAUTION": 1,
            "DISTRACTED": 2,
            "DROWSY": 2,
            "HIGH RISK": 3,
        }
        alert_level = level_map.get(state, 0)

        # Trigger audio alerts only for DROWSY, DISTRACTED, or HIGH RISK
        # with cooldown to avoid continuous annoyance
        if state in ("DROWSY", "DISTRACTED", "HIGH RISK"):
            with self._lock:
                if (now - self.last_audio_time) >= self.config.audio_cooldown_seconds:
                    self.last_audio_time = now
                    audio_triggered = True
                    freq = 1200 if state == "HIGH RISK" else 800
                    dur = 500 if state == "HIGH RISK" else 300
                    self._play_audio_beep(frequency=freq, duration_ms=dur)

        return {
            "state": state,
            "audio_triggered": audio_triggered,
            "alert_level": alert_level,
        }
