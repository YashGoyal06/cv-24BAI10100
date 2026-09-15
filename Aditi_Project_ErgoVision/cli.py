#!/usr/bin/env python3
"""ErgoVision - Standalone Terminal CLI Interface.

Student Name: Aditi Prakash
"""

import argparse
import os
import sys
import time
import warnings
import cv2

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

DEFAULT_VIDEO = os.path.join(CURRENT_DIR, "data", "sample_video.mp4")


def resolve_video_stream(source):
    stream = VideoStream(source=source)
    if stream.start():
        return stream, source, False
    if isinstance(source, int) or (isinstance(source, str) and source.isdigit()):
        fallback = VideoStream(source=DEFAULT_VIDEO)
        if fallback.start():
            return fallback, DEFAULT_VIDEO, True
    return None, source, False


def run_cli(source=0, duration=15):
    print("=" * 72)
    print("  ErgoVision: Posture & Screen Fatigue CLI (Aditi Prakash)")
    print("=" * 72)

    stream, active_source, is_fallback = resolve_video_stream(source)
    if stream is None:
        print(f"[ERROR] Could not open source: {source}")
        sys.exit(1)

    print(f"[*] Source   : {active_source}")
    print(f"[*] Duration : {duration}s\n")

    cfg = ErgoAppConfig()
    detector = FaceLandmarkDetector()
    posture = PostureDetector(cfg.posture)
    distance = DistanceEstimator(cfg.distance)
    fatigue = FatigueTracker(cfg.fatigue)
    analytics = ErgoAnalytics()
    analytics.start_session()

    start_time = time.time()
    last_print = 0.0

    print("SEC    | FPS   | POSTURE STATUS        | SCREEN DISTANCE | BLINKS/MIN")
    print("-" * 72)

    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= duration:
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

            landmarks, found = detector.process_frame(frame)
            p_data = posture.analyze_posture(landmarks, frame.shape)
            d_data = distance.estimate_distance(landmarks, frame.shape[1])
            f_data = fatigue.process_eyes(landmarks)

            analytics.update(
                posture_status=p_data["posture_status"],
                is_slouching=p_data["is_slouching"],
                is_too_close=d_data["is_too_close"],
                ear=f_data["ear"],
                blinks=f_data["total_blinks"],
            )

            if elapsed - last_print >= 0.5:
                print(
                    f"{elapsed:5.1f}s | {stream.get_fps():4.1f} | "
                    f"{p_data['posture_status']:<21} | "
                    f"{d_data['proximity_status']:<15} | "
                    f"{f_data['blinks_per_min']:4.1f}"
                )
                last_print = elapsed

    except KeyboardInterrupt:
        print("\n[*] Interrupted.")
    finally:
        stream.stop()
        detector.close()
        analytics.end_session()

    print("\n" + "=" * 72)
    print("  ERGOVISION POST-SESSION SUMMARY")
    print("=" * 72)
    for k, v in analytics.get_summary().items():
        print(f"  • {k:<25}: {v}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="0")
    parser.add_argument("--duration", type=int, default=15)
    args = parser.parse_args()
    source = int(args.source) if args.source.isdigit() else args.source
    run_cli(source=source, duration=args.duration)
