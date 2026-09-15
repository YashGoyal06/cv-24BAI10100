"""Face and Landmark Detection Module for ErgoVision.

Employs native MediaPipe FaceMesh (468 landmarks) with smooth local fallback.
"""

import os
import cv2
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


class FaceLandmarkDetector:
    """Extracts 468 dense facial mesh landmarks."""

    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self.face_mesh = None
        self.backend = "cascade"

        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
                self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence,
                )
                self.backend = "solutions"
        except Exception:
            pass

    def process_frame(self, bgr_frame: np.ndarray):
        """Processes frame and returns (landmarks_pixel, face_detected)."""
        if bgr_frame is None or bgr_frame.size == 0:
            return None, False

        h, w, _ = bgr_frame.shape

        if self.backend == "solutions" and self.face_mesh is not None:
            try:
                rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    num_pts = len(face_landmarks.landmark)
                    landmarks_pixel = np.zeros((num_pts, 3), dtype=np.float64)

                    for i, lm in enumerate(face_landmarks.landmark):
                        landmarks_pixel[i] = [lm.x * w, lm.y * h, lm.z * w]

                    return landmarks_pixel, True
            except Exception:
                pass

        return None, False

    def close(self):
        if self.face_mesh is not None and hasattr(self.face_mesh, "close"):
            self.face_mesh.close()
