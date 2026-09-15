#!/usr/bin/env python3
"""ErgoVision - AI-Powered Ergonomic Posture & Screen Fatigue Monitor.

Student Name: Aditi Prakash
Course: Computer Vision Project (VITyarthi)

Usage:
    python3 main.py           # Launches interactive live OpenCV visual window with HUD
    python3 main.py --cli     # Runs in pure terminal streaming mode
"""

import argparse
import os
import sys
import time
import warnings
import cv2
import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["GLOG_minloglevel"] = "3"
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.config import ErgoAppConfig
from src.camera import VideoStream
from src.face_detector import FaceLandmarkDetector
from src.posture_detector import PostureDetector
from src.distance_estimator import DistanceEstimator
from src.fatigue_tracker import FatigueTracker
from src.analytics import ErgoAnalytics
from src.utils import draw_ergo_hud

DEFAULT_VIDEO = os.path.join(CURRENT_DIR, "data", "sample_video.mp4")


def resolve_video_stream(source):
    stream = VideoStream(source=source)
    if stream.start():
        return stream, source, False

    if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
        print("\n[!] Camera not directly accessible. Engaging bundled test video.")
        fallback = VideoStream(source=DEFAULT_VIDEO)
        if fallback.start():
            return fallback, DEFAULT_VIDEO, True

    return None, source, False


def run_visual(source=0, duration=0):
    print("=" * 72)
    print("  ErgoVision: Ergonomic Posture & Screen Fatigue Monitoring System")
    print("  Student: Aditi Prakash | VITyarthi Computer Vision Project")
    print("  Interactive Visual Window Mode (Press 'q' or ESC to stop)")
    print("=" * 72)

    stream, active_source, is_fallback = resolve_video_stream(source)
    if stream is None:
        print(f"[ERROR] Could not open video source: {source}")
        sys.exit(1)

    print(f"[*] Video Source : {active_source}")
    print("[*] Controls     : Press 'q' or ESC on the video window to finish.\n")

    cfg = ErgoAppConfig()
    detector = FaceLandmarkDetector()
    posture = PostureDetector(cfg.posture)
    distance = DistanceEstimator(cfg.distance)
    fatigue = FatigueTracker(cfg.fatigue)
    analytics = ErgoAnalytics()
    analytics.start_session()

    win_name = "ErgoVision - Posture & Fatigue Monitor (Aditi Prakash)"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 800, 600)

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
                    stream.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    success, frame = stream.read_frame()
                    if not success:
                        break
                else:
                    break

            h, w, _ = frame.shape
            landmarks, found = detector.process_frame(frame)

            p_data = posture.analyze_posture(landmarks, frame.shape)
            d_data = distance.estimate_distance(landmarks, w)
            f_data = fatigue.process_eyes(landmarks)

            analytics.update(
                posture_status=p_data["posture_status"],
                is_slouching=p_data["is_slouching"],
                is_too_close=d_data["is_too_close"],
                ear=f_data["ear"],
                blinks=f_data["total_blinks"],
            )

            annotated = frame.copy()
            if found and landmarks is not None:
                # Draw key posture points (chin, forehead, nose, eyes)
                for idx in [1, 10, 33, 263, 152]:
                    pt = (int(landmarks[idx][0]), int(landmarks[idx][1]))
                    cv2.circle(annotated, pt, 3, (0, 255, 255), -1, cv2.LINE_AA)

            annotated = draw_ergo_hud(
                frame=annotated,
                posture_status=p_data["posture_status"],
                neck_tilt=p_data["neck_tilt_deg"],
                lateral_tilt=p_data["lateral_tilt_deg"],
                dist_status=d_data["proximity_status"],
                dist_cm=d_data["estimated_distance_cm"],
                ear=f_data["ear"],
                blinks_per_min=f_data["blinks_per_min"],
                fps=stream.get_fps(),
            )

            cv2.imshow(win_name, annotated)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                print("\n[*] Monitoring stopped by user.")
                break

    except KeyboardInterrupt:
        print("\n[*] Stopped (Ctrl+C).")
    finally:
        stream.stop()
        cv2.destroyAllWindows()
        detector.close()
        analytics.end_session()

    print_summary(analytics)


def print_summary(analytics):
    print("\n" + "=" * 72)
    print("  ERGOVISION - POST-SESSION WORKSPACE REPORT")
    print("  Student: Aditi Prakash")
    print("=" * 72)
    summary = analytics.get_summary()
    for k, v in summary.items():
        label = k.replace("_", " ").title()
        print(f"  • {label:<32}: {v}")

    out_csv = os.path.join(CURRENT_DIR, "data", "sample_sessions", "latest_session.csv")
    out_json = os.path.join(CURRENT_DIR, "data", "sample_sessions", "latest_session.json")
    analytics.export_csv(out_csv)
    analytics.export_json(out_json)
    print("-" * 72)
    print(f"[✓] Exported telemetry CSV : {out_csv}")
    print(f"[✓] Exported session JSON  : {out_json}")
    print("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description="ErgoVision – Posture & Fatigue Monitor")
    parser.add_argument("--source", type=str, default="0", help="Camera index or video file")
    parser.add_argument("--cli", action="store_true", help="Run in headless terminal mode")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    if args.cli:
        from cli import run_cli
        run_cli(source=source, duration=args.duration if args.duration > 0 else 15)
    else:
        run_visual(source=source, duration=args.duration)


if __name__ == "__main__":
    main()
