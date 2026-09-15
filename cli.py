#!/usr/bin/env python3
"""VisionGuard - Standalone Command-Line Interface (CLI).

Provides terminal-based, non-GUI execution of the Driver Drowsiness
and Distraction Detection pipeline for headless/automated environments,
satisfying the CLI-executability requirement.
"""

import argparse
import os
import sys
import time
import cv2
import numpy as np

# Ensure project root is in path
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


def run_cli(source=0, duration=15, export_prefix="cli_session", no_audio=False):
    """Execute VisionGuard monitoring in pure terminal mode.

    Args:
        source: Camera index (int) or path to video file (str).
        duration: Run duration in seconds (or 0 for infinite until Ctrl+C).
        export_prefix: Prefix for exported CSV/JSON telemetry logs.
        no_audio: If True, disable sound beeps.
    """
    print("=" * 70)
    print("  VisionGuard: AI-Based Driver Drowsiness & Distraction Detection")
    print("  Terminal CLI Execution Mode (VITyarthi Project Evaluation)")
    print("=" * 70)
    print(f"[*] Initializing video source: {source}")
    print(f"[*] Max duration: {duration} seconds (0 = run until interrupted)")
    print(f"[*] Audio alerts: {'Disabled' if no_audio else 'Enabled'}")
    print("-" * 70)

    config = AppConfig()
    if no_audio:
        config.alert.enable_audio = False

    # Initialize modules
    video_stream = VideoStream(source=source)
    if not video_stream.start():
        print(f"[ERROR] Failed to open video source: {source}")
        print("  - If using a physical webcam, verify permissions in macOS System Settings.")
        print("  - Or pass a test video: python cli.py --source /path/to/test.mp4")
        sys.exit(1)

    print("[*] Loading MediaPipe FaceMesh model...")
    face_detector = FaceLandmarkDetector(
        min_detection_confidence=config.min_detection_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
    )
    eye_detector = EyeDetector(config.eye)
    head_pose = HeadPoseEstimator(config.head_pose)
    risk_engine = RiskEngine(config.risk)
    alert_manager = AlertManager(config.alert)
    analytics = SessionAnalytics()
    analytics.start_session()

    print("[*] Pipeline running. Processing frames...\n")
    print(f"{'SEC':<6} | {'FPS':<5} | {'STATUS':<11} | {'RISK%':<6} | {'EAR':<6} | {'POSE':<8} | {'BLINKS':<6} | {'ALERTS'}")
    print("-" * 70)

    start_time = time.time()
    last_print = 0

    try:
        while True:
            elapsed = time.time() - start_time
            if duration > 0 and elapsed >= duration:
                print(f"\n[*] Target duration ({duration}s) reached.")
                break

            success, frame = video_stream.read_frame()
            if not success or frame is None:
                print("\n[*] End of video stream or camera disconnected.")
                break

            # 1. Face landmarks
            landmarks_px, _, face_detected = face_detector.process_frame(frame)

            # 2. Eyes
            eye_data = eye_detector.process_eyes(landmarks_px)

            # 3. Yawn (using placeholder empty mouth for speed in CLI if needed)
            yawn_data = {"mar": 0.0, "is_yawning": False, "is_mouth_open": False, "total_yawns": 0}

            # 4. Pose
            pose_data = head_pose.estimate_pose(landmarks_px, frame.shape)

            # 5. Risk
            risk_data = risk_engine.assess_risk(
                eye_data=eye_data,
                yawn_data=yawn_data,
                pose_data=pose_data,
                face_detected=face_detected,
            )

            # 6. Alerts
            alert_info = alert_manager.update_alert(risk_data["state"], risk_data["risk_score"])

            # 7. Analytics
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

            # Console telemetry output every 0.5s
            if time.time() - last_print >= 0.5:
                last_print = time.time()
                alert_flag = "BEEP" if alert_info["audio_triggered"] else "-"
                print(
                    f"{elapsed:5.1f}s | {video_stream.get_fps():4.1f} | "
                    f"{risk_data['state']:<11} | {risk_data['risk_score']:5.1f}% | "
                    f"{eye_data['avg_ear']:5.3f} | {pose_data['direction']:<8} | "
                    f"{eye_data['total_blinks']:<6} | {alert_flag}"
                )

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user (Ctrl+C).")
    finally:
        video_stream.stop()
        face_detector.close()
        analytics.end_session()

    print("-" * 70)
    print("\n" + "=" * 70)
    print("  SESSION SUMMARY & ANALYTICS")
    print("=" * 70)
    summary = analytics.get_summary()
    for k, v in summary.items():
        label = k.replace("_", " ").title()
        print(f"  • {label:<32}: {v}")

    # Export logs
    os.makedirs(os.path.join(CURRENT_DIR, "data", "sample_sessions"), exist_ok=True)
    csv_out = os.path.join(CURRENT_DIR, "data", "sample_sessions", f"{export_prefix}.csv")
    json_out = os.path.join(CURRENT_DIR, "data", "sample_sessions", f"{export_prefix}.json")
    analytics.export_csv(csv_out)
    analytics.export_json(json_out)
    print(f"\n[✓] Telemetry exported to: {csv_out}")
    print(f"[✓] Summary exported to:   {json_out}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="VisionGuard – CLI Driver Drowsiness & Distraction Detection"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Camera device index (default: 0) or path to a video file (.mp4, .avi)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=15,
        help="Duration to run monitoring in seconds (default: 15, 0 = infinite)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="cli_session",
        help="Prefix filename for exported CSV/JSON logs",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audible beep alerts",
    )
    args = parser.parse_args()

    # Convert integer source if numeric
    source = int(args.source) if args.source.isdigit() else args.source
    run_cli(
        source=source,
        duration=args.duration,
        export_prefix=args.prefix,
        no_audio=args.no_audio,
    )


if __name__ == "__main__":
    main()
