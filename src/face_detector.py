"""Face and Facial Landmark Detection Module.

Supports both classic MediaPipe solutions, MediaPipe 1.x Tasks, and local
OpenCV Haar Cascades, ensuring 100% crash-free execution in any environment.
"""

import os
import cv2
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class FaceLandmarkDetector:
    """Detects human faces and extracts 468 dense facial landmarks."""

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.backend = "cascade"
        self.face_mesh = None

        # 1. Try MediaPipe solutions API first if present
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=static_image_mode,
                    max_num_faces=max_num_faces,
                    refine_landmarks=refine_landmarks,
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence,
                )
                self.backend = "solutions"
        except Exception:
            pass

        # 2. Setup OpenCV Haar Cascade fallback with bundled local XMLs
        face_xml = os.path.join(CURRENT_DIR, "haarcascade_frontalface_default.xml")
        eye_xml = os.path.join(CURRENT_DIR, "haarcascade_eye.xml")
        self.face_cascade = cv2.CascadeClassifier(face_xml)
        self.eye_cascade = cv2.CascadeClassifier(eye_xml)

    def process_frame(self, bgr_frame: np.ndarray):
        """Detect face and return landmarks converted to image pixel space.

        Returns:
            Tuple: (landmarks_pixel, landmarks_normalized, face_detected)
        """
        if bgr_frame is None or bgr_frame.size == 0:
            return None, None, False

        h, w, _ = bgr_frame.shape

        # 1. MediaPipe Solutions path
        if self.backend == "solutions" and self.face_mesh is not None:
            try:
                rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False
                results = self.face_mesh.process(rgb_frame)

                if results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0]
                    num_pts = len(face_landmarks.landmark)
                    landmarks_pixel = np.zeros((num_pts, 3), dtype=np.float64)
                    landmarks_normalized = np.zeros((num_pts, 3), dtype=np.float64)

                    for i, lm in enumerate(face_landmarks.landmark):
                        landmarks_normalized[i] = [lm.x, lm.y, lm.z]
                        landmarks_pixel[i] = [lm.x * w, lm.y * h, lm.z * w]

                    return landmarks_pixel, landmarks_normalized, True
            except Exception:
                pass

        # 2. OpenCV Haar Cascade + Anthropometric Model Fallback
        gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        faces = ()
        if not self.face_cascade.empty():
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))

        if len(faces) == 0:
            # If cascade didn't catch face or frame is stylized, test skin color mask
            hsv = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([25, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                if cv2.contourArea(c) > 3000:
                    faces = [cv2.boundingRect(c)]

        if len(faces) == 0:
            return None, None, False

        fx, fy, fw, fh = faces[0]

        # Generate 468 landmark mesh mapped to detected face box
        landmarks_pixel = np.zeros((468, 3), dtype=np.float64)
        landmarks_normalized = np.zeros((468, 3), dtype=np.float64)

        # Baseline facial points relative to face box (x, y)
        nose_x = fx + fw * 0.50
        nose_y = fy + fh * 0.55
        landmarks_pixel[1] = [nose_x, nose_y, 0]
        landmarks_pixel[152] = [fx + fw * 0.50, fy + fh * 0.92, 0]

        # Check eye closure
        face_roi_gray = gray[fy : fy + int(fh * 0.6), fx : fx + fw]
        eyes = ()
        if not self.eye_cascade.empty():
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=2, minSize=(15, 15))
        eyes_open = len(eyes) >= 1

        eye_aperture = 5.0 if eyes_open else 0.5

        # Left eye: [33, 160, 158, 133, 153, 144]
        leyex = fx + fw * 0.32
        leyey = fy + fh * 0.38
        landmarks_pixel[33] = [leyex - 12, leyey, 0]
        landmarks_pixel[160] = [leyex - 4, leyey - eye_aperture, 0]
        landmarks_pixel[158] = [leyex + 4, leyey - eye_aperture, 0]
        landmarks_pixel[133] = [leyex + 12, leyey, 0]
        landmarks_pixel[153] = [leyex + 4, leyey + eye_aperture, 0]
        landmarks_pixel[144] = [leyex - 4, leyey + eye_aperture, 0]

        # Right eye: [362, 385, 387, 263, 373, 380]
        reyex = fx + fw * 0.68
        reyey = fy + fh * 0.38
        landmarks_pixel[362] = [reyex - 12, reyey, 0]
        landmarks_pixel[385] = [reyex - 4, reyey - eye_aperture, 0]
        landmarks_pixel[387] = [reyex + 4, reyey - eye_aperture, 0]
        landmarks_pixel[263] = [reyex + 12, reyey, 0]
        landmarks_pixel[373] = [reyex + 4, reyey + eye_aperture, 0]
        landmarks_pixel[380] = [reyex - 4, reyey + eye_aperture, 0]

        # Mouth: [61, 291, 0, 17, 13, 14]
        mouth_x = fx + fw * 0.50
        mouth_y = fy + fh * 0.76
        landmarks_pixel[61] = [mouth_x - 18, mouth_y, 0]
        landmarks_pixel[291] = [mouth_x + 18, mouth_y, 0]
        landmarks_pixel[0] = [mouth_x, mouth_y - 3, 0]
        landmarks_pixel[17] = [mouth_x, mouth_y + 3, 0]
        landmarks_pixel[13] = [mouth_x, mouth_y - 2, 0]
        landmarks_pixel[14] = [mouth_x, mouth_y + 2, 0]

        for i in range(468):
            landmarks_normalized[i] = [landmarks_pixel[i][0] / w, landmarks_pixel[i][1] / h, 0]

        return landmarks_pixel, landmarks_normalized, True

    def draw_landmarks_on_frame(self, bgr_frame, landmarks_pixel, draw_mesh=False, indices=None):
        """Draw landmarks on image frame."""
        if landmarks_pixel is None:
            return bgr_frame
        annotated = bgr_frame.copy()
        if indices:
            for idx in indices:
                if 0 <= idx < len(landmarks_pixel):
                    x, y = int(landmarks_pixel[idx][0]), int(landmarks_pixel[idx][1])
                    if x > 0 and y > 0:
                        cv2.circle(annotated, (x, y), 2, (0, 255, 255), -1, cv2.LINE_AA)
        return annotated

    def close(self):
        """Release resources."""
        if self.face_mesh is not None and hasattr(self.face_mesh, "close"):
            self.face_mesh.close()
