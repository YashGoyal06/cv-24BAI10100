<div align="center">

<br/>

# VisionGuard

### — AI-Based Driver Drowsiness and Distraction Detection System —

<br/>

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh%20468-00C7B7?style=flat-square)](https://developers.google.com/mediapipe)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![CLI](https://img.shields.io/badge/Interface-CLI%20%2B%20Web-555555?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-2ea44f?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-17%20Passed-brightgreen?style=flat-square)](tests/)

<br/>

```
  Facial Landmarks  ·  Eye Aspect Ratio  ·  Yawn Analysis  ·  3D Head Pose  ·  Risk Scoring
```

<br/>

</div>

---

## About the Project

**VisionGuard** is an end-to-end, edge-computing Computer Vision application designed to monitor driver alertness in real time, detect physiological drowsiness, and identify cognitive or visual distraction. Operating from a live video stream (webcam or video file), VisionGuard extracts 468 3D facial landmarks, computes scale-invariant ocular and oral geometry, estimates 3D head orientation via Perspective-n-Point (SolvePnP), and issues multi-tier visual and auditory hazard alerts.

The project is structured specifically for the **VITyarthi "Build Your Own Project" Flipped Course Evaluation**, demonstrating rigorous mathematical Computer Vision fundamentals, modular software architecture, comprehensive unit testing, and full command-line terminal executability.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Getting Started](#getting-started)
- [Usage (CLI & Web)](#usage-cli--web)
- [Computer Vision Algorithms](#computer-vision-algorithms)
- [System Diagrams](#system-diagrams)
- [Screenshots](#screenshots)
- [Non-Functional Requirements](#non-functional-requirements)
- [Testing](#testing)
- [Author](#author)

---

## Features

**Face & Landmark Localization**  
Tracks 468 dense 3D facial landmarks in real time using MediaPipe FaceMesh, mapping normalized coordinates to image pixel space with robust handling of temporary facial loss.

**Eye Aspect Ratio (EAR) & Blink Tracking**  
Implements the 6-point EAR formula (Soukupová & Čech, 2016) to calculate eyelid aperture, record intentional blinks ($1-4$ frames), compute blink rates, and detect micro-sleep episodes ($\ge 15$ frames).

**Mouth Aspect Ratio (MAR) & Yawn Detection**  
Calculates oral aperture relative to mouth width, filtering out transient speech and smiles via a 15-frame temporal persistence buffer and cooldown timer.

**3D Head Pose & Distraction Estimation**  
Applies OpenCV's `solvePnP` using canonical anthropometric 3D facial coordinates to compute Euler angles (Pitch, Yaw, Roll), project a 3D directional gaze ray, and alert when the driver's head turns away ($|\theta_{\text{yaw}}| > 25^\circ$).

**Multi-Cue Risk Assessment Engine**  
Combines ocular, oral, spatial, and blink cues into a linear hazard score with Exponential Moving Average (EMA) smoothing ($\alpha = 0.25$), categorizing status into `SAFE`, `CAUTION`, `DROWSY`, `DISTRACTED`, and `HIGH RISK`.

**Debounced Auditory Alert System**  
Dispatches priority-tiered acoustic alarms via non-blocking background threads with a 2.0-second cooldown to avoid continuous sound spamming.

**Dual Execution Modes: Web & Terminal CLI**  
Fully executable via an interactive dark glassmorphic Streamlit dashboard (`app.py`) as well as a standalone terminal command-line tool (`cli.py`) for automated/headless evaluation.

**Session Analytics & Data Persistence**  
Logs granular frame-level telemetry and generates one-click exports to structured CSV and JSON datasets.

---

## Project Structure

```
VisionGuard/
│
├── src/
│   ├── config.py                 # Centralized thresholds & configuration dataclasses
│   ├── camera.py                 # OpenCV VideoStream frame acquisition & FPS tracker
│   ├── face_detector.py          # MediaPipe FaceMesh 468 3D landmark extractor
│   ├── eye_detector.py           # 6-point EAR calculation & blink/closure detector
│   ├── yawn_detector.py          # MAR calculation & temporal yawn persistence filter
│   ├── head_pose.py              # 3D SolvePnP pose estimation & Euler angle calculator
│   ├── risk_engine.py            # Multi-cue hazard scoring & EMA temporal smoothing
│   ├── alert_manager.py          # Threaded non-blocking audio alarm dispatcher
│   ├── analytics.py              # Telemetry collector & CSV/JSON exporter
│   └── utils.py                  # Euclidean distance math & Heads-Up Display (HUD)
│
├── tests/
│   ├── test_eye_detector.py      # Unit tests for EAR, distance math & blink logic
│   ├── test_yawn_detector.py     # Unit tests for MAR & speech rejection
│   ├── test_head_pose.py         # Unit tests for 3D SolvePnP & orientation dict
│   ├── test_risk_engine.py       # Unit tests for risk state transitions
│   └── test_analytics.py         # Unit tests for session telemetry & file export
│
├── data/
│   └── sample_sessions/          # Directory for exported session logs (.csv, .json)
│
├── docs/
│   ├── diagrams/                 # High-resolution PNG system diagrams (01-06)
│   └── screenshots/              # Rendered PNG operational UI states (01-05)
│
├── app.py                        # Streamlit web dashboard application
├── cli.py                        # Standalone terminal command-line interface
├── requirements.txt              # Pinned Python package dependencies
├── statement.md                  # University project statement & scope
├── HowToRun.txt                  # Platform execution notes
├── LICENSE                       # MIT License
└── README.md
```

---

## Technologies

| Component | Detail |
|-----------|--------|
| Language | Python 3.11+ |
| Computer Vision | OpenCV (`opencv-python` 5.0.0), MediaPipe (`mediapipe` 1.0.1) |
| Numerical Mathematics | NumPy 2.4.6, SciPy |
| Data Processing | Pandas 3.0.5 |
| Web Dashboard | Streamlit 1.63.0 (Dark Glassmorphic UI) |
| CLI Interface | Standard Library (`argparse`, `sys`, `time`) |
| Testing Framework | Pytest 9.1.1 |
| Version Control | Git & GitHub |

---

## Getting Started

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed
- Standard USB Webcam or integrated laptop camera (or test video clip)
- Git

### Clone & Install

```bash
# Clone the repository
git clone https://github.com/YashGoyal06/cv-24BAI10100.git
cd cv-24BAI10100

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install all dependencies
pip3 install -r requirements.txt
```

---

## Usage (CLI & Web)

VisionGuard is designed to be **100% executable from the terminal command line**, as well as through an interactive web UI.

### 1. Command-Line Interface (CLI Mode)
*Run completely in the terminal without GUI requirements:*

```bash
# Run monitoring with default webcam for 15 seconds
python3 cli.py

# Run for a specific duration (e.g. 30 seconds)
python3 cli.py --duration 30

# Run with a recorded driving video file
python3 cli.py --source /path/to/driving_clip.mp4 --duration 20

# Run in silent mode without sound beeps
python3 cli.py --no-audio
```

**CLI Output Example:**
```
SEC    | FPS   | STATUS      | RISK%  | EAR    | POSE     | BLINKS | ALERTS
----------------------------------------------------------------------
  1.0s |  29.1 | SAFE        |  12.3% |  0.334 | FORWARD  | 1      | -
  3.5s |  28.7 | DROWSY      |  65.4% |  0.138 | FORWARD  | 2      | BEEP
  6.0s |  29.0 | DISTRACTED  |  68.2% |  0.312 | RIGHT    | 2      | BEEP
```

### 2. Interactive Web Dashboard (Streamlit Mode)

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`. Click **▶ Start Monitoring** to begin live video analysis with heads-up display overlays, real-time biometrics, and post-session CSV/JSON downloads.

---

## Computer Vision Algorithms

### Eye Aspect Ratio (EAR)
$$\text{EAR} = \frac{\|p_2 - p_6\|_2 + \|p_3 - p_5\|_2}{2 \cdot \|p_1 - p_4\|_2}$$
* Open eye: $\text{EAR} \approx 0.28 - 0.38$
* Closed eye: $\text{EAR} < 0.22$
* Sustained closure $\ge 15$ continuous frames ($\approx 0.5$s) triggers `DROWSY` state.

### Mouth Aspect Ratio (MAR)
$$\text{MAR} = \frac{\|p_{\text{top}} - p_{\text{bottom}}\|_2 + \|p_{\text{mid\_top}} - p_{\text{mid\_bottom}}\|_2}{2 \cdot \|p_{\text{left}} - p_{\text{right}}\|_2}$$
* Resting mouth: $\text{MAR} < 0.35$
* Yawn threshold: $\text{MAR} \ge 0.60$ for $\ge 15$ continuous frames.

### 3D Head Pose (Perspective-n-Point)
Solves rigid world-to-camera projective geometry using 6 canonical 3D facial coordinates:
$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \mathbf{K} \begin{bmatrix} \mathbf{R} & \mathbf{t} \end{bmatrix} \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}$$
Rotation matrix $\mathbf{R}$ is decomposed into Tait-Bryan Euler angles: Pitch ($\theta_x$), Yaw ($\theta_y$), and Roll ($\theta_z$). Turns exceeding $|\theta_{\text{yaw}}| > 25^\circ$ for $>20$ frames trigger `DISTRACTED`.

---

## System Diagrams

### Use Case Diagram
Interaction flow between the driver and system functions:
![Use Case Diagram](docs/diagrams/01-use-case-diagram.png)

### Class / Component Diagram
Modular object-oriented structure and class relationships:
![Class Diagram](docs/diagrams/02-class-diagram.png)

### Sequence Diagram
Per-frame chronological processing across perception, risk, and alert modules:
![Sequence Diagram](docs/diagrams/03-sequence-diagram.png)

### Architecture Diagram
Five-tier layered pipeline architecture:
![Architecture Diagram](docs/diagrams/04-architecture-diagram.png)

### Telemetry ER Diagram
Data relationship schema between Driver Sessions and Frame Observations:
![ER Diagram](docs/diagrams/05-er-diagram.png)

### Process Flow Diagram
Complete lifecycle from frame ingestion to telemetry export:
![Process Flow Diagram](docs/diagrams/06-process-flow-diagram.png)

---

## Screenshots

### Live Monitoring (SAFE State)
Driver alert and looking forward with nominal EAR:
![SAFE State](docs/screenshots/01_live_monitoring_safe.png)

### Prolonged Eye Closure (DROWSY State)
High-contrast warning and auditory beep triggered:
![DROWSY State](docs/screenshots/02_drowsiness_detected.png)

### Head Turn Distraction (DISTRACTED State)
3D gaze ray projection tracking driver gaze diversion:
![DISTRACTED State](docs/screenshots/03_distraction_detected.png)

### Yawn Detection (CAUTION State)
Mouth aspect ratio exceeding threshold with speech filtering:
![CAUTION State](docs/screenshots/04_yawn_detected_caution.png)

### Compound Fatigue (HIGH RISK State)
Coincident eye closure and head turn with pulsing critical alarm:
![HIGH RISK State](docs/screenshots/05_compound_high_risk.png)

---

## Non-Functional Requirements

- **Performance (NFR-1)**: End-to-end frame processing latency under 35ms ($\approx 28-30$ FPS) on consumer laptop CPUs without GPU acceleration.
- **Usability (NFR-2)**: Single-command startup (`python3 cli.py` or `streamlit run app.py`) with responsive layout, clear status badges, and intuitive sliders.
- **Reliability (NFR-3)**: Complete fault-tolerance for camera disconnections, lighting dropouts, and facial occlusions (`NO FACE` standby).
- **Maintainability (NFR-4)**: Strict PEP-8 compliance, modular architecture, comprehensive docstrings, and zero unexplained magic numbers.
- **Resource Efficiency (NFR-5)**: Lightweight memory footprint under 320 MB and CPU utilization under 15%.
- **Privacy & Portability (NFR-6)**: 100% on-device volatile processing with cross-platform support across macOS, Linux, and Windows.

---

## Testing

VisionGuard is validated through automated unit tests and reproducible scenario protocols:

### Automated Unit Testing (Pytest)
```bash
python3 -m pytest tests/ -v
```
**Test Results: 17 Passed, 0 Failed (100% Pass Rate)**
- Geometric Euclidean distance invariants & division-by-zero protection
- EAR calculation under open/closed eye synthetic geometries
- MAR calculation & temporal speech suppression
- 3D SolvePnP pose estimation and Euler angle extraction
- Multi-cue Risk Engine transitions (`SAFE` $\to$ `DROWSY` $\to$ `DISTRACTED` $\to$ `HIGH RISK`)
- Telemetry aggregation, KPI computation, and CSV/JSON disk export

---

## Author

**Yash Goyal**  
Registration Number: 24BAI10100  
Course: B.Tech (Computer Vision / Applied AI)  
Institution: Vellore Institute of Technology (VIT)  
Academic Session: 2025 – 2026  
VITyarthi - Build Your Own Project Evaluation  
License: [MIT](LICENSE)
