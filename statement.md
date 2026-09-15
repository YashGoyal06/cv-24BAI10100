# Project Statement

## Problem Statement
Automotive transport constitutes the backbone of modern logistics and mobility, yet driver fatigue, micro-sleep episodes, and visual distractions remain primary catalysts in vehicular collisions globally. According to the World Health Organization (WHO), over 1.35 million traffic fatalities occur annually, with driver impairment contributing to more than 20% of severe highway crashes. Traditional vehicular warning systems—such as lane departure warning systems (LDWS) or steering jerk sensors—are fundamentally reactive: they detect an anomaly only after the vehicle trajectory has already begun to deviate dangerously into oncoming traffic.

There is a critical requirement for a non-intrusive, proactive Driver Monitoring System (DMS) that continuously observes human facial biometrics, identifies cognitive and physical drowsiness early, detects diverted gaze in real time, and issues immediate graded alerts before hazardous control loss occurs.

## Scope of the Project
VisionGuard provides an end-to-end, edge-computing Computer Vision pipeline capable of ingesting live video streams, localizing dense 3D facial landmarks, evaluating scale-invariant ocular and oral geometry, estimating 3D head orientation via Perspective-n-Point (SolvePnP), and synthesizing multi-cue risk assessments.

**In Scope:**
* Real-time video frame acquisition from consumer webcams and pre-recorded driving video files ($640 \times 480$, 30 FPS)
* MediaPipe FaceMesh perception extracting 468 dense 3D facial vertices
* Mathematical formulation of Eye Aspect Ratio (EAR) for blink counting and prolonged eye-closure detection
* Mouth Aspect Ratio (MAR) computation with temporal persistence to distinguish involuntary yawning from natural speech
* Classical 3D Perspective-n-Point (SolvePnP) rigid head pose estimation calculating Euler angles (Pitch, Yaw, Roll)
* Multi-factor linear hazard scoring with Exponential Moving Average (EMA) temporal smoothing
* Tiered safety state escalation (`SAFE`, `CAUTION`, `DROWSY`, `DISTRACTED`, `HIGH RISK`)
* Interactive web-based dashboard (Streamlit) and headless command-line interface (CLI)
* Rate-limited, non-blocking auditory alert cues with anti-spam cooldown timers
* Real-time telemetry logging and export to CSV and JSON formats

**Out of Scope:**
* Medical diagnosis of clinical sleep disorders (such as narcolepsy or sleep apnea)
* Certified automotive ASIL-D embedded controller integration (ISO 26262)
* Autonomous vehicle steering actuation or electro-mechanical braking intervention
* Full functionality in total darkness without an active Near-Infrared (NIR) camera

## Target Users
* **Commercial Fleet Operators & Logistics Managers**: Fleet tracking of driver fatigue trends, shift safety auditing, and route risk profiling
* **Everyday Drivers & Long-Distance Commuters**: Real-time cabin companion providing non-intrusive alertness reminders during night driving
* **Automotive Telematics & DMS Engineers**: Prototyping computer vision algorithms for next-generation in-cabin safety systems
* **Academic Evaluators & Researchers**: Demonstrating rigorous applications of geometric Computer Vision, landmark regression, and temporal modeling

## High-Level Features

### 1. Face & Facial Landmark Perception Module
* High-frequency 468-point 3D landmark mesh extraction using MediaPipe FaceMesh
* Fast conversion of normalized coordinates into image pixel space
* Graceful degradation: handles temporary facial occlusions, head turns, or camera dropouts without crashing (`NO FACE` state)

### 2. Ocular & Drowsiness Tracking Module
* Real-time 6-point Eye Aspect Ratio (EAR) calculation per eye
* Intentional blink tracking ($1 - 4$ frames) and blink rate (blinks/minute) monitoring
* Sustained eye closure detection ($\ge 15$ frames / $\approx 0.5$s) indicating micro-sleep

### 3. Yawn & Fatigue Detection Module
* Mouth Aspect Ratio (MAR) measuring oral aperture relative to horizontal mouth width
* Multi-frame persistence buffer ($\ge 15$ continuous frames) to eliminate false alarms from speech or laughter
* Refractory cooldown timer preventing duplicate yawn event counts

### 4. 3D Head Pose & Distraction Module
* SolvePnP using 6 canonical anthropometric 3D facial coordinates
* Decomposition of rotation vectors into Tait-Bryan Euler angles (Pitch, Yaw, Roll)
* 3D gaze ray projection visualizing driver focal attention direction
* Sustained gaze diversion warning ($|\theta_{\text{yaw}}| > 25^\circ$ for $>20$ frames)

### 5. Multi-Cue Risk Engine
* Linear hazard scoring combining eye closure, yawning, distraction, and blink irregularity into a $[0, 100]$ score
* Exponential Moving Average (EMA) temporal filter smoothing sensor noise
* Deterministic hierarchical safety state classifier

### 6. Dual Presentation & Alert System
* Modern Streamlit web dashboard with heads-up display (HUD) overlay and parameter calibration sliders
* Standalone terminal CLI script (`cli.py`) for automated, non-GUI execution
* Debounced non-blocking auditory bell alarms with 2.0-second cooldown protection
* Full session telemetry logging with one-click export to CSV and JSON formats
