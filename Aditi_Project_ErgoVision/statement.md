# Academic Problem Statement & Scope

**Project Title:** ErgoVision – AI-Based Ergonomic Posture and Screen Fatigue Monitoring System  
**Student Name:** Aditi Prakash  
**Course:** Computer Vision (VITyarthi Project)  

---

## 1. Problem Statement
Sedentary office and academic screen time has increased dramatically, causing high prevalence of cervical spine strain (forward head posture/slouching) and digital eye strain (asthenopia). Current commercial solutions rely either on wearable posture harnesses or periodic manual timer reminders, which are inconvenient and frequently ignored.

## 2. Objective
To design and deploy a lightweight, zero-wearable Computer Vision system capable of:
1. Monitoring forward head tilt and lateral lean from facial landmark vectors in real-time.
2. Estimating distance to the monitor using perspective camera geometry and inter-pupillary ratios.
3. Tracking blink frequency to detect ocular fatigue and prevent dry-eye syndrome.
4. Providing real-time visual feedback and exporting actionable ergonomics telemetry.

## 3. Technology & Frameworks
- **Core Language:** Python 3.11
- **Computer Vision:** OpenCV (`opencv-python`), MediaPipe FaceMesh
- **Numerical Mathematics:** NumPy
- **Testing:** Pytest
- **Execution Target:** Terminal and OpenCV HighGUI (Zero-Config, Single-Command)
