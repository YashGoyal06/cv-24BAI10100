"""VisionGuard - AI-Based Driver Drowsiness and Distraction Detection System.

Main application dashboard built with Streamlit and OpenCV.
Provides live camera processing, heads-up display, configurable CV thresholds,
real-time safety status classification, and session analytics export.
"""

import os
import sys
import time
import tempfile
import cv2
import numpy as np
import pandas as pd
import streamlit as st

# Add project root to sys.path for robust imports
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


# Page layout and aesthetics
st.set_page_config(
    page_title="VisionGuard | AI Driver Safety System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End Modern Styling
st.markdown(
    """
    <style>
    /* Dark glassmorphic theme styling */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #f3f4f6;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 12px;
    }
    .status-badge-safe {
        background-color: #10b981;
        color: #ffffff;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
        display: inline-block;
    }
    .status-badge-caution {
        background-color: #f59e0b;
        color: #ffffff;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
        display: inline-block;
    }
    .status-badge-drowsy {
        background-color: #f97316;
        color: #ffffff;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
        display: inline-block;
    }
    .status-badge-distracted {
        background-color: #8b5cf6;
        color: #ffffff;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
        display: inline-block;
    }
    .status-badge-high-risk {
        background-color: #ef4444;
        color: #ffffff;
        font-weight: 800;
        padding: 6px 14px;
        border-radius: 8px;
        display: inline-block;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.04); }
        100% { transform: scale(1); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize Streamlit state variables."""
    if "config" not in st.session_state:
        st.session_state.config = AppConfig()
    if "analytics" not in st.session_state:
        st.session_state.analytics = SessionAnalytics()
    if "is_monitoring" not in st.session_state:
        st.session_state.is_monitoring = False
    if "last_summary" not in st.session_state:
        st.session_state.last_summary = None


def render_sidebar():
    """Render interactive sidebar with configurable CV parameters and info."""
    st.sidebar.title("🛡️ VisionGuard")
    st.sidebar.caption("VITyarthi CV Capstone | Driver Safety System")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Detection Parameters")

    # EAR configuration
    ear_thresh = st.sidebar.slider(
        "Eye Aspect Ratio (EAR) Threshold",
        min_value=0.15,
        max_value=0.35,
        value=st.session_state.config.eye.ear_threshold,
        step=0.01,
        help="EAR below this indicates eye closure (Soukupová & Čech, 2016)",
    )
    st.session_state.config.eye.ear_threshold = ear_thresh

    eye_frames = st.sidebar.slider(
        "Prolonged Eye Closure Frames",
        min_value=5,
        max_value=40,
        value=st.session_state.config.eye.eye_closed_consec_frames,
        step=1,
        help="Consecutive frames of eye closure to trigger drowsiness alarm (~30fps)",
    )
    st.session_state.config.eye.eye_closed_consec_frames = eye_frames

    # MAR configuration
    mar_thresh = st.sidebar.slider(
        "Mouth Aspect Ratio (MAR) Threshold",
        min_value=0.40,
        max_value=0.85,
        value=st.session_state.config.yawn.mar_threshold,
        step=0.02,
        help="MAR above this indicates mouth wide open",
    )
    st.session_state.config.yawn.mar_threshold = mar_thresh

    # Head pose angles
    yaw_thresh = st.sidebar.slider(
        "Head Turn (Yaw) Threshold (°)",
        min_value=15.0,
        max_value=45.0,
        value=st.session_state.config.head_pose.yaw_threshold,
        step=1.0,
        help="Degrees of head rotation away from windshield before distraction warning",
    )
    st.session_state.config.head_pose.yaw_threshold = yaw_thresh

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 Alert Configuration")
    enable_audio = st.sidebar.checkbox(
        "Enable Audible Alerts",
        value=st.session_state.config.alert.enable_audio,
        help="Play non-blocking auditory cues during critical events",
    )
    st.session_state.config.alert.enable_audio = enable_audio

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 0.8rem; color: #94a3b8;">
        <b>Academic Project Notice:</b><br/>
        VisionGuard is an academic Computer Vision prototype for driver assistance research.
        It does not diagnose medical conditions or guarantee crash prevention.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    """Main application loop and UI coordinator."""
    init_session_state()
    render_sidebar()

    st.title("VisionGuard – Driver Drowsiness & Distraction Detection")
    st.markdown(
        "**Real-time Computer Vision Pipeline** analyzing facial landmarks, "
        "Eye Aspect Ratio (EAR), Mouth Aspect Ratio (MAR), and 3D Head Pose orientation via SolvePnP."
    )

    # Top KPI summary cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(
            '<div class="metric-card"><h4>Safety Status</h4><div id="status_text" style="font-size:1.4rem; font-weight:700;">STANDBY</div></div>',
            unsafe_allow_html=True,
        )
    with kpi_col2:
        st.markdown(
            '<div class="metric-card"><h4>Composite Risk</h4><div style="font-size:1.4rem; font-weight:700; color:#38bdf8;">0%</div></div>',
            unsafe_allow_html=True,
        )
    with kpi_col3:
        st.markdown(
            '<div class="metric-card"><h4>Total Blinks</h4><div style="font-size:1.4rem; font-weight:700; color:#a7f3d0;">0</div></div>',
            unsafe_allow_html=True,
        )
    with kpi_col4:
        st.markdown(
            '<div class="metric-card"><h4>Total Yawns</h4><div style="font-size:1.4rem; font-weight:700; color:#fde047;">0</div></div>',
            unsafe_allow_html=True,
        )

    # Controls row
    col_btn1, col_btn2, col_src, _ = st.columns([1.5, 1.5, 3, 2])
    with col_btn1:
        start_clicked = st.button(
            "▶ Start Monitoring",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.is_monitoring,
        )
    with col_btn2:
        stop_clicked = st.button(
            "⏹ Stop Monitoring",
            use_container_width=True,
            disabled=not st.session_state.is_monitoring,
        )
    with col_src:
        input_mode = st.selectbox(
            "Video Stream Source",
            options=["Hardware Webcam (Default Index 0)", "Upload Video Clip"],
            index=0,
        )

    uploaded_video_file = None
    if input_mode == "Upload Video Clip":
        uploaded_video_file = st.file_uploader(
            "Upload MP4/AVI driving test clip", type=["mp4", "avi", "mov"]
        )

    if start_clicked:
        st.session_state.is_monitoring = True
        st.session_state.analytics.start_session()
        st.session_state.last_summary = None
        st.rerun()

    if stop_clicked:
        st.session_state.is_monitoring = False
        st.session_state.analytics.end_session()
        st.session_state.last_summary = st.session_state.analytics.get_summary()
        st.rerun()

    # Video Feed Display and Live Monitoring Loop
    video_col, telemetry_col = st.columns([3, 2])

    with video_col:
        st.subheader("📹 Live Video Feed")
        frame_placeholder = st.empty()

    with telemetry_col:
        st.subheader("📊 Live Telemetry & Biometrics")
        telemetry_placeholder = st.empty()

    # Active Monitoring Execution
    if st.session_state.is_monitoring:
        # Determine source
        source = 0
        temp_video_path = None
        if input_mode == "Upload Video Clip":
            if uploaded_video_file is None:
                st.warning("Please upload a video file to proceed or select Hardware Webcam.")
                st.session_state.is_monitoring = False
                return
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_video_file.read())
            temp_video_path = tfile.name
            source = temp_video_path

        # Initialize detector modules
        cfg = st.session_state.config
        face_detector = FaceLandmarkDetector(
            min_detection_confidence=cfg.min_detection_confidence,
            min_tracking_confidence=cfg.min_tracking_confidence,
        )
        eye_detector = EyeDetector(cfg.eye)
        yawn_detector = YawnDetector(cfg.yawn)
        head_pose = HeadPoseEstimator(cfg.head_pose)
        risk_engine = RiskEngine(cfg.risk)
        alert_manager = AlertManager(cfg.alert)
        analytics = st.session_state.analytics

        video_stream = VideoStream(source=source)
        opened = video_stream.start()

        if not opened:
            st.error(
                "❌ Could not access video source. Check webcam permissions in macOS "
                "System Settings -> Privacy & Security -> Camera."
            )
            st.session_state.is_monitoring = False
            return

        try:
            while st.session_state.is_monitoring:
                success, frame = video_stream.read_frame()
                if not success or frame is None:
                    # End of video file or camera disconnect
                    break

                # Step 1: Detect face & landmarks
                landmarks_px, _, face_detected = face_detector.process_frame(frame)

                # Step 2: Extract Eye features
                eye_data = eye_detector.process_eyes(landmarks_px)

                # Step 3: Extract Yawn features
                yawn_data = yawn_detector.process_mouth(landmarks_px)

                # Step 4: Estimate 3D Head Pose
                pose_data = head_pose.estimate_pose(landmarks_px, frame.shape)

                # Step 5: Composite Risk Evaluation
                risk_data = risk_engine.assess_risk(
                    eye_data=eye_data,
                    yawn_data=yawn_data,
                    pose_data=pose_data,
                    face_detected=face_detected,
                )

                # Step 6: Dispatch Alerts
                alert_manager.update_alert(risk_data["state"], risk_data["risk_score"])

                # Step 7: Update Analytics
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

                # Step 8: Render Overlays & HUD
                annotated_frame = frame.copy()
                if face_detected and landmarks_px is not None:
                    # Draw subtle key landmarks
                    annotated_frame = face_detector.draw_landmarks_on_frame(
                        annotated_frame,
                        landmarks_px,
                        indices=cfg.eye.left_eye_indices
                        + cfg.eye.right_eye_indices
                        + cfg.yawn.mouth_indices
                        + [1, 152],
                    )
                    # Draw 3D gaze ray if available
                    if pose_data["nose_2d"] and pose_data["nose_3d_proj"]:
                        cv2.line(
                            annotated_frame,
                            pose_data["nose_2d"],
                            pose_data["nose_3d_proj"],
                            (255, 180, 0),
                            2,
                            cv2.LINE_AA,
                        )

                # Render HUD bar
                fps = video_stream.get_fps()
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
                    fps=fps,
                )

                # Convert to RGB for Streamlit rendering
                rgb_display = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(
                    rgb_display, channels="RGB", use_container_width=True
                )

                # Update live telemetry pane
                with telemetry_placeholder.container():
                    st.metric(
                        label="Driver Safety State",
                        value=risk_data["state"],
                        delta=f"Risk Score: {risk_data['risk_score']:.1f}%",
                    )
                    m1, m2 = st.columns(2)
                    m1.metric("Eye Aspect Ratio (EAR)", f"{eye_data['avg_ear']:.3f}")
                    m2.metric("Mouth Aspect Ratio (MAR)", f"{yawn_data['mar']:.3f}")

                    m3, m4 = st.columns(2)
                    m3.metric("Head Pose Direction", pose_data["direction"])
                    m4.metric(
                        "Orientation (P/Y/R)",
                        f"{pose_data['pitch']:.0f}° / {pose_data['yaw']:.0f}° / {pose_data['roll']:.0f}°",
                    )

                    st.progress(
                        min(max(risk_data["risk_score"] / 100.0, 0.0), 1.0),
                        text=f"Hazard Index: {risk_data['risk_score']:.1f}%",
                    )

                time.sleep(0.01)

        finally:
            video_stream.stop()
            face_detector.close()
            if temp_video_path and os.path.exists(temp_video_path):
                os.remove(temp_video_path)

    # Post-Session Analytics Display & Export
    if st.session_state.last_summary:
        st.markdown("---")
        st.header("📈 Session Analytics & Post-Drive Evaluation")
        summary = st.session_state.last_summary

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Session Duration", summary["session_duration_formatted"])
        r2.metric("Safe Time %", f"{summary['safe_time_percentage']}%")
        r3.metric("Drowsy Time %", f"{summary['drowsy_time_percentage']}%")
        r4.metric("Distracted Time %", f"{summary['distracted_time_percentage']}%")

        r5, r6, r7, r8 = st.columns(4)
        r5.metric("Total Blinks", summary["total_blinks"])
        r6.metric("Blink Rate (per min)", summary["blinks_per_minute"])
        r7.metric("Prolonged Eye Closures", summary["prolonged_closure_events"])
        r8.metric("Confirmed Yawns", summary["total_yawns"])

        # Export buttons
        exp_col1, exp_col2, _ = st.columns([2, 2, 4])
        with exp_col1:
            csv_path = os.path.join(
                CURRENT_DIR, "data", "sample_sessions", "latest_session.csv"
            )
            st.session_state.analytics.export_csv(csv_path)
            with open(csv_path, "rb") as f:
                st.download_button(
                    "📥 Export Session Telemetry (CSV)",
                    data=f,
                    file_name="visionguard_session_telemetry.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        with exp_col2:
            json_path = os.path.join(
                CURRENT_DIR, "data", "sample_sessions", "latest_session.json"
            )
            st.session_state.analytics.export_json(json_path)
            with open(json_path, "rb") as f:
                st.download_button(
                    "📄 Export Summary Report (JSON)",
                    data=f,
                    file_name="visionguard_session_summary.json",
                    mime="application/json",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
