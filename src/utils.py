"""VisionGuard Utility Functions.

Geometric math helpers, Euclidean distance calculations, visual annotation,
and overlay drawing for high-contrast driver feedback.
"""

from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np


def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two 2D/3D points.

    Args:
        p1: Coordinates of first point (x, y) or (x, y, z).
        p2: Coordinates of second point (x, y) or (x, y, z).

    Returns:
        Euclidean norm ||p1 - p2||.
    """
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))


def calculate_ear(landmarks: np.ndarray, indices: List[int]) -> float:
    """Calculate Eye Aspect Ratio (EAR) based on Soukupová and Čech (2016).

    Formula:
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)

    Where:
        p1, p4: horizontal eye corner points
        p2, p6: vertical top-bottom outer landmark pair
        p3, p5: vertical top-bottom inner landmark pair

    Args:
        landmarks: Array of facial landmarks (N, 2) or (N, 3).
        indices: List of 6 landmark indices [p1, p2, p3, p4, p5, p6].

    Returns:
        Eye Aspect Ratio scalar value. Returns 0.0 if horizontal distance <= 0.
    """
    if len(indices) != 6:
        raise ValueError(f"EAR requires exactly 6 landmark indices, got {len(indices)}")

    p1 = landmarks[indices[0]][:2]
    p2 = landmarks[indices[1]][:2]
    p3 = landmarks[indices[2]][:2]
    p4 = landmarks[indices[3]][:2]
    p5 = landmarks[indices[4]][:2]
    p6 = landmarks[indices[5]][:2]

    # Compute vertical distances
    v1 = euclidean_distance(p2, p6)
    v2 = euclidean_distance(p3, p5)

    # Compute horizontal distance
    h = euclidean_distance(p1, p4)

    if h <= 1e-6:
        return 0.0

    ear = (v1 + v2) / (2.0 * h)
    return float(ear)


def calculate_mar(landmarks: np.ndarray, indices: List[int]) -> float:
    """Calculate Mouth Aspect Ratio (MAR) based on facial landmarks.

    Formula:
        MAR = (||upper_lip - lower_lip|| + ||mid_upper - mid_lower||) / (2 * ||left_corner - right_corner||)

    Args:
        landmarks: Array of facial landmarks (N, 2) or (N, 3).
        indices: List of 6 mouth indices [left, right, top, bottom, mid_top, mid_bottom].

    Returns:
        Mouth Aspect Ratio scalar value. Returns 0.0 if horizontal width <= 0.
    """
    if len(indices) < 6:
        raise ValueError(f"MAR requires at least 6 landmark indices, got {len(indices)}")

    p_left = landmarks[indices[0]][:2]
    p_right = landmarks[indices[1]][:2]
    p_top = landmarks[indices[2]][:2]
    p_bot = landmarks[indices[3]][:2]
    p_mid_top = landmarks[indices[4]][:2]
    p_mid_bot = landmarks[indices[5]][:2]

    # Vertical mouth aperture
    v1 = euclidean_distance(p_top, p_bot)
    v2 = euclidean_distance(p_mid_top, p_mid_bot)

    # Horizontal mouth width
    h = euclidean_distance(p_left, p_right)

    if h <= 1e-6:
        return 0.0

    mar = (v1 + v2) / (2.0 * h)
    return float(mar)


def draw_hud(
    frame: np.ndarray,
    status: str,
    risk_score: float,
    ear: float,
    mar: float,
    head_pose_dir: str,
    blinks: int,
    yawns: int,
    distractions: int,
    fps: float,
) -> np.ndarray:
    """Render a modern, high-contrast Heads-Up Display (HUD) on the video frame.

    Args:
        frame: OpenCV BGR image frame.
        status: Safety state ('SAFE', 'CAUTION', 'DROWSY', 'DISTRACTED', 'HIGH RISK').
        risk_score: Overall risk score in [0, 100].
        ear: Current average Eye Aspect Ratio.
        mar: Current Mouth Aspect Ratio.
        head_pose_dir: Head direction ('FORWARD', 'LEFT', 'RIGHT', etc.).
        blinks: Total blink count.
        yawns: Total yawn count.
        distractions: Total distraction events count.
        fps: Current processing frames-per-second.

    Returns:
        Frame with annotated HUD overlays.
    """
    h, w, _ = frame.shape
    overlay = frame.copy()

    # Color palette based on status
    status_colors: Dict[str, Tuple[int, int, int]] = {
        "SAFE": (46, 204, 113),         # Emerald Green (BGR)
        "CAUTION": (0, 215, 255),       # Amber / Yellow
        "DROWSY": (0, 140, 255),        # Deep Orange
        "DISTRACTED": (204, 102, 0),    # Blue-Violet
        "HIGH RISK": (40, 40, 230),     # Crimson Red
        "NO FACE": (128, 128, 128),     # Gray
    }
    badge_color = status_colors.get(status, (255, 255, 255))

    # Top Status Bar background (translucent dark slate)
    cv2.rectangle(overlay, (0, 0), (w, 65), (15, 23, 42), -1)
    # Bottom Telemetry Bar background
    cv2.rectangle(overlay, (0, h - 50), (w, h), (15, 23, 42), -1)

    # Blend overlay for glassmorphic effect
    alpha = 0.82
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Top Status Badge
    cv2.rectangle(frame, (16, 12), (180, 52), badge_color, -1)
    text_color = (0, 0, 0) if status in ("SAFE", "CAUTION") else (255, 255, 255)
    cv2.putText(
        frame,
        status,
        (26, 40),
        cv2.FONT_HERSHEY_DUPLEX,
        0.75,
        text_color,
        2,
        cv2.LINE_AA,
    )

    # Risk Score Gauge Bar
    gauge_x = 200
    gauge_w = 150
    gauge_h = 16
    gauge_y = 25
    cv2.rectangle(frame, (gauge_x, gauge_y), (gauge_x + gauge_w, gauge_y + gauge_h), (50, 60, 75), -1)
    fill_w = int(gauge_w * min(max(risk_score / 100.0, 0.0), 1.0))
    cv2.rectangle(frame, (gauge_x, gauge_y), (gauge_x + fill_w, gauge_y + gauge_h), badge_color, -1)
    cv2.putText(
        frame,
        f"Risk: {risk_score:.0f}%",
        (gauge_x + gauge_w + 12, gauge_y + 13),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )

    # FPS counter on top right
    fps_text = f"FPS: {fps:.1f}"
    cv2.putText(
        frame,
        fps_text,
        (w - 110, 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 200),
        1,
        cv2.LINE_AA,
    )

    # Bottom Telemetry Items
    col1 = f"EAR: {ear:.2f}"
    col2 = f"MAR: {mar:.2f}"
    col3 = f"Pose: {head_pose_dir}"
    col4 = f"Blinks: {blinks}"
    col5 = f"Yawns: {yawns}"
    col6 = f"Distract: {distractions}"

    telemetry_items = [col1, col2, col3, col4, col5, col6]
    spacing = w // (len(telemetry_items) + 1)
    for idx, item in enumerate(telemetry_items):
        pos_x = 15 + idx * spacing
        cv2.putText(
            frame,
            item,
            (pos_x, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (210, 220, 230),
            1,
            cv2.LINE_AA,
        )

    # If HIGH RISK or DROWSY, render border highlight
    if status in ("HIGH RISK", "DROWSY"):
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), badge_color, 4)

    return frame
