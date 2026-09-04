# VisionGuard – Visual Gallery & Demonstration Guide

This directory contains visual documentation and interface walkthrough captures illustrating VisionGuard across different operational states.

---

## 1. Key Interface Screens

### A. Home Dashboard (Standby Mode)
* **Description:** Initial landing state upon launching `streamlit run app.py`. Displays KPI metrics in standby, video source selector, and configurable biometric parameter sidebar.
* **Key Components:** Parameter sliders (EAR threshold, MAR threshold, Yaw angle), Start Monitoring button, and glassmorphic telemetry cards.

### B. Live Monitoring (SAFE State)
* **Description:** Real-time video processing running at ~30 FPS.
* **Visual Cues:**
  * Top status badge displays green `SAFE`.
  * Risk Score gauge reads $<20\%$.
  * Subtle yellow landmark keypoints annotate eye perimeter, lips, and nose.
  * Real-time telemetry bar at the bottom displays live EAR ($\approx 0.32$), MAR ($\approx 0.22$), and blink counter.

### C. Drowsiness Detected (DROWSY State)
* **Description:** Triggered when the driver's eyes remain closed for $\ge 15$ continuous frames ($\approx 0.5$s).
* **Visual Cues:**
  * Top status badge turns deep orange `DROWSY`.
  * Outer frame border flashes high-contrast orange.
  * Risk Score gauge jumps to $60\% - 75\%$.
  * Debounced auditory alert beep sounds through platform speakers.

### D. Driver Distraction (DISTRACTED State)
* **Description:** Triggered when head yaw angle exceeds $\pm 25^\circ$ for $>20$ continuous frames.
* **Visual Cues:**
  * Top status badge turns purple `DISTRACTED`.
  * Directional 3D Gaze Ray extends from the driver's nose tip, pointing toward the lateral window or phone zone.
  * Head Pose HUD reads `Pose: LEFT` or `Pose: RIGHT`.

### E. Critical Multi-Cue Hazard (HIGH RISK State)
* **Description:** Compound hazard state when driver displays both prolonged eye closure and diverted head orientation, or when composite risk score exceeds $80\%$.
* **Visual Cues:**
  * Top badge flashes crimson red `HIGH RISK` with active CSS pulse animation.
  * Rapid high-frequency auditory alarm sounds.
  * Outer border highlighted with 4px red stroke.

### F. Post-Drive Analytics & Export
* **Description:** Rendered immediately after clicking **⏹ Stop Monitoring**.
* **Visual Cues:**
  * Session duration, safe time percentage, total blinks, and confirmed yawns displayed in structured metric cards.
  * Direct download buttons for `visionguard_session_telemetry.csv` and `visionguard_session_summary.json`.

---

## 2. Capturing Live Screenshots During Evaluation
To capture high-resolution screenshots for your submission:
1. Start monitoring via webcam: `streamlit run app.py`
2. Perform the actions described above (open eyes, closed eyes, yawn, look away).
3. Use macOS shortcut `Cmd + Shift + 4` to capture the region and save PNG files directly into this `screenshots/` directory.
