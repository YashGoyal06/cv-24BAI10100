# VisionGuard – Future Enhancements Roadmap

While VisionGuard provides an end-to-end real-time computer vision driver safety pipeline, future industrial iterations can expand its operational capabilities across the following dimensions:

---

## 1. Near-Infrared (NIR) Active Illumination
* **Current State:** Relies on visible spectrum ambient lighting captured by standard RGB webcams.
* **Enhancement:** Integrate active 850nm or 940nm Near-Infrared (NIR) LED illuminators and monochrome NIR cameras. This eliminates dependence on ambient light, enabling full functionality in complete darkness or nighttime driving without blinding the driver.

---

## 2. Deep Eye Gaze Tracking (Pupil Center Corneal Reflection)
* **Current State:** Distraction is estimated primarily via gross 3D head orientation (Pitch, Yaw, Roll).
* **Enhancement:** Incorporate fine-grained iris landmark regression and gaze vectors to detect "cognitive distraction" or "eyes-off-road" when the head remains pointed forward but the driver's eyes wander toward a mobile device mounted on the center console.

---

## 3. Physiological Signal Fusion (Heart Rate via Remote Photoplethysmography - rPPG)
* **Current State:** Evaluates physical biomechanical manifestations (eyelid droop, mouth aperture, head rotation).
* **Enhancement:** Implement non-contact camera-based rPPG that measures subtle cyclical skin color variations in the driver's forehead caused by blood pulsation. Extracting Heart Rate Variability (HRV) would provide an autonomic indicator of impending drowsiness minutes before physical eyelid droop manifests.

---

## 4. Embedded Automotive Edge Deployment (NVIDIA Jetson / Raspberry Pi 5)
* **Current State:** Python-based Streamlit application running on desktop/laptop environments.
* **Enhancement:** Port the inference pipeline to C++ utilizing TensorRT or ONNX Runtime on embedded platforms such as NVIDIA Jetson Orin Nano or Raspberry Pi 5. Containerize with Docker and interface with the vehicle Controller Area Network (CAN-bus) to actuate tactile steering wheel haptic vibrations.

---

## 5. Personalized Biometric Calibration
* **Current State:** Uses fixed empirical default thresholds with manual slider calibration.
* **Enhancement:** Implement an initial 10-second adaptive baseline calibration phase during engine ignition. The system learns the specific resting EAR, blink frequency, and neutral head tilt of the individual driver, accommodating distinct ethnic eye shapes or physical traits.
