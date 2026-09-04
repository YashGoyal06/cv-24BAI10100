# VisionGuard – Computer Vision Models & Landmark Topology

## 1. Landmark Extraction Architecture
VisionGuard leverages Google's **MediaPipe FaceMesh** solution for dense, high-frequency 3D facial landmark regression.

```
Input Frame (BGR 640x480)
       │
       ▼
Pre-processing (Color Conversion BGR -> RGB)
       │
       ▼
BlazeFace Detector (Locates face bounding box ROI)
       │
       ▼
Face Landmark Model (Deep 3D Mesh Regression Network)
       │
       ▼
468 / 478 Dense 3D Landmarks (Normalized x, y, z coordinates)
       │
       ▼
Pixel Space Transformation: x * width, y * height, z * width
```

---

## 2. Anatomical Landmark Mapping Indices

### Eye Landmarks (6-Point EAR Formulation per Eye)
The Eye Aspect Ratio (EAR) requires 6 key boundary points on each eye perimeter:
* **Left Eye (`left_eye_indices`):**
  * `33`: Lateral outer canthus (outer corner)
  * `160`: Upper eyelid lateral point
  * `158`: Upper eyelid medial point
  * `133`: Medial inner canthus (inner corner)
  * `153`: Lower eyelid medial point
  * `144`: Lower eyelid lateral point

* **Right Eye (`right_eye_indices`):**
  * `362`: Lateral outer canthus (outer corner)
  * `385`: Upper eyelid lateral point
  * `387`: Upper eyelid medial point
  * `263`: Medial inner canthus (inner corner)
  * `373`: Lower eyelid medial point
  * `380`: Lower eyelid lateral point

### Mouth Landmarks (MAR Formulation)
* `61`: Left oral commissure (corner of mouth)
* `291`: Right oral commissure (corner of mouth)
* `0`: Upper vermilion border (top of upper lip)
* `17`: Lower vermilion border (bottom of lower lip)
* `13`: Inner upper lip median
* `14`: Inner lower lip median

### Canonical 3D Head Pose Points (SolvePnP)
To solve the Perspective-n-Point pose estimation, 6 anthropometric 3D landmarks are mapped to a standard head coordinate frame:
1. **Nose Tip:** MediaPipe Landmark `1` $\to (0.0, 0.0, 0.0)$ mm
2. **Chin Center:** MediaPipe Landmark `152` $\to (0.0, -330.0, -65.0)$ mm
3. **Left Eye Corner:** MediaPipe Landmark `33` $\to (-225.0, 170.0, -135.0)$ mm
4. **Right Eye Corner:** MediaPipe Landmark `263` $\to (225.0, 170.0, -135.0)$ mm
5. **Left Mouth Corner:** MediaPipe Landmark `61` $\to (-150.0, -150.0, -125.0)$ mm
6. **Right Mouth Corner:** MediaPipe Landmark `291` $\to (150.0, -150.0, -125.0)$ mm

---

## 3. Computational Rationale
* **Inference Speed:** Runs at $\approx 30$ FPS on standard consumer CPUs without requiring discrete NVIDIA GPU hardware.
* **Resilience:** BlazeFace ROI tracking avoids running full-image face detection on every frame, reducing CPU utilization below 15%.
* **Coordinate Invariance:** Computing aspect ratios (EAR, MAR) normalizes for camera-to-driver distance and scale changes.
