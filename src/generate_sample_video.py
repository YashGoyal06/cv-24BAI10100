#!/usr/bin/env python3
"""Synthetic Driving Video Generator for VisionGuard.

Generates a realistic 30 FPS test video (data/sample_video.mp4) simulating
a driver in various safety states:
- 0 to 4s:  Normal attentive driving (eyes open, looking forward)
- 4 to 8s:  Drowsy / Prolonged eye closure
- 8 to 12s: Distraction (head turned looking right)
- 12 to 16s: Yawning episode (mouth wide open)
- 16 to 20s: Return to safe baseline driving

Enables 100% automated terminal evaluation without requiring physical webcam hardware.
"""

import os
import cv2
import numpy as np

def generate_sample_video(output_path="data/sample_video.mp4", duration_sec=20, fps=30):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    print(f"Generating synthetic test video: {output_path} ({duration_sec}s, {total_frames} frames)...")

    for f_idx in range(total_frames):
        t = f_idx / fps
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Background: vehicle interior ambience
        frame[:] = (25, 28, 36)

        # Subtle road horizon gradient in windshield area
        cv2.rectangle(frame, (80, 40), (560, 200), (45, 50, 60), -1)
        cv2.line(frame, (320, 140), (200, 200), (70, 75, 85), 2)
        cv2.line(frame, (320, 140), (440, 200), (70, 75, 85), 2)

        # Determine simulated driver state based on timestamp
        is_closed = False
        is_yawn = False
        pose_offset_x = 0

        if 4.0 <= t < 8.0:
            # Drowsy: closed eyes
            is_closed = True
        elif 8.0 <= t < 12.0:
            # Distracted: head turned right
            pose_offset_x = 45
        elif 12.0 <= t < 16.0:
            # Yawn: mouth wide open
            is_yawn = True

        # Driver Head Silhouette
        center_x = 320 + pose_offset_x
        center_y = 280
        # Neck & Shoulders
        cv2.ellipse(frame, (center_x, 430), (140, 100), 0, 0, 180, (40, 45, 55), -1)
        # Head oval
        cv2.ellipse(frame, (center_x, center_y), (85, 110), 0, 0, 360, (190, 160, 140), -1)

        # Hair
        cv2.ellipse(frame, (center_x, center_y - 45), (88, 70), 0, 180, 360, (30, 25, 20), -1)

        # Eyes (relative to center)
        eye_y = center_y - 15
        left_eye_x = center_x - 30
        right_eye_x = center_x + 30

        if is_closed:
            # Closed eyes (drooping line)
            cv2.line(frame, (left_eye_x - 14, eye_y), (left_eye_x + 14, eye_y), (40, 30, 25), 3)
            cv2.line(frame, (right_eye_x - 14, eye_y), (right_eye_x + 14, eye_y), (40, 30, 25), 3)
        else:
            # Open eyes with pupil
            cv2.ellipse(frame, (left_eye_x, eye_y), (14, 8), 0, 0, 360, (245, 245, 245), -1)
            cv2.circle(frame, (left_eye_x, eye_y), 4, (40, 30, 25), -1)
            cv2.ellipse(frame, (right_eye_x, eye_y), (14, 8), 0, 0, 360, (245, 245, 245), -1)
            cv2.circle(frame, (right_eye_x, eye_y), 4, (40, 30, 25), -1)

        # Eyebrows
        cv2.line(frame, (left_eye_x - 15, eye_y - 14), (left_eye_x + 15, eye_y - 12), (30, 25, 20), 3)
        cv2.line(frame, (right_eye_x - 15, eye_y - 12), (right_eye_x + 15, eye_y - 14), (30, 25, 20), 3)

        # Nose
        cv2.line(frame, (center_x, eye_y + 8), (center_x - 4, eye_y + 35), (160, 130, 110), 2)
        cv2.line(frame, (center_x - 4, eye_y + 35), (center_x + 6, eye_y + 35), (160, 130, 110), 2)

        # Mouth
        mouth_y = center_y + 55
        if is_yawn:
            # Wide open mouth (vertical ellipse)
            cv2.ellipse(frame, (center_x, mouth_y), (18, 28), 0, 0, 360, (60, 20, 30), -1)
            cv2.ellipse(frame, (center_x, mouth_y), (18, 28), 0, 0, 360, (140, 70, 70), 2)
        else:
            # Closed / resting mouth
            cv2.line(frame, (center_x - 22, mouth_y), (center_x + 22, mouth_y), (140, 70, 70), 3)

        # Timestamp and scenario overlay in bottom left
        info = f"Synthetic Benchmark: {t:4.1f}s | "
        if 4.0 <= t < 8.0:
            info += "Scenario: Closed Eyes (Drowsy)"
        elif 8.0 <= t < 12.0:
            info += "Scenario: Head Turn (Distraction)"
        elif 12.0 <= t < 16.0:
            info += "Scenario: Sustained Yawn"
        else:
            info += "Scenario: Attentive Forward Driving"
        cv2.putText(frame, info, (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 170, 180), 1, cv2.LINE_AA)

        out.write(frame)

    out.release()
    print(f"[✓] Synthetic test video successfully created: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")
    return output_path

if __name__ == "__main__":
    generate_sample_video()
