"""Session Analytics Module.

Tracks real-time performance indicators, driver behavioral statistics,
cumulative risk profile, and exports formatted CSV/JSON session summaries.
"""

from datetime import datetime
import json
import os
import time
from typing import Dict, List, Optional
import pandas as pd


class SessionAnalytics:
    """Collects and aggregates driver monitoring session metrics."""

    def __init__(self):
        """Initialize session analytics collector."""
        self.session_start_time: float = time.time()
        self.session_end_time: Optional[float] = None
        self.total_frames: int = 0

        # State durations (in frame counts)
        self.state_counts: Dict[str, int] = {
            "SAFE": 0,
            "CAUTION": 0,
            "DROWSY": 0,
            "DISTRACTED": 0,
            "HIGH RISK": 0,
            "NO FACE": 0,
        }

        # Event aggregates
        self.total_blinks: int = 0
        self.total_yawns: int = 0
        self.total_prolonged_closures: int = 0
        self.total_distractions: int = 0

        # Continuous timeseries records
        self.timestamps: List[float] = []
        self.risk_scores: List[float] = []
        self.ear_values: List[float] = []
        self.mar_values: List[float] = []
        self.states: List[str] = []

    def start_session(self) -> None:
        """Reset and start a fresh recording session."""
        self.session_start_time = time.time()
        self.session_end_time = None
        self.total_frames = 0
        self.state_counts = {k: 0 for k in self.state_counts}
        self.total_blinks = 0
        self.total_yawns = 0
        self.total_prolonged_closures = 0
        self.total_distractions = 0
        self.timestamps.clear()
        self.risk_scores.clear()
        self.ear_values.clear()
        self.mar_values.clear()
        self.states.clear()

    def update(
        self,
        state: str,
        risk_score: float,
        ear: float,
        mar: float,
        blinks: int,
        yawns: int,
        prolonged_closures: int,
        distractions: int,
    ) -> None:
        """Record frame-level observation into timeseries and counters.

        Args:
            state: Current safety state.
            risk_score: Smoothed risk score.
            ear: Eye Aspect Ratio.
            mar: Mouth Aspect Ratio.
            blinks: Cumulative blink count.
            yawns: Cumulative yawn count.
            prolonged_closures: Cumulative prolonged closure event count.
            distractions: Cumulative distraction event count.
        """
        self.total_frames += 1
        elapsed = time.time() - self.session_start_time

        self.state_counts[state] = self.state_counts.get(state, 0) + 1
        self.total_blinks = blinks
        self.total_yawns = yawns
        self.total_prolonged_closures = prolonged_closures
        self.total_distractions = distractions

        # Record timeseries sample (decimated or full)
        self.timestamps.append(round(elapsed, 2))
        self.risk_scores.append(round(risk_score, 2))
        self.ear_values.append(round(ear, 3))
        self.mar_values.append(round(mar, 3))
        self.states.append(state)

    def end_session(self) -> None:
        """Mark end of session recording."""
        self.session_end_time = time.time()

    def get_summary(self) -> Dict[str, any]:
        """Compute holistic summary metrics across the session.

        Returns:
            Dictionary of session summary KPIs and percentages.
        """
        end_time = self.session_end_time or time.time()
        duration_sec = max(end_time - self.session_start_time, 0.001)
        duration_min = duration_sec / 60.0

        fps = (self.total_frames / duration_sec) if duration_sec > 0 else 0.0
        avg_risk = float(pd.Series(self.risk_scores).mean()) if self.risk_scores else 0.0
        max_risk = float(pd.Series(self.risk_scores).max()) if self.risk_scores else 0.0

        safe_frames = self.state_counts.get("SAFE", 0)
        safe_pct = (safe_frames / self.total_frames * 100.0) if self.total_frames > 0 else 100.0

        drowsy_frames = self.state_counts.get("DROWSY", 0)
        drowsy_pct = (drowsy_frames / self.total_frames * 100.0) if self.total_frames > 0 else 0.0

        distracted_frames = self.state_counts.get("DISTRACTED", 0)
        distracted_pct = (distracted_frames / self.total_frames * 100.0) if self.total_frames > 0 else 0.0

        high_risk_frames = self.state_counts.get("HIGH RISK", 0)
        high_risk_pct = (high_risk_frames / self.total_frames * 100.0) if self.total_frames > 0 else 0.0

        blinks_per_min = (self.total_blinks / duration_min) if duration_min > 0 else 0.0

        return {
            "session_duration_seconds": round(duration_sec, 2),
            "session_duration_formatted": f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}",
            "total_frames_processed": self.total_frames,
            "average_fps": round(fps, 1),
            "total_blinks": self.total_blinks,
            "blinks_per_minute": round(blinks_per_min, 1),
            "prolonged_closure_events": self.total_prolonged_closures,
            "total_yawns": self.total_yawns,
            "distraction_events": self.total_distractions,
            "safe_time_percentage": round(safe_pct, 1),
            "drowsy_time_percentage": round(drowsy_pct, 1),
            "distracted_time_percentage": round(distracted_pct, 1),
            "high_risk_time_percentage": round(high_risk_pct, 1),
            "average_risk_score": round(avg_risk, 1),
            "peak_risk_score": round(max_risk, 1),
        }

    def export_csv(self, file_path: str) -> str:
        """Export raw frame timeseries to CSV.

        Args:
            file_path: Destination path for CSV.

        Returns:
            Normalized file path written.
        """
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        df = pd.DataFrame(
            {
                "timestamp_sec": self.timestamps,
                "state": self.states,
                "risk_score": self.risk_scores,
                "ear": self.ear_values,
                "mar": self.mar_values,
            }
        )
        df.to_csv(file_path, index=False)
        return file_path

    def export_json(self, file_path: str) -> str:
        """Export session summary KPIs to JSON.

        Args:
            file_path: Destination path for JSON.

        Returns:
            Normalized file path written.
        """
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return file_path
