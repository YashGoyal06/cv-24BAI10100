# VisionGuard – System Diagrams Specification

This document presents the complete architectural, process, UML, and data flow diagrams for the VisionGuard Driver Drowsiness and Distraction Detection System.

---

## 1. System Architecture Diagram

```mermaid
graph TD
    subgraph Video Acquisition Layer
        CAM[Hardware Webcam / Video File] -->|OpenCV BGR Frame| VS[VideoStream Manager]
    end

    subgraph Perception Layer
        VS -->|BGR Frame 640x480| FD[FaceLandmarkDetector MediaPipe]
        FD -->|468 3D Landmarks| NORM[Pixel Normalizer]
    end

    subgraph Feature Extraction Layer
        NORM -->|Eye Landmarks| ED[EyeDetector - EAR Formulation]
        NORM -->|Mouth Landmarks| YD[YawnDetector - MAR Formulation]
        NORM -->|PnP 6 Keypoints| HP[HeadPoseEstimator - SolvePnP]
    end

    subgraph Assessment & Control Layer
        ED -->|EAR, Closure Frames, Blinks| RE[Multi-Cue RiskEngine]
        YD -->|MAR, Yawn Duration| RE
        HP -->|Euler Angles, Distraction Status| RE
        RE -->|Safety State, Risk Score| AM[AlertManager]
        RE -->|Telemetry Stream| SA[SessionAnalytics]
    end

    subgraph Presentation & UI Layer
        AM -->|Audio Cues| SOUND[Debounced Audio Alarm]
        AM -->|Visual Badges| HUD[High-Contrast HUD Renderer]
        SA -->|Timeseries Data| EXPORT[CSV & JSON Exporter]
        HUD -->|Annotated Frame| ST[Streamlit Dashboard]
        SA -->|KPI Metrics| ST
    end
```

---

## 2. Process Flow / Workflow Diagram

