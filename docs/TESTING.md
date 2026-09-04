# VisionGuard – Testing and Validation Protocol

This document details the test matrix, automated test results, edge-case validations, and manual testing procedures for the VisionGuard driver safety system.

---

## 1. Automated Test Suite (Pytest)

The test suite contains automated unit tests covering all core mathematical formulations, state transitions, and file persistence routines.

| Test ID | Test Module | Function Tested | Input Data | Expected Output | Actual Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UT-01** | `test_eye_detector.py` | `euclidean_distance` | 2D Points: $(0,0)$ and $(3,4)$ | Distance $= 5.0$ | $5.0$ | **PASS** |
| **UT-02** | `test_eye_detector.py` | `calculate_ear` | Synthetic open eye landmarks ($v_1=8, v_2=8, h=10$) | $\text{EAR} = 0.80$ | $0.80$ | **PASS** |
| **UT-03** | `test_eye_detector.py` | `calculate_ear` | Synthetic closed eye landmarks ($v_1=1, v_2=1, h=10$) | $\text{EAR} = 0.10$ | $0.10$ | **PASS** |
| **UT-04** | `test_eye_detector.py` | `calculate_ear` | Array with $<6$ indices | Raise `ValueError` | `ValueError` | **PASS** |
| **UT-05** | `test_eye_detector.py` | `EyeDetector.process_eyes` | 2 closed frames followed by open frame | Increment `total_blinks` by 1 | `total_blinks = 1` | **PASS** |
| **UT-06** | `test_eye_detector.py` | `EyeDetector.process_eyes` | 6 consecutive closed frames (thresh: 5) | `is_prolonged_closure = True` | `True` | **PASS** |
| **UT-07** | `test_yawn_detector.py` | `calculate_mar` | Synthetic open mouth landmarks | $\text{MAR} = 0.80$ | $0.80$ | **PASS** |
| **UT-08** | `test_yawn_detector.py` | `YawnDetector.process_mouth` | 2 open frames (simulating speech) | `total_yawns = 0` | $0$ | **PASS** |
| **UT-09** | `test_yawn_detector.py` | `YawnDetector.process_mouth` | 4 consecutive open frames (thresh: 4) | `total_yawns = 1` | $1$ | **PASS** |
| **UT-10** | `test_head_pose.py` | `HeadPoseEstimator` | Empty/None landmarks input | Safe default: `FORWARD`, no crash | `FORWARD` | **PASS** |
| **UT-11** | `test_head_pose.py` | `HeadPoseEstimator.estimate_pose`| Frontal canonical 2D facial points | Computes Pitch, Yaw, Roll, Nose 2D | Valid Euler dict | **PASS** |
| **UT-12** | `test_risk_engine.py` | `RiskEngine.assess_risk` | Nominal inputs (open eyes, forward pose) | State `SAFE`, Risk Score $< 20$ | `SAFE`, Score $< 20$| **PASS** |
| **UT-13** | `test_risk_engine.py` | `RiskEngine.assess_risk` | Prolonged closed eyes | State `DROWSY` | `DROWSY` | **PASS** |
| **UT-14** | `test_risk_engine.py` | `RiskEngine.assess_risk` | Turned head pose | State `DISTRACTED` | `DISTRACTED` | **PASS** |
| **UT-15** | `test_risk_engine.py` | `RiskEngine.assess_risk` | Closed eyes + Turned head compound | State `HIGH RISK` | `HIGH RISK` | **PASS** |
| **UT-16** | `test_risk_engine.py` | `RiskEngine.assess_risk` | `face_detected = False` | State `NO FACE`, no crash | `NO FACE` | **PASS** |
| **UT-17** | `test_analytics.py` | `SessionAnalytics.update` | 10 frames with varied states | Accurately compute percentages | $60\%$ Safe, $20\%$ Drowsy | **PASS** |
| **UT-18** | `test_analytics.py` | `export_csv` & `export_json` | Active session export | Create non-empty valid CSV/JSON | Files verified | **PASS** |

---

## 2. Edge Case & Robustness Validation

| Condition | Potential Failure | System Mitigation Strategy | Verification Result |
| :--- | :--- | :--- | :--- |
| **Camera Unplugged / Perms Denied** | Application crash on `read()` | Checked in `camera.py` with boolean return and user UI error notification. | Handled gracefully |
| **Temporary Facial Occlusion** | Index out-of-range on landmark array | Landmark presence verified before indexing; returns `NO FACE` status. | Handled gracefully |
| **Rapid Natural Talking** | False positive yawn alarm | High threshold ($\text{MAR} \ge 0.60$) combined with 15-frame temporal filter. | Confirmed isolated |
| **Normal Blinking** | False positive drowsiness alarm | Blinks constrained to 1–4 frame window; prolonged alarm requires $\ge 15$ frames. | Zero false alarms |
| **Audio Alert Spam** | Ear-piercing audio loop | 2.0-second cooldown mutex timer enforced in `alert_manager.py`. | Cooldown active |
| **Slow Hardware / Lag** | UI freezing | Image processing decoupled; non-blocking audio threads; lightweight MediaPipe mesh. | Steady 25–30 FPS |

---

## 3. Manual Live Verification Protocol

For course examiners or students demonstrating the system live with a webcam:

1. **Step 1: Normal Gaze:** Sit in front of the webcam looking straight ahead. Verify that the HUD status badge displays a green `SAFE` and risk is $<20\%$.
2. **Step 2: Natural Blinks:** Blink normally. Observe the `Blinks` counter in the bottom HUD incrementing by 1 after each blink.
3. **Step 3: Prolonged Eye Closure:** Close eyes and hold closed for $>1$ second. Observe the HUD badge shift to orange `DROWSY` and hear the alert beep.
4. **Step 4: Driver Distraction:** Turn head to the left or right ($>30^\circ$) looking away from the screen for 1–2 seconds. Observe the HUD badge turn purple `DISTRACTED` and the blue 3D gaze ray point in your head's orientation.
5. **Step 5: Yawn Simulation:** Open mouth widely for $\ge 1$ second. Observe the `Yawns` counter increment and state transition to amber `CAUTION`.
6. **Step 6: Face Disappearance:** Move head out of the camera view. Observe the state gracefully change to gray `NO FACE` without crashing.
7. **Step 7: Session Summary:** Click **Stop Monitoring**. Review the summary KPIs and download the CSV/JSON telemetry records.
