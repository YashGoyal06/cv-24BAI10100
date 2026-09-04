"""Head Pose and Driver Distraction Detection Module.

Estimates 3D head orientation (Pitch, Yaw, Roll) using OpenCV's Perspective-n-Point
(SolvePnP) algorithm with canonical 3D facial feature points and 2D MediaPipe landmarks.
"""

from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from src.config import HeadPoseConfig


class HeadPoseEstimator:
    """Estimates 3D head orientation and classifies driver distraction direction."""

    def __init__(self, config: Optional[HeadPoseConfig] = None):
        """Initialize head pose estimator.

        Args:
            config: Optional HeadPoseConfig instance. Uses default values if omitted.
        """
        self.config = config or HeadPoseConfig()

        # 3D model points in canonical world coordinates (float64)
        self.model_points_3d = np.array(
            self.config.model_points_3d, dtype=np.float64
        )

        # Distraction temporal tracking
        self.distraction_frame_count: int = 0
        self.total_distraction_events: int = 0
        self.is_distracted: bool = False

    def reset(self) -> None:
        """Reset temporal state counters."""
        self.distraction_frame_count = 0
        self.total_distraction_events = 0
        self.is_distracted = False

    def estimate_pose(
        self,
        landmarks: Optional[np.ndarray],
        frame_shape: Tuple[int, int, int],
    ) -> Dict[str, any]:
        """Estimate 3D head orientation (Pitch, Yaw, Roll) via SolvePnP.

        Args:
            landmarks: Array of (N, 2) or (N, 3) 2D pixel coordinates, or None.
            frame_shape: Shape of the input image frame (H, W, C).

        Returns:
            Dictionary containing:
                - 'pitch': Rotation around X-axis (degrees, positive = looking down)
                - 'yaw': Rotation around Y-axis (degrees, positive = looking right)
                - 'roll': Rotation around Z-axis (degrees, positive = tilting right)
                - 'direction': Categorical direction ('FORWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN')
                - 'is_distracted': Boolean indicating persistent gaze away from road
                - 'distraction_events': Cumulative distraction event count
                - 'nose_2d': Coordinates of 2D nose tip for projection
                - 'nose_3d_proj': Projected 3D forward line point for orientation axis drawing
        """
        h, w, _ = frame_shape

        if landmarks is None or len(landmarks) < 300:
            return {
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0,
                "direction": "FORWARD",
                "is_distracted": False,
                "distraction_events": self.total_distraction_events,
                "nose_2d": None,
                "nose_3d_proj": None,
            }

        # Extract the 6 canonical 2D landmarks corresponding to the 3D model
        image_points_2d = []
        for idx in self.config.pnp_landmark_indices:
            pt = landmarks[idx][:2]
            image_points_2d.append([pt[0], pt[1]])
        image_points_2d = np.array(image_points_2d, dtype=np.float64)

        # Camera Intrinsic Matrix approximation (assuming principal point at frame center)
        focal_length = w
        center = (w / 2.0, h / 2.0)
        camera_matrix = np.array(
            [
                [focal_length, 0.0, center[0]],
                [0.0, focal_length, center[1]],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

        # Assuming no lens distortion
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # Solve Perspective-n-Point
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points_3d,
            image_points_2d,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            return {
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0,
                "direction": "FORWARD",
                "is_distracted": False,
                "distraction_events": self.total_distraction_events,
                "nose_2d": None,
                "nose_3d_proj": None,
            }

        # Convert Rodrigues rotation vector to 3x3 rotation matrix
        rotation_mat, _ = cv2.Rodrigues(rotation_vector)

        # Decompose rotation matrix into Euler angles
        # Using RQDecomp3x3 for robust Euler angle extraction (Pitch, Yaw, Roll)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_mat)

        pitch = float(angles[0] * 360.0)
        yaw = float(angles[1] * 360.0)
        roll = float(angles[2] * 360.0)

        # Classify head gaze direction
        direction = "FORWARD"
        if yaw > self.config.yaw_threshold:
            direction = "RIGHT"
        elif yaw < -self.config.yaw_threshold:
            direction = "LEFT"
        elif pitch > self.config.pitch_threshold:
            direction = "DOWN"
        elif pitch < -self.config.pitch_threshold:
            direction = "UP"

        # Temporal distraction detection
        if direction != "FORWARD":
            self.distraction_frame_count += 1
            if self.distraction_frame_count >= self.config.distraction_consec_frames:
                if not self.is_distracted:
                    self.total_distraction_events += 1
                self.is_distracted = True
        else:
            self.distraction_frame_count = 0
            self.is_distracted = False

        # Project 3D nose vector into image space for directional gaze ray
        nose_end_point3D = np.array([[0.0, 0.0, 1000.0]], dtype=np.float64)
        projected_pts, _ = cv2.projectPoints(
            nose_end_point3D,
            rotation_vector,
            translation_vector,
            camera_matrix,
            dist_coeffs,
        )
        nose_2d = (int(image_points_2d[0][0]), int(image_points_2d[0][1]))
        nose_3d_proj = (int(projected_pts[0][0][0]), int(projected_pts[0][0][1]))

        return {
            "pitch": pitch,
            "yaw": yaw,
            "roll": roll,
            "direction": direction,
            "is_distracted": self.is_distracted,
            "distraction_events": self.total_distraction_events,
            "nose_2d": nose_2d,
            "nose_3d_proj": nose_3d_proj,
        }
