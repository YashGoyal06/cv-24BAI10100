"""Drawing utilities and visual HUD for ErgoVision."""

import cv2
import numpy as np


def draw_ergo_hud(
    frame: np.ndarray,
    posture_status: str,
    neck_tilt: float,
    lateral_tilt: float,
    dist_status: str,
    dist_cm: float,
    ear: float,
    blinks_per_min: float,
    fps: float,
) -> np.ndarray:
    """Renders professional ergonomic Heads-Up Display on video frame."""
    h, w, _ = frame.shape
    overlay = frame.copy()

    # Top HUD background panel
    cv2.rectangle(overlay, (0, 0), (w, 85), (20, 20, 20), -1)
    # Bottom Telemetry panel
    cv2.rectangle(overlay, (0, h - 35), (w, h), (15, 15, 15), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Top Title
    cv2.putText(
        frame,
        "ErgoVision | AI Posture & Screen Fatigue Guard",
        (15, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )

    # Status Badges
    # 1. Posture Badge
    p_color = (0, 220, 0) if "GOOD" in posture_status else (0, 0, 255)
    cv2.putText(
        frame,
        f"POSTURE: {posture_status}",
        (15, 52),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        p_color,
        2,
        cv2.LINE_AA,
    )

    # 2. Distance Badge
    d_color = (0, 220, 0) if "OPTIMAL" in dist_status else (0, 165, 255)
    cv2.putText(
        frame,
        f"SCREEN DIST: {dist_status} (~{int(dist_cm)}cm)",
        (15, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        d_color,
        1,
        cv2.LINE_AA,
    )

    # Bottom Telemetry bar
    telemetry = (
        f"FPS: {fps:.1f}  |  Neck Tilt: {neck_tilt:.1f} deg  |  "
        f"Head Lean: {lateral_tilt:.1f} deg  |  EAR: {ear:.2f}  |  Blinks/Min: {blinks_per_min:.1f}"
    )
    cv2.putText(
        frame,
        telemetry,
        (15, h - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    return frame