```mermaid
flowchart TD
    START([Start System]) --> INIT[Initialize MediaPipe, OpenCV & Config]
    INIT --> CAPTURE[Capture Next Video Frame]
    CAPTURE --> CHECK_FRAME{Frame Valid?}
    CHECK_FRAME -- No --> RECONNECT[Attempt Camera Reconnect / Terminate]
    CHECK_FRAME -- Yes --> DETECT_FACE[Run MediaPipe Face Mesh]
    
    DETECT_FACE --> FACE_FOUND{Face Detected?}
    FACE_FOUND -- No --> SET_NO_FACE[Set State = NO FACE] --> RENDER_HUD
    
    FACE_FOUND -- Yes --> EXTRACT[Extract 468 Dense Landmarks]
    
    EXTRACT --> CALC_EAR[Compute Eye Aspect Ratio EAR]
    EXTRACT --> CALC_MAR[Compute Mouth Aspect Ratio MAR]
    EXTRACT --> SOLVE_PNP[Solve 3D Perspective-n-Point]
    
    CALC_EAR --> EVAL_EYES{EAR < 0.22?}
    EVAL_EYES -- Yes --> INC_EYE_CNT[Increment Closed Frame Counter]
    EVAL_EYES -- No --> CHECK_BLINK{1 <= Frames <= 4?}
    CHECK_BLINK -- Yes --> INC_BLINK[Blink Count + 1]
    CHECK_BLINK -- No --> RESET_EYE_CNT[Reset Counter]
    
    INC_EYE_CNT --> CHECK_PROLONGED{Closed Frames >= 15?}
    CHECK_PROLONGED -- Yes --> FLAG_DROWSY[Set Flag: Prolonged Eye Closure]
    CHECK_PROLONGED -- No --> CALC_RISK
    
    CALC_MAR --> EVAL_MOUTH{MAR >= 0.60?}
    EVAL_MOUTH -- Yes --> INC_YAWN_CNT[Increment Mouth Open Counter]
    EVAL_MOUTH -- No --> RESET_YAWN[Reset Mouth Counter]
    INC_YAWN_CNT --> CHECK_YAWN{Open Frames >= 15?}
    CHECK_YAWN -- Yes --> FLAG_YAWN[Set Flag: Confirmed Yawn]
    CHECK_YAWN -- No --> CALC_RISK
    
    SOLVE_PNP --> CALC_EULER[Decompose Rotation Matrix to Pitch/Yaw/Roll]
    CALC_EULER --> CHECK_POSE{|Yaw| > 25° or |Pitch| > 20°?}
    CHECK_POSE -- Yes --> INC_POSE_CNT[Increment Distraction Counter]
    CHECK_POSE -- No --> RESET_POSE[Reset Distraction Counter]
    INC_POSE_CNT --> CHECK_DISTRACT{Distract Frames >= 20?}
    CHECK_DISTRACT -- Yes --> FLAG_DISTRACT[Set Flag: Driver Distracted]
    CHECK_DISTRACT -- No --> CALC_RISK
    
    FLAG_DROWSY --> CALC_RISK[Calculate Instantaneous & Smoothed Risk Score]
    FLAG_YAWN --> CALC_RISK
    FLAG_DISTRACT --> CALC_RISK
    RESET_EYE_CNT --> CALC_RISK
    RESET_YAWN --> CALC_RISK
    RESET_POSE --> CALC_RISK
    
    CALC_RISK --> CLASSIFY_STATE{Evaluate State Hierarchy}
    CLASSIFY_STATE -->|Drowsy + Distracted| ST_HIGH[HIGH RISK]
    CLASSIFY_STATE -->|Prolonged Eye Closure| ST_DROWSY[DROWSY]
    CLASSIFY_STATE -->|Head Turned Away| ST_DISTRACT[DISTRACTED]
    CLASSIFY_STATE -->|Yawning / Moderate Risk| ST_CAUTION[CAUTION]
    CLASSIFY_STATE -->|Nominal Biometrics| ST_SAFE[SAFE]
    
    ST_HIGH --> DISPATCH_ALERT[Dispatch Visual & Auditory Cues]
    ST_DROWSY --> DISPATCH_ALERT
    ST_DISTRACT --> DISPATCH_ALERT
    ST_CAUTION --> DISPATCH_ALERT
    ST_SAFE --> DISPATCH_ALERT
    
    DISPATCH_ALERT --> UPDATE_STATS[Update Session Telemetry & Timeseries]
    UPDATE_STATS --> RENDER_HUD[Draw High-Contrast HUD on Frame]
    RENDER_HUD --> DISPLAY[Render in Streamlit Dashboard]
    DISPLAY --> CHECK_STOP{User Clicked Stop?}
    CHECK_STOP -- No --> CAPTURE
    CHECK_STOP -- Yes --> EXPORT_REPORT[Export CSV/JSON Session Analytics]
    EXPORT_REPORT --> END([End Monitoring])
```

---

## 3. UML Use Case Diagram

```mermaid
graph LR
    DRIVER((Driver / Student))
    SYS((VisionGuard System))

    subgraph VisionGuard Driver Monitoring System
        UC1[Start Monitoring Session]
        UC2[Calibrate Biometric Thresholds EAR / MAR / Pose]
        UC3[View Real-Time Video HUD]
        UC4[Receive Auditory Fatigue Alerts]
        UC5[Stop Monitoring Session]
        UC6[View Post-Drive Analytics Dashboard]
        UC7[Export Session Telemetry to CSV / JSON]
    end

    DRIVER --> UC1
    DRIVER --> UC2
    DRIVER --> UC3
    DRIVER --> UC4
    DRIVER --> UC5
    DRIVER --> UC6
    DRIVER --> UC7

    UC1 -.-> SYS
    UC3 -.-> SYS
    UC4 -.-> SYS
    UC7 -.-> SYS
```

---

