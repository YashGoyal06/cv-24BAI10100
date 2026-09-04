# VisionGuard – Data and Validation Guide

## 1. Dataset Strategy & Real-World Validation
VisionGuard is designed as an edge-computing, real-time Computer Vision system that processes live video streams. Unlike deep-learning classifiers trained on pre-labeled static image datasets, VisionGuard relies on **geometric landmark regression** and **temporal biomechanical modeling** (Eye Aspect Ratio, Mouth Aspect Ratio, 3D Perspective-n-Point pose estimation).

Consequently, the system does not require large static training datasets for weights training. Instead, evaluation and validation utilize:
1. **Benchmark Academic Datasets** (for offline cross-validation).
2. **Controlled Real-Time Simulation Scenarios** (for interactive and pipeline validation).

---

## 2. Public Benchmark Datasets (For Comparative Validation)

If conducting formal offline cross-validation experiments, the following public academic datasets are recommended:

### A. NTHU-DDD (National Tsing Hua University Driver Drowsiness Detection Dataset)
* **Source:** National Tsing Hua University Computer Vision Lab
* **Purpose:** Academic benchmark for driver fatigue evaluation under various driving conditions.
* **Characteristics:**
  * Multi-subject video sequences (day, night, with/without glasses).
  * Labeled ground-truth for: Normal Driving, Slow Blinking, Yawning, Nodding, Head Dropping.
* **Usage in VisionGuard:** Validating EAR threshold sensitivity and temporal blink filter under varying illumination and eyewear.

### B. YawDD (Yawning Detection Dataset)
* **Source:** University of Ottawa (Distributed for Academic Research)
* **Purpose:** Dedicated benchmark for mouth state and yawn classification.
* **Characteristics:**
  * Two video subsets: Dash-camera angle and In-car rear-view mirror angle.
  * Male and female drivers with diverse facial hair and ethnicity.
* **Usage in VisionGuard:** Calibrating MAR threshold (0.60) to eliminate false positives during normal conversation and laughing.

### C. Biwi Kinect Head Pose Database
* **Source:** ETH Zurich Computer Vision Laboratory
* **Purpose:** Benchmark for 3D head orientation estimation.
* **Characteristics:** Over 15,000 frames with synchronized RGB and ground-truth 3D head rotation angles (Pitch, Yaw, Roll).
* **Usage in VisionGuard:** Calibrating SolvePnP camera matrix parameters and verifying Euler angle accuracy.

---

## 3. Controlled Real-Time Scenario Protocol

To evaluate the system under reproducible conditions without downloading multi-gigabyte restricted archives, the following controlled protocol is defined:

| Scenario ID | Test Condition | Protocol | Success Criteria |
| :--- | :--- | :--- | :--- |
| **SC-01** | Attentive Driving | Subject looks straight at camera with normal blinking for 30s. | State remains `SAFE`; 0 false alerts. |
| **SC-02** | Natural Blinking | Subject blinks naturally at 12–20 blinks/min. | Blinks tracked with $\ge 90\%$ accuracy. |
| **SC-03** | Prolonged Eye Closure | Subject closes eyes for $>1.5$ seconds (~45 frames). | Transition to `DROWSY` within 0.5s; alert fired. |
| **SC-04** | Yawning | Subject simulates 3 distinct yawning episodes (>1s each). | Exactly 3 yawns recorded; `CAUTION` triggered. |
| **SC-05** | Distraction (Left/Right) | Subject turns head $>30^\circ$ left/right for $>2$ seconds. | Transition to `DISTRACTED`; direction accurately identified. |
| **SC-06** | Compound Fatigue | Subject turns head while closing eyes. | Transition to `HIGH RISK` state. |
| **SC-07** | Facial Occlusion / Loss | Subject temporarily covers face or moves out of frame. | State transitions to `NO FACE`; zero application crashes. |

---

## 4. Session Telemetry Directory (`sample_sessions/`)
When running VisionGuard, exported CSV and JSON telemetry files are saved into this directory (`data/sample_sessions/`). These records store timestamped records of:
* Frame timestamp (seconds elapsed)
* Instantaneous EAR and MAR
* Estimated 3D Euler angles (Pitch, Yaw, Roll)
* Assigned Safety State and Composite Risk Index
