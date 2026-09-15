# ErgoVision – AI-Based Ergonomic Posture & Screen Fatigue Monitoring System

**Student Name:** Aditi Prakash  
**Project Track:** Computer Vision (VITyarthi Project)  
**Execution Type:** Pure Computer Vision (OpenCV + MediaPipe), Zero-Config Single-Command CLI/GUI  

---

## 1. Project Overview

Prolonged desktop computer usage causes two primary workplace hazards:
1. **Musculoskeletal Disorders (MSDs)**: Neck strain ("tech-neck"), forward head tilt, and spine slouching.
2. **Computer Vision Syndrome (CVS)**: Reduced blink rates leading to ocular fatigue, dry eye disease, and near-screen eye strain.

**ErgoVision** is an intelligent, real-time Computer Vision system that operates continuously via standard webcam to monitor workplace ergonomics without intrusive wearables or manual sensor attachments.

---

## 2. Computer Vision Syllabus Alignment

| Syllabus Unit | Concept Implemented | ErgoVision Implementation |
| :--- | :--- | :--- |
| **Unit 1: Transformations & Geometry** | Euclidean metrics & Affine scaling | `src/fatigue_tracker.py` calculates Euclidean distance between ocular feature points invariant to scale. |
| **Unit 2: Perspective & Pin-hole Geometry** | Camera projection & Distance estimation | `src/distance_estimator.py` uses perspective pinhole camera model and inter-pupillary pixel spans to estimate physical user-to-screen distance in centimeters. |
| **Unit 3: Feature Extraction** | Facial landmark topological extraction | `src/face_detector.py` leverages dense 468-point facial mesh. |
| **Unit 4: Spatio-Temporal Analysis** | Rolling temporal analysis & thresholds | `src/posture_detector.py` uses temporal persistence thresholds to differentiate momentary shifts from habitual bad posture. |

---

## 3. How to Run

### Interactive Visual Mode (Recommended)
```bash
python3 main.py
```
- Controls: Press `q` or `ESC` on the display window to stop and inspect the summary report.

### Headless Terminal Mode
```bash
python3 main.py --cli --duration 15
```

### Automated Unit Testing
```bash
python3 -m pytest tests/ -v
```

---

## 4. Directory Structure
```
Aditi_Project_ErgoVision/
├── data/
│   ├── sample_video.mp4          # 20s benchmark test video
│   └── sample_sessions/          # Exported CSV and JSON logs
├── docs/
├── src/
│   ├── __init__.py
│   ├── analytics.py              # Session metric telemetry and exports
│   ├── camera.py                 # VideoCapture handler with auto-fallback
│   ├── config.py                 # Centralized ergonomic angle & distance thresholds
│   ├── distance_estimator.py     # Pinhole perspective distance calculator
│   ├── face_detector.py          # 468-point facial landmark detector
│   ├── fatigue_tracker.py        # Soukupová & Čech EAR & blink rate monitor
│   ├── posture_detector.py       # Neck tilt & lateral head lean analyzer
│   └── utils.py                  # Real-time HUD renderer
├── tests/
│   └── test_ergovision.py        # Automated test suite
├── cli.py                        # Standalone terminal runner
├── main.py                       # Master single-command runner
├── HowToRun.txt                  # Step-by-step execution guide
├── requirements.txt              # Pinned dependencies
└── README.md
```
