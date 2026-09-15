"""Camera and Video Capture Handler for ErgoVision."""

import time
import cv2


class VideoStream:
    """Encapsulates OpenCV VideoCapture with fallback and FPS calculation."""

    def __init__(self, source=0, width=640, height=480):
        self.source = source
        self.width = width
        self.height = height
        self.cap = None
        self.prev_time = time.time()
        self.fps = 0.0

    def start(self) -> bool:
        """Initialize camera or video file."""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            return False

        if isinstance(self.source, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        return True

    def read_frame(self):
        """Read a frame and compute instantaneous FPS."""
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret:
            return False, None

        curr_time = time.time()
        delta = curr_time - self.prev_time
        if delta > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / delta)
        self.prev_time = curr_time

        return True, frame

    def get_fps(self) -> float:
        return max(self.fps, 1.0)

    def stop(self):
        if self.cap is not None:
            self.cap.release()
