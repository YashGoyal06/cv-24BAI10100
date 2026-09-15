#!/usr/bin/env python3
"""VisionGuard - Master Single-Command Entry Point.

Usage:
    python3 main.py           # Launches interactive visual window with live video & HUD
    python3 main.py --cli     # Runs in pure terminal stdout mode (headless/automated)

By default, 'python3 main.py' opens a live OpenCV display window showing:
- Real-time video feed with detected face bounding box & facial landmarks
- Glassmorphic top HUD with color-coded safety badge (SAFE, DROWSY, DISTRACTED, HIGH RISK)
- Dynamic risk gauge bar (0 - 100%)
- Live telemetry bar (FPS, EAR, MAR, Head Pose direction, Blink count, Yawn count)
- Press 'q' or ESC in the window to stop and view the final session summary.
"""

import argparse
import os
import sys
import time
import warnings
import cv2
import numpy as np

# Suppress framework deprecation notices for a clean terminal experience
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.alert_manager import AlertManager
from src.analytics import SessionAnalytics
from src.camera import VideoStream
from src.config import AppConfig
from src.eye_detector import EyeDetector
from src.face_detector import FaceLandmarkDetector
from src.head_pose import HeadPoseEstimator
from src.risk_engine import RiskEngine
from src.utils import draw_hud
from src.yawn_detector import YawnDetector

DEFAULT_VIDEO = os.path.join(CURRENT_DIR, "data", "sample_video.mp4")


def resolve_video_stream(source):
    """Open video stream with automatic fallback to sample video if webcam is blocked."""
    stream = VideoStream(source=source)
    if stream.start():
        return stream, source, False

    # If camera 0 failed (e.g. macOS permission restriction), fallback to sample video
    if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
        print("\n[!] Camera device not accessible directly. Engaging bundled test video.")
        if not os.path.exists(DEFAULT_VIDEO):
            from src.generate_sample_video import generate_sample_video
            generate_sample_video(DEFAULT_VIDEO)
        fallback_stream = VideoStream(source=DEFAULT_VIDEO)
        if fallback_stream.start():
            return fallback_stream, DEFAULT_VIDEO, True

    return None, source, False


