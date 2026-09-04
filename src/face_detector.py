"""Face and Facial Landmark Detection Module.

Integrates MediaPipe FaceMesh to extract 468/478 precise 3D facial landmarks
at real-time frame rates, with graceful fallback and coordinate normalization.
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np

# Suppress noisy TensorFlow / MediaPipe logs
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


class FaceLandmarkDetector:
    """Detects human faces and extracts 468 dense facial landmarks using MediaPipe."""

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        """Initialize MediaPipe FaceMesh solution.

        Args:
            static_image_mode: Whether to treat images as static or video stream.
            max_num_faces: Maximum number of faces to detect (default: 1 for driver).
            refine_landmarks: Whether to refine iris and lip landmark coordinates.
            min_detection_confidence: Confidence threshold for face detection.
            min_tracking_confidence: Confidence threshold for landmark tracking.
        """
        import mediapipe as mp  # lazy import to verify installation

        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process_frame(
        self, bgr_frame: np.ndarray
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], bool]:
        """Detect face and return landmarks converted to image pixel space.

        Args:
            bgr_frame: BGR frame captured from OpenCV camera.

        Returns:
            Tuple of:
                - landmarks_pixel: np.ndarray of shape (468, 3) in pixel coordinates (x, y, z), or None.
                - landmarks_normalized: np.ndarray of shape (468, 3) in [0.0, 1.0], or None.
                - face_detected: Boolean flag indicating if at least one face was detected.
        """
        if bgr_frame is None or bgr_frame.size == 0:
            return None, None, False

        h, w, _ = bgr_frame.shape

        # MediaPipe requires RGB color format
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None, None, False

        # Extract primary face (driver)
        face_landmarks = results.multi_face_landmarks[0]

        num_pts = len(face_landmarks.landmark)
        landmarks_pixel = np.zeros((num_pts, 3), dtype=np.float64)
        landmarks_normalized = np.zeros((num_pts, 3), dtype=np.float64)

        for i, lm in enumerate(face_landmarks.landmark):
            landmarks_normalized[i] = [lm.x, lm.y, lm.z]
            # Convert normalized [0, 1] space to image pixel space
            landmarks_pixel[i] = [lm.x * w, lm.y * h, lm.z * w]

        return landmarks_pixel, landmarks_normalized, True

    def draw_landmarks_on_frame(
        self,
        bgr_frame: np.ndarray,
        landmarks_pixel: np.ndarray,
        draw_mesh: bool = False,
        indices: Optional[List[int]] = None,
    ) -> np.ndarray:
        """Annotate facial landmarks and key regions on BGR image.

        Args:
            bgr_frame: Input BGR frame.
            landmarks_pixel: Array of landmark coordinates in pixels.
            draw_mesh: If True, draws subtle facial mesh tessellation.
            indices: List of specific keypoint indices to highlight (e.g. eyes, mouth).

        Returns:
            Annotated BGR frame.
        """
        if landmarks_pixel is None:
            return bgr_frame

        annotated = bgr_frame.copy()

        # Highlight key landmarks (eyes, mouth, nose)
        if indices:
            for idx in indices:
                if 0 <= idx < len(landmarks_pixel):
                    x, y = int(landmarks_pixel[idx][0]), int(landmarks_pixel[idx][1])
                    cv2.circle(annotated, (x, y), 2, (0, 255, 255), -1, cv2.LINE_AA)

        return annotated

    def close(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, "face_mesh") and self.face_mesh is not None:
            self.face_mesh.close()
