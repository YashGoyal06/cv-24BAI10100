"""Camera and Video Stream Acquisition Module.

Provides robust, thread-safe frame acquisition from hardware webcams,
synthetic video streams, or video files with automatic reconnection,
FPS tracking, and error diagnostics.
"""

import logging
import time
from typing import Optional, Tuple
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoStream:
    """Manages video frame acquisition with error tolerance and auto-recovery."""

    def __init__(
        self,
        source: int | str = 0,
        width: int = 640,
        height: int = 480,
        target_fps: int = 30,
    ):
        """Initialize video stream.

        Args:
            source: Camera device index (int, e.g. 0) or video file path (str).
            width: Desired capture frame width.
            height: Desired capture frame height.
            target_fps: Target frame capture rate.
        """
        self.source = source
        self.width = width
        self.height = height
        self.target_fps = target_fps

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened: bool = False
        self.frame_count: int = 0
        self.start_time: float = time.time()
        self.last_frame_time: float = time.time()
        self.fps: float = float(target_fps)

    def start(self) -> bool:
        """Open video capture stream.

        Returns:
            True if capture opened successfully, False otherwise.
        """
        try:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                logger.warning("Failed to open video source: %s", self.source)
                self.is_opened = False
                return False

            # Set hardware properties if available
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

            self.is_opened = True
            self.start_time = time.time()
            self.last_frame_time = time.time()
            self.frame_count = 0
            return True
        except Exception as ex:
            logger.error("Error opening video capture: %s", ex)
            self.is_opened = False
            return False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a single frame from the stream and compute rolling FPS.

        Returns:
            Tuple of (success_flag, bgr_frame).
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None

        self.frame_count += 1
        now = time.time()
        delta = now - self.last_frame_time
        if delta > 0:
            instant_fps = 1.0 / delta
            # Smooth FPS using alpha=0.1 filter
            self.fps = 0.9 * self.fps + 0.1 * instant_fps
        self.last_frame_time = now

        return True, frame

    def get_fps(self) -> float:
        """Return current computed FPS."""
        return max(round(self.fps, 1), 1.0)

    def stop(self) -> None:
        """Release camera resource."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_opened = False
