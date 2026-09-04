# VisionGuard – System Architecture Specification

## 1. Architectural Principles
VisionGuard is designed with the following core software engineering tenets:
* **Separation of Concerns:** Low-level OpenCV acquisition is strictly separated from Computer Vision feature geometry, risk aggregation, UI rendering, and disk persistence.
* **Stateless Geometry & Stateful Temporal Analysis:** Functions calculating Euclidean distances and aspect ratios are pure, deterministic functions, while temporal persistence (blink counters, moving averages) are encapsulated in stateful class objects.
* **Fault-Tolerant & Non-Blocking:** Audio alarms and I/O run on background threads; camera frame drops or temporary landmark losses are handled gracefully without application halts.

---

## 2. Layered Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  - Streamlit Dashboard (app.py)                             │
│  - HUD Drawing Routine (utils.py)                           │
│  - Interactive Parameter Configuration Sidebar              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    DECISION & ALERT LAYER                   │
│  - Risk Engine (risk_engine.py)                             │
│  - Alert Manager & Threaded Audio Alarm (alert_manager.py)  │
│  - Session Analytics Collector & Exporter (analytics.py)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  FEATURE EXTRACTION LAYER                   │
│  - Eye & Blink Detector (eye_detector.py)                   │
│  - Yawn Detector (yawn_detector.py)                         │
│  - 3D Head Pose Solver (head_pose.py)                       │
│  - Mathematical Distance Helpers (utils.py)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    PERCEPTION LAYER                         │
│  - MediaPipe FaceMesh Wrapper (face_detector.py)            │
│  - Coordinate Normalization & Landmark Indexing             │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                 VIDEO ACQUISITION LAYER                     │
│  - OpenCV VideoCapture & Thread Buffer (camera.py)          │
│  - Camera Reconnection & Resolution Management              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Module Responsibilities

| Module | File | Key Class / Method | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Config** | `src/config.py` | `AppConfig` | Holds all dataclass configuration for EAR, MAR, PnP, and Risk weights. Eliminates magic numbers. |
| **Acquisition** | `src/camera.py` | `VideoStream` | Interfaces with OpenCV `VideoCapture`, configures 640x480 resolution, tracks instantaneous FPS. |
| **Perception** | `src/face_detector.py` | `FaceLandmarkDetector` | Wraps MediaPipe FaceMesh, maps normalized coordinates to pixel space, draws debug mesh. |
| **Ocular Analysis** | `src/eye_detector.py` | `EyeDetector` | Calculates EAR, maintains closed-frame counter, records intentional blinks and prolonged closures. |
| **Oral Analysis** | `src/yawn_detector.py` | `YawnDetector` | Calculates MAR, filters speech micro-openings, tracks sustained yawns with cooldown. |
| **Spatial Pose** | `src/head_pose.py` | `HeadPoseEstimator` | Implements `cv2.solvePnP`, projects 3D gaze rays, calculates Pitch, Yaw, Roll, flags distraction. |
| **Assessment** | `src/risk_engine.py` | `RiskEngine` | Linear cue weighting, exponential moving average smoothing, categorical state determination. |
| **Notifications** | `src/alert_manager.py` | `AlertManager` | Dispatches priority levels, non-blocking platform audio beeps, enforces alert cooldowns. |
| **Telemetry** | `src/analytics.py` | `SessionAnalytics` | Computes aggregate KPIs, safe time percentage, exports to CSV and JSON formats. |
| **UI Dashboard** | `app.py` | `main()` | Streamlit dashboard connecting all modules into an interactive user-facing tool. |
