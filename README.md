# VisionGuard – AI-Based Driver Drowsiness and Distraction Detection System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-00C7B7)](https://developers.google.com/mediapipe)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-brightgreen)](tests/)

> **VITyarthi "Build Your Own Project" Flipped Course Capstone**  
> **Course Domain:** Computer Vision / Applied Machine Learning  
> **Author:** Yash Goyal  

---

## 1. Overview
**VisionGuard** is an end-to-end, real-time Computer Vision system designed to monitor driver alertness, detect early signs of physiological fatigue, and identify visual inattention. By analyzing real-time video streams from a consumer webcam or vehicle-mounted camera, VisionGuard computes dense facial geometry, evaluates eye and mouth aspect ratios, estimates 3D head orientation via Perspective-n-Point (SolvePnP), and issues multi-tier visual and auditory safety alerts.

Unlike basic black-box classifiers or static image-processing demos, VisionGuard is grounded in classical and modern geometric Computer Vision principles with transparent, mathematically defensible biomechanical models.

---

## 2. Problem Statement
Driver drowsiness, micro-sleep episodes, and visual distraction account for over 20% of fatal automotive accidents worldwide. Traditional vehicular telemetry (such as lane deviation or erratic steering) only registers an issue *after* the vehicle has dangerously drifted. VisionGuard provides proactive in-cabin visual monitoring, detecting cognitive fatigue and diverted gaze seconds before an incident occurs.

---

## 3. Objectives
* Extract 468 3D facial landmarks at real-time speeds ($\ge 25$ FPS) using MediaPipe FaceMesh.
* Formulate scale- and illumination-invariant **Eye Aspect Ratio (EAR)** for blink tracking and prolonged eye closure detection.
* Formulate **Mouth Aspect Ratio (MAR)** with temporal persistence filtering to identify yawning while rejecting normal conversational speech.
* Implement **3D Perspective-n-Point (SolvePnP)** rigid head pose estimation to calculate Pitch, Yaw, and Roll for distraction detection.
* Fuse multi-modal cues into a composite **Risk Assessment Engine** with exponential moving average (EMA) smoothing.
* Present live telemetry via a glassmorphic **Streamlit HUD** with non-blocking audio cues and exportable session telemetry (CSV/JSON).

---

## 4. Key Features
* 👁️ **Blink & Drowsiness Tracker:** Distinguishes rapid intentional blinks from hazardous prolonged closures ($>0.5$s).
* 🥱 **Yawn Persistence Filter:** Eliminates false alarms caused by talking or smiling through temporal verification.
* 🧭 **3D Gaze Ray & Pose Estimation:** Projects a real-time 3D directional gaze vector from the driver's nose tip.
* 🛡️ **Multi-Tier Safety State Hierarchy:** Classifies driver status into `SAFE`, `CAUTION`, `DROWSY`, `DISTRACTED`, and `HIGH RISK`.
* 🔔 **Smart Rate-Limited Audio Alerts:** Non-blocking platform audio beeps with cooldown to prevent driver annoyance.
* 📊 **Post-Session Analytics & Export:** One-click generation of driving summaries and detailed timeseries datasets.

---

## 5. Functional Modules

```
VisionGuard Core Pipeline
│
├── Module 1: VideoStream (camera.py) ────────► OpenCV frame capture, reconnection & FPS
├── Module 2: FaceLandmarkDetector (face_detector.py) ─► MediaPipe 468 3D facial landmarks
├── Module 3: EyeDetector (eye_detector.py) ────────► 6-point EAR, blink count & closure
├── Module 4: YawnDetector (yawn_detector.py) ──────► MAR formulation & temporal yawn filter
├── Module 5: HeadPoseEstimator (head_pose.py) ────► 3D-to-2D SolvePnP & Euler angles
├── Module 6: RiskEngine (risk_engine.py) ──────────► Multi-cue linear fusion & EMA smoothing
├── Module 7: AlertManager (alert_manager.py) ──────► Visual badges & threaded audio beeps
└── Module 8: SessionAnalytics (analytics.py) ─────► Timeseries logging, KPIs & CSV/JSON export
```

---

## 6. Technologies Used
* **Programming Language:** Python 3.11
* **Computer Vision & Video:** OpenCV (`opencv-python`), MediaPipe FaceMesh
* **Numerical Mathematics:** NumPy, SciPy
* **Data Processing & Analytics:** Pandas
* **User Interface:** Streamlit (Custom Dark Glassmorphic CSS)
* **Automated Testing:** Pytest
* **Report Compilation:** ReportLab (PDF Generation)

---