## 4. UML Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Driver / Evaluator
    participant UI as Streamlit Dashboard (app.py)
    participant Cam as VideoStream
    participant Face as FaceLandmarkDetector
    participant Eye as EyeDetector
    participant Yawn as YawnDetector
    participant Pose as HeadPoseEstimator
    participant Risk as RiskEngine
    participant Alert as AlertManager
    participant Analytics as SessionAnalytics

    User->>UI: Click "Start Monitoring"
    UI->>Cam: start()
    UI->>Analytics: start_session()
    
    loop Every Video Frame (~30 FPS)
        Cam->>Cam: read_frame()
        Cam-->>UI: BGR Image Frame
        
        UI->>Face: process_frame(frame)
        Face-->>UI: landmarks_pixel (468, 3), face_detected
        
        par Feature Extraction
            UI->>Eye: process_eyes(landmarks_pixel)
            Eye-->>UI: ear, is_closed, is_prolonged, blinks
        and
            UI->>Yawn: process_mouth(landmarks_pixel)
            Yawn-->>UI: mar, is_yawning, yawns
        and
            UI->>Pose: estimate_pose(landmarks_pixel, shape)
            Pose-->>UI: pitch, yaw, roll, direction, is_distracted
        end
        
        UI->>Risk: assess_risk(eye_data, yawn_data, pose_data)
        Risk-->>UI: state, instant_score, risk_score
        
        UI->>Alert: update_alert(state, risk_score)
        opt State in (DROWSY, DISTRACTED, HIGH RISK)
            Alert->>Alert: _play_audio_beep() [Threaded]
        end
        
        UI->>Analytics: update(state, risk_score, ear, mar, ...)
        UI->>UI: draw_hud(frame, state, metrics)
        UI-->>User: Display Live Video + Telemetry Panel
    end
    
    User->>UI: Click "Stop Monitoring"
    UI->>Cam: stop()
    UI->>Analytics: end_session()
    Analytics-->>UI: session_summary (KPIs)
    UI-->>User: Display Summary Cards & Export Buttons
    User->>UI: Click "Export Session Telemetry (CSV)"
    UI->>Analytics: export_csv()
    Analytics-->>User: Download visionguard_session_telemetry.csv
```

---

## 5. UML Class / Component Diagram

```mermaid
classDiagram
    class AppConfig {
        +EyeConfig eye
        +YawnConfig yawn
        +HeadPoseConfig head_pose
        +RiskEngineConfig risk
        +AlertConfig alert
        +int camera_index
        +int frame_width
        +int frame_height
    }

    class VideoStream {
        -int source
        -VideoCapture cap
        -float fps
        +start() bool
        +read_frame() Tuple~bool, ndarray~
        +get_fps() float
        +stop() void
    }

    class FaceLandmarkDetector {
        -FaceMesh face_mesh
        +process_frame(bgr_frame) Tuple
        +draw_landmarks_on_frame() ndarray
        +close() void
    }

    class EyeDetector {
        -EyeConfig config
        -int closed_frame_count
        -int total_blinks
        -int prolonged_closure_events
        +reset() void
        +process_eyes(landmarks) dict
    }

    class YawnDetector {
        -YawnConfig config
        -int open_frame_count
        -int total_yawns
        -int cooldown_counter
        +reset() void
        +process_mouth(landmarks) dict
    }

    class HeadPoseEstimator {
        -HeadPoseConfig config
        -ndarray model_points_3d
        -int distraction_frame_count
        +reset() void
        +estimate_pose(landmarks, shape) dict
    }

    class RiskEngine {
        -RiskEngineConfig config
        -float smoothed_risk_score
        -str current_state
        +reset() void
        +assess_risk(eye_data, yawn_data, pose_data) dict
    }

    class AlertManager {
        -AlertConfig config
        -float last_audio_time
        +update_alert(state, risk_score) dict
        -_play_audio_beep() void
    }

    class SessionAnalytics {
        -float session_start_time
        -dict state_counts
        -list timestamps
        -list risk_scores
        +start_session() void
        +update(state, score, ear, mar, ...) void
        +end_session() void
        +get_summary() dict
        +export_csv(path) str
        +export_json(path) str
    }

    VideoStream ..> FaceLandmarkDetector : Provides Frames
    FaceLandmarkDetector ..> EyeDetector : Feeds Landmarks
    FaceLandmarkDetector ..> YawnDetector : Feeds Landmarks
    FaceLandmarkDetector ..> HeadPoseEstimator : Feeds Landmarks
    EyeDetector ..> RiskEngine : Provides Eye Features
    YawnDetector ..> RiskEngine : Provides Yawn Features
    HeadPoseEstimator ..> RiskEngine : Provides Pose Features
    RiskEngine ..> AlertManager : Triggers Alerts
    RiskEngine ..> SessionAnalytics : Logs Telemetry
    AppConfig --* EyeDetector
    AppConfig --* YawnDetector
    AppConfig --* HeadPoseEstimator
    AppConfig --* RiskEngine
    AppConfig --* AlertManager
```
