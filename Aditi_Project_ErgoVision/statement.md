# Academic Problem Statement & Scope Specification

**Project Title:** ErgoVision – AI-Based Ergonomic Posture and Screen Fatigue Monitoring System  
**Student Name:** Aditi Prakash  
**Course:** Computer Vision (VITyarthi Project)  
**Submission Category:** Build Your Own Project (Flipped Course Evaluation)  

---

## 1. Problem Statement
Sedentary office, research, and academic computer usage has grown drastically, leading to high incidences of:
1. **Musculoskeletal Disorders (MSDs)**: Neck strain ("tech-neck"), spinal slouching, and lateral head leaning from prolonged unergonomic screen alignment.
2. **Computer Vision Syndrome (CVS)**: Significant decrease in spontaneous blink rates (from the normal ~15–20 blinks/min down to <6 blinks/min), resulting in evaporative dry eye disease, visual asthenopia, and blurred vision.
3. **Harmful Screen Proximity**: Unconscious forward leaning bringing eyes excessively close (<45 cm) to display monitors.

Existing remedies rely on manual timer prompts or cumbersome wearable posture harnesses, which disrupt workplace concentration and suffer from high abandonment rates.

---

## 2. Project Scope & Objectives
The objective of **ErgoVision** is to engineer a continuous, non-intrusive, zero-wearable Computer Vision system powered by standard webcam video streams to:
- Continuously compute forward neck tilt angles and lateral tilt angles using facial landmark triangulation.
- Estimate physical distance to the display screen in centimeters via pinhole perspective geometry and inter-pupillary distance.
- Monitor ocular apertures via the Soukupová and Čech Eye Aspect Ratio (EAR) metric and compute real-time rolling blink frequency.
- Provide non-distracting visual Heads-Up Display (HUD) cues and export timestamped CSV and JSON telemetry for ergonomic health auditing.

---

## 3. Target Users
1. **Software Engineers and Knowledge Workers**: Professionals spending 8+ hours daily in front of desktop monitors.
2. **Students and Academic Researchers**: Individuals engaged in intensive reading, programming, and screen work.
3. **Corporate Ergonomics and Occupational Health Officers**: Teams evaluating workplace seating and screen setups.

---

## 4. High-Level Functional Requirements
1. **Real-Time Video Capture Module**: Support native webcam streams (device index 0) with automatic zero-configuration fallback to bundled video benchmarks.
2. **Dense Facial Mesh Extraction**: Extract 468 3D facial landmarks per frame at $\ge 25$ frames per second (FPS).
3. **Ergonomic Posture Classification**: Classify posture into `GOOD`, `SLOUCHING (FORWARD TILT)`, and `SLOUCHING (HEAD TILTED)` with temporal hysteresis.
4. **Perspective Distance Estimation**: Detect when user distance breaches safety margins (<45 cm or >85 cm).
5. **Ocular Fatigue Tracking**: Detect spontaneous blinks and trigger dry-eye risk warnings when blink rate drops below 10 blinks/minute.
6. **Telemetry & Audit Export**: Automatically persist per-second CSV telemetry and high-level JSON summaries upon session conclusion.

---

## 5. Non-Functional Requirements
1. **Performance**: Real-time throughput maintained at 25–30 FPS on standard consumer CPUs without requiring discrete GPU acceleration.
2. **Usability**: Single-command execution (`python3 main.py`) with zero GUI installation hurdles or framework complexities.
3. **Reliability & Error Handling**: Graceful fallback to bundled benchmark video if camera permissions are restricted, ensuring non-crashing execution.
4. **Privacy**: Pure local edge processing. All image frames remain strictly in memory and are discarded immediately after landmark vectorization; no image data is transmitted or recorded to disk.

---

## 6. Technical Stack
- **Programming Language**: Python 3.11
- **Computer Vision & Image Processing**: OpenCV (`opencv-python` 4.8+)
- **Facial Landmark Geometry**: MediaPipe FaceMesh (468 3D Landmarks)
- **Numerical Computation**: NumPy
- **Unit Testing Framework**: Pytest
- **Documentation & Diagrams**: Markdown, Matplotlib Architecture Schematics