## 7. System Requirements
* **Operating System:** macOS (Apple Silicon / Intel), Windows 10/11, Ubuntu 20.04+
* **Processor:** Intel Core i5 / AMD Ryzen 5 / Apple M1 or higher
* **Memory (RAM):** 4 GB minimum (8 GB recommended)
* **Camera:** Standard 720p USB webcam or integrated laptop camera
* **Python Version:** Python 3.9 – 3.11

---

## 8. Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/VisionGuard.git
cd VisionGuard

# 2. (Optional but recommended) Create virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 9. How to Run the Application

```bash
# Launch the interactive Streamlit dashboard
streamlit run app.py
```

The web interface will open automatically in your default browser at `http://localhost:8501`.

### Operating Instructions:
1. Select your video stream source (Hardware Webcam or Upload Video Clip).
2. Adjust biometric thresholds in the left sidebar if needed (or keep recommended defaults).
3. Click **▶ Start Monitoring** to begin live real-time analysis.
4. When finished, click **⏹ Stop Monitoring** to view session analytics and download the CSV/JSON telemetry logs.

---

## 10. Computer Vision Algorithms & Mathematics

### Eye Aspect Ratio (EAR)
$$\text{EAR} = \frac{\|p_2 - p_6\| + \|p_3 - p_5\|}{2 \cdot \|p_1 - p_4\|}$$
* Normal open eye: $\text{EAR} \approx 0.28 - 0.38$
* Closed eye: $\text{EAR} < 0.22$
* Sustained closure $\ge 15$ frames triggers `DROWSY` state.

### Mouth Aspect Ratio (MAR)
$$\text{MAR} = \frac{\|p_{\text{top}} - p_{\text{bottom}}\| + \|p_{\text{mid\_top}} - p_{\text{mid\_bottom}}\|}{2 \cdot \|p_{\text{left}} - p_{\text{right}}\|}$$
* Resting/speaking mouth: $\text{MAR} < 0.50$
* Yawning mouth: $\text{MAR} \ge 0.60$ for $\ge 15$ continuous frames.

### 3D Head Pose (Perspective-n-Point)
Solves the world-to-camera coordinate transformation:
$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \mathbf{K} [\mathbf{R} \mid \mathbf{t}] \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}$$
Extracts Pitch ($\theta_x$), Yaw ($\theta_y$), and Roll ($\theta_z$). Head turns exceeding $|\theta_y| > 25^\circ$ for $>20$ frames trigger `DISTRACTED`.

---

## 11. Testing & Verification

Run the automated Pytest test suite:
```bash
pytest tests/ -v
```

All 18 unit tests cover:
* Geometric distance calculations and EAR/MAR bounds
* Blink identification vs. prolonged closure transitions
* Yawn temporal persistence and speech false-alarm rejection
* 3D SolvePnP pose estimation and Euler angle extraction
* Multi-cue risk scoring and state hierarchy escalation
* Timeseries telemetry aggregation and CSV/JSON file generation

---

## 12. Non-Functional Requirements Summary
* **Performance:** Real-time processing at $25 - 30$ FPS with $<40$ms per-frame latency.
* **Usability:** Single-click startup, intuitive glassmorphic dashboard, responsive layout, and configurable sliders.
* **Reliability:** Exception-safe architecture that handles camera disconnections, face loss, and occlusions gracefully without crashing.
* **Resource Efficiency:** Lightweight CPU execution utilizing $<15\%$ CPU and $<350$ MB RAM.
* **Maintainability:** Strict PEP-8 adherence, modular package hierarchy, and zero magic numbers.

---

## 13. Limitations
* **Illumination Dependency:** Performance degrades in pitch-black environments when using standard visible-spectrum RGB webcams (mitigated by near-infrared hardware in commercial DMS).
* **Extreme Angles:** Face profile turns beyond $\pm 45^\circ$ may cause partial landmark occlusion.
* **Eyewear:** Highly reflective sunglasses or thick frames may reduce ocular landmark precision.

---

## 14. Ethical & Safety Positioning
> [!IMPORTANT]
> **Academic Prototype Notice:** VisionGuard is developed strictly as an academic Computer Vision prototype for student research and evaluation. It is **not** a certified automotive safety system (such as ISO 26262 ASIL-D) and does **not** provide medical diagnosis of sleep disorders or guarantee collision avoidance. All video frames are processed locally in memory; no user imagery is transmitted or stored externally.

---

## 15. Team & Course Information
* **Course:** VITyarthi - Build Your Own Project (Computer Vision / Applied AI)
* **Student Name:** Yash Goyal
* **Institution:** Vellore Institute of Technology (VIT)
* **License:** MIT License (see [LICENSE](LICENSE))