def run_visual(source=0, duration=0, no_audio=False):
    """Run VisionGuard with live visual OpenCV display window showing HUD & landmarks."""
    print("=" * 72)
    print("  VisionGuard: Driver Drowsiness & Distraction Detection System")
    print("  Interactive Visual Mode (Press 'q' or ESC to stop)")
    print("=" * 72)

    stream, active_source, is_fallback = resolve_video_stream(source)
    if stream is None:
        print(f"[ERROR] Could not open video source: {source}")
        sys.exit(1)

    print(f"[*] Video Source : {active_source}")
    print(f"[*] Audio Alerts : {'Disabled' if no_audio else 'Enabled'}")
    print("[*] Controls     : Press 'q' or ESC on the video window to finish.\n")

    config = AppConfig()
    if no_audio:
        config.alert.enable_audio = False

    face_detector = FaceLandmarkDetector(
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
    )
    eye_detector = EyeDetector(config.eye)
    yawn_detector = YawnDetector(config.yawn)
    head_pose = HeadPoseEstimator(config.head_pose)
    risk_engine = RiskEngine(config.risk)
    alert_manager = AlertManager(config.alert)
    analytics = SessionAnalytics()
    analytics.start_session()

    window_name = "VisionGuard - AI Driver Safety Monitoring"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)

    start_time = time.time()

    try:
        while True:
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                print(f"\n[*] Target duration ({duration}s) reached.")
                break

            success, frame = stream.read_frame()
            if not success or frame is None:
                if is_fallback:
                    # Loop benchmark video
                    stream.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    success, frame = stream.read_frame()
                    if not success:
                        break
                else:
                    break

            # 1. Face & Landmarks
            landmarks_px, _, face_detected = face_detector.process_frame(frame)

            # 2. Eye Aspect Ratio & Blinks
            eye_data = eye_detector.process_eyes(landmarks_px)

            # 3. Mouth Aspect Ratio & Yawns
            yawn_data = yawn_detector.process_mouth(landmarks_px)

            # 4. 3D Head Pose
            pose_data = head_pose.estimate_pose(landmarks_px, frame.shape)

            # 5. Composite Risk Assessment
            risk_data = risk_engine.assess_risk(
                eye_data=eye_data,
                yawn_data=yawn_data,
                pose_data=pose_data,
                face_detected=face_detected,
            )

            # 6. Audio alerts
            alert_manager.update_alert(risk_data["state"], risk_data["risk_score"])

            # 7. Session Analytics
            analytics.update(
                state=risk_data["state"],
                risk_score=risk_data["risk_score"],
                ear=eye_data["avg_ear"],
                mar=yawn_data["mar"],
                blinks=eye_data["total_blinks"],
                yawns=yawn_data["total_yawns"],
                prolonged_closures=eye_data["prolonged_events"],
                distractions=pose_data["distraction_events"],
            )

            # 8. Render Visual Overlays & HUD on Frame
            annotated_frame = frame.copy()

            if face_detected and landmarks_px is not None:
                # Draw facial landmark points
                annotated_frame = face_detector.draw_landmarks_on_frame(
                    annotated_frame,
                    landmarks_px,
                    indices=config.eye.left_eye_indices
                    + config.eye.right_eye_indices
                    + config.yawn.mouth_indices
                    + [1, 152],
                )
                # Draw 3D Gaze Ray pointing in head orientation
                if pose_data.get("nose_2d") and pose_data.get("nose_3d_proj"):
                    cv2.line(
                        annotated_frame,
                        pose_data["nose_2d"],
                        pose_data["nose_3d_proj"],
                        (255, 180, 0),
                        2,
                        cv2.LINE_AA,
                    )

            # Draw the HUD bar
            annotated_frame = draw_hud(
                frame=annotated_frame,
                status=risk_data["state"],
                risk_score=risk_data["risk_score"],
                ear=eye_data["avg_ear"],
                mar=yawn_data["mar"],
                head_pose_dir=pose_data["direction"],
                blinks=eye_data["total_blinks"],
                yawns=yawn_data["total_yawns"],
                distractions=pose_data["distraction_events"],
                fps=stream.get_fps(),
            )

            # Display the live window
            cv2.imshow(window_name, annotated_frame)

            # Check key press ('q' or ESC = 27)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                print("\n[*] Monitoring stopped by user key press.")
                break

    except KeyboardInterrupt:
        print("\n[*] Monitoring interrupted (Ctrl+C).")
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        face_detector.close()
        analytics.end_session()

    # Print session summary and save logs
    print_session_summary(analytics)


def print_session_summary(analytics):
    """Display final KPI summary and write CSV/JSON exports."""
    print("\n" + "=" * 72)
    print("  VISIONGUARD - POST-DRIVE SESSION ANALYTICS")
    print("=" * 72)
    summary = analytics.get_summary()
    for k, v in summary.items():
        label = k.replace("_", " ").title()
        print(f"  • {label:<32}: {v}")

    os.makedirs(os.path.join(CURRENT_DIR, "data", "sample_sessions"), exist_ok=True)
    csv_out = os.path.join(CURRENT_DIR, "data", "sample_sessions", "latest_session.csv")
    json_out = os.path.join(CURRENT_DIR, "data", "sample_sessions", "latest_session.json")
    analytics.export_csv(csv_out)
    analytics.export_json(json_out)
    print("-" * 72)
    print(f"[✓] Telemetry CSV exported:  {csv_out}")
    print(f"[✓] Summary JSON exported:    {json_out}")
    print("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="VisionGuard – AI Driver Drowsiness & Distraction Detection System"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Camera device index (default: 0) or path to video file (.mp4, .avi)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in headless terminal stdout mode without GUI window",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Monitoring duration in seconds (default: 0 = run until 'q' or Ctrl+C)",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio beep alerts",
    )
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    if args.cli:
        # Import and run CLI mode
        from cli import run_cli
        run_cli(source=source, duration=args.duration if args.duration > 0 else 15, no_audio=args.no_audio)
    else:
        # Default: Visual Window with real-time video feed and HUD
        run_visual(source=source, duration=args.duration, no_audio=args.no_audio)


if __name__ == "__main__":
    main()
