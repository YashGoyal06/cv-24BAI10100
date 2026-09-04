# VisionGuard – AI-Based Driver Drowsiness and Distraction Detection System

## 1. Problem Statement
Driver fatigue, drowsiness, and inattention represent leading contributors to global vehicular collisions and highway fatalities. Conventional vehicle telemetry (such as steering jerk or lane departure) often detects fatigue only after unsafe vehicle trajectories have occurred. Real-time visual monitoring of driver facial biometrics provides an early, non-invasive indicator of cognitive degradation and gaze diversion. This project builds a real-time, explainable Computer Vision pipeline that monitors facial geometry to proactively detect drowsiness, prolonged eye closures, yawning, and head rotation away from the road.

## 2. Scope of the Project
- **In Scope:**
  - Real-time video frame acquisition from standard consumer webcams (30 FPS, 640×480).
  - Dense facial landmark tracking using lightweight mesh models (MediaPipe 468 landmarks).
  - Mathematical computation of Eye Aspect Ratio (EAR) for blink and micro-sleep identification.
  - Mouth Aspect Ratio (MAR) formulation for involuntary yawn detection.
  - Perspective-n-Point (SolvePnP) rigid 3D pose estimation for yaw/pitch distraction tracking.
  - Multi-cue temporal risk engine synthesizing biometrics into actionable safety states (`SAFE`, `CAUTION`, `DROWSY`, `DISTRACTED`, `HIGH RISK`).
  - Interactive Streamlit dashboard with heads-up display (HUD), audible alarms, and post-session telemetry export (CSV/JSON).
  - Validation protocol across controlled real-world driving simulation scenarios.

- **Out of Scope:**
  - Medical diagnosis of clinical sleep disorders (narcolepsy, sleep apnea).
  - Certified automotive ASIL-D embedded controller deployment.
  - Autonomous vehicle steering actuation or braking intervention.

## 3. Target Users
1. **Commercial Fleet Operators:** Logistics managers seeking driver shift safety metrics and fatigue event tracking.
2. **Commuters & Long-Distance Drivers:** Everyday drivers seeking non-intrusive alertness monitoring during night highway travel.
3. **Automotive Telematics Developers:** Engineers prototyping intelligent Driver Monitoring Systems (DMS) for next-generation vehicle dashboards.
4. **Academic Researchers & Students:** University researchers studying real-time feature extraction, geometric Computer Vision, and human-computer safety interfaces.

## 4. High-Level Features
- **High-Precision Facial Landmark Localization:** 468-point 3D landmark mesh mapped to pixel space in real time.
- **Explainable Biometric Thresholding:** Fully transparent mathematical formulation of EAR and MAR without black-box unexplainable scores.
- **Temporal False-Positive Suppression:** Multi-frame persistence buffers that distinguish normal speech from yawning and quick blinks from prolonged micro-sleep.
- **Head Orientation Vector Projection:** 3D gaze ray projection visualizing driver focal attention direction.
- **Debounced Auditory Cues:** Threaded non-blocking acoustic warnings with cooldown protection to eliminate driver annoyance.
- **Session Telemetry & Analytics:** Granular timeseries export of EAR, MAR, and safety states for retrospective fleet safety auditing.

## 5. Expected Outcomes
- Sub-50ms per-frame end-to-end processing latency on standard consumer laptops.
- Over 90% detection accuracy on controlled prolonged eye closure and distraction test scenarios.
- Zero frame crashes during temporary facial occlusions or variable ambient lighting.
- A fully reproducible, submission-ready project demonstrating core Computer Vision methodologies.

## 6. Project Boundaries & Operational Constraints
- Operates under adequate ambient illumination (or near-infrared camera sources for night operation).
- Designed for single-driver frontal view within ±45° camera orientation angle.
- Compliant with ethical privacy guidelines: all image processing occurs locally in volatile memory; raw video is never transmitted to external cloud servers.
