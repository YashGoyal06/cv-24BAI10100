# VisionGuard – Computer Vision Algorithms & Mathematical Formulations

This document provides rigorous mathematical and algorithmic explanations for all Computer Vision methods implemented in VisionGuard.

---

## 1. Facial Landmark Extraction (MediaPipe FaceMesh)
MediaPipe FaceMesh performs 3D surface geometry regression over human faces using a two-stage cascade:
1. **Detector Model (BlazeFace):** Lightweight sub-millisecond anchor-based convolutional network that detects the face bounding box.
2. **Regression Model (Mesh):** 3D landmark regressor that predicts 468 3D vertices $(x_i, y_i, z_i)$ normalized within $[0.0, 1.0]$.

### Coordinate Transformation
Normalized coordinates are converted to Euclidean pixel coordinates $(u_i, v_i)$ for an image with resolution $(W, H)$:
$$u_i = x_i \cdot W, \quad v_i = y_i \cdot H, \quad w_i = z_i \cdot W$$

---

## 2. Eye Aspect Ratio (EAR) Formulation
Introduced by Tereza Soukupová and Jan Čech (Computer Vision Winter Workshop, 2016), the Eye Aspect Ratio measures the degree of eyelid aperture in an illumination-invariant and scale-invariant manner.

For a 6-point eyelid configuration $[p_1, p_2, p_3, p_4, p_5, p_6]$ where $p_1, p_4$ are horizontal outer and inner canthi, and $(p_2, p_6), (p_3, p_5)$ are vertical eyelid landmark pairs:

$$\text{EAR} = \frac{\|p_2 - p_6\|_2 + \|p_3 - p_5\|_2}{2 \cdot \|p_1 - p_4\|_2}$$

Where $\|\cdot\|_2$ represents Euclidean $L_2$ distance:
$$\|a - b\|_2 = \sqrt{(a_x - b_x)^2 + (a_y - b_y)^2}$$

### Mathematical Properties
* When eyes are wide open, $\text{EAR} \approx 0.28 - 0.38$.
* When eyes close, the numerator shrinks towards zero while the denominator stays constant, yielding $\text{EAR} < 0.20$.
* By averaging both eyes:
  $$\text{EAR}_{\text{avg}} = \frac{\text{EAR}_{\text{left}} + \text{EAR}_{\text{right}}}{2}$$

---

## 3. Blink and Drowsiness Detection Logic
A single low EAR frame does **not** signify fatigue. VisionGuard separates intentional blinks from micro-sleep events via temporal frame windows:

* **Normal Blink:** 
  $$\text{EAR} < \text{Threshold}_{\text{EAR}} \quad \text{for } N \text{ frames}, \quad 1 \le N \le 4$$
* **Prolonged Eye Closure (Micro-sleep):**
  $$\text{EAR} < \text{Threshold}_{\text{EAR}} \quad \text{for } N \text{ frames}, \quad N \ge N_{\text{closed\_thresh}} \quad (\approx 15 \text{ frames at } 30\text{ FPS})$$

---

## 4. Mouth Aspect Ratio (MAR) Formulation
Yawning is characterized by involuntary prolonged vertical opening of the oral cavity. The Mouth Aspect Ratio computes vertical oral aperture relative to horizontal mouth width:

$$\text{MAR} = \frac{\|p_{\text{top}} - p_{\text{bottom}}\|_2 + \|p_{\text{mid\_top}} - p_{\text{mid\_bottom}}\|_2}{2 \cdot \|p_{\text{left}} - p_{\text{right}}\|_2}$$

* Normal resting/speaking mouth: $\text{MAR} \in [0.15, 0.35]$.
* Yawn state: $\text{MAR} \ge 0.60$.

### Temporal Smoothing & Cooldown
To eliminate false positives caused by talking or laughing:
1. The mouth must maintain $\text{MAR} \ge 0.60$ for at least $N_{\text{yawn\_consec}} = 15$ continuous frames ($\approx 0.5$ seconds).
2. A refractory cooldown period ($60$ frames $\approx 2$ seconds) prevents a single yawning yawn from incrementing the counter multiple times.

---

## 5. 3D Head Pose Estimation (Perspective-n-Point)
To detect driver distraction (looking at phones, looking out side windows, or head drooping), VisionGuard solves the classical **Perspective-n-Point (PnP)** problem.

Given:
* 6 3D canonical anthropometric world points $\mathbf{P}_w \in \mathbb{R}^3$ (Nose, Chin, Left/Right Eye corners, Mouth corners)
* 6 corresponding 2D image coordinates $\mathbf{p}_i \in \mathbb{R}^2$ regressed from MediaPipe
* Camera intrinsic calibration matrix $\mathbf{K}$:

$$\mathbf{K} = \begin{bmatrix} f & 0 & c_x \\ 0 & f & c_y \\ 0 & 0 & 1 \end{bmatrix}$$
Where $f \approx W$ (focal length approximation), $c_x = W/2$, $c_y = H/2$.

The relationship between 3D world coordinates and 2D image coordinates is governed by the pinhole projection:

$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \mathbf{K} \begin{bmatrix} \mathbf{R} & \mathbf{t} \end{bmatrix} \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix}$$

VisionGuard solves for rotation matrix $\mathbf{R} \in SO(3)$ and translation vector $\mathbf{t} \in \mathbb{R}^3$ using OpenCV's Levenberg-Marquardt iterative solver (`cv2.solvePnP`).

### Euler Angles Decomposition
Using QR/RQ decomposition on $\mathbf{R}$, we extract Tait-Bryan angles:
* **Pitch ($\theta_x$):** Tilting head Up / Down.
* **Yaw ($\theta_y$):** Turning head Left / Right.
* **Roll ($\theta_z$):** Tilting head sideways.

**Distraction Condition:**
$$|\theta_y| > 25^\circ \quad \text{or} \quad |\theta_x| > 20^\circ \quad \text{for } \ge 20 \text{ consecutive frames}$$

---

## 6. Multi-Cue Risk Engine
The risk engine synthesizes discrete and continuous variables into a scalar Risk Score $\mathcal{R}_t \in [0, 100]$:

$$\mathcal{H}_t = \Big( w_{\text{eye}} \cdot f_{\text{eye}} + w_{\text{yawn}} \cdot f_{\text{yawn}} + w_{\text{dist}} \cdot f_{\text{dist}} + w_{\text{blink}} \cdot f_{\text{blink}} \Big) \times 100$$

With default weights:
$$w_{\text{eye}} = 0.40, \quad w_{\text{yawn}} = 0.25, \quad w_{\text{dist}} = 0.25, \quad w_{\text{blink}} = 0.10$$

### Exponential Moving Average (EMA)
To smooth instantaneous frame noise:
$$\mathcal{R}_t = \alpha \mathcal{H}_t + (1 - \alpha) \mathcal{R}_{t-1}, \quad \text{with } \alpha = 0.25$$

### State Decision Hierarchy
1. If no face detected $\to$ `NO FACE`
2. If `ProlongedEyeClosure` AND `Distracted` $\to$ `HIGH RISK`
3. If `ProlongedEyeClosure` $\to$ `DROWSY`
4. If `Distracted` $\to$ `DISTRACTED`
5. If `Yawning` or $\mathcal{R}_t \ge 30$ $\to$ `CAUTION`
6. Otherwise $\to$ `SAFE`
