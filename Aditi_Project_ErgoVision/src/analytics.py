"""Session Analytics and Metric Exporter for ErgoVision."""

import csv
import json
import time
from typing import Dict, List


class ErgoAnalytics:
    """Tracks session telemetry and exports summary statistics."""

    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.records: List[Dict] = []
        self.total_frames = 0
        self.good_posture_frames = 0
        self.slouch_frames = 0
        self.too_close_frames = 0

    def start_session(self):
        self.start_time = time.time()
        self.records.clear()
        self.total_frames = 0
        self.good_posture_frames = 0
        self.slouch_frames = 0
        self.too_close_frames = 0

    def update(self, posture_status: str, is_slouching: bool, is_too_close: bool, ear: float, blinks: int):
        self.total_frames += 1
        if is_slouching:
            self.slouch_frames += 1
        else:
            self.good_posture_frames += 1

        if is_too_close:
            self.too_close_frames += 1

        self.records.append({
            "timestamp": round(time.time() - self.start_time, 2),
            "posture": posture_status,
            "slouching": is_slouching,
            "too_close": is_too_close,
            "ear": round(ear, 3),
            "blinks": blinks,
        })

    def end_session(self):
        self.end_time = time.time()

    def get_summary(self) -> Dict:
        duration = max(self.end_time - self.start_time, 1.0)
        good_pct = (self.good_posture_frames / max(self.total_frames, 1)) * 100.0
        slouch_pct = (self.slouch_frames / max(self.total_frames, 1)) * 100.0
        close_pct = (self.too_close_frames / max(self.total_frames, 1)) * 100.0

        return {
            "duration_seconds": round(duration, 1),
            "total_frames": self.total_frames,
            "good_posture_pct": round(good_pct, 1),
            "slouch_time_pct": round(slouch_pct, 1),
            "too_close_pct": round(close_pct, 1),
        }

    def export_csv(self, file_path: str):
        if not self.records:
            return
        keys = self.records[0].keys()
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.records)

    def export_json(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump(self.get_summary(), f, indent=2)
