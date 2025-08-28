# app_logic.py
import sys
import os
import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from ui_main_window import UiMainWindow

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AppLogic(QWidget, UiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.focus_counter = 0
        self.is_focused = False

        # --- Dlib & Head Pose Setup ---
        try:
            predictor_path = resource_path("assets/shape_predictor_68_face_landmarks.dat")
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(predictor_path)
            (self.lStart, self.lEnd) = (42, 48)
            (self.rStart, self.rEnd) = (36, 42)
        except Exception as e:
            print(f"CRITICAL ERROR loading models: {e}")
            self.predictor = None

        # --- 3D Face Model for Head Pose ---
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])

        # --- (The rest of __init__ is the same) ---
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        sound_path = resource_path("assets/demo_sound.mp3")
        source = QUrl.fromLocalFile(sound_path)
        self.player.setSource(source)
        
        toggle_off_path = resource_path("assets/toggle_off.png").replace('\\', '/')
        toggle_on_path = resource_path("assets/toggle_on.png").replace('\\', '/')
        self.aura_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{ width: 90px; height: 60px; }}
            QCheckBox::indicator:unchecked {{ image: url({toggle_off_path}); }}
            QCheckBox::indicator:checked {{ image: url({toggle_on_path}); }}
            QCheckBox {{ color: white; spacing: 15px; }}
        """)
        
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.aura_toggle.toggled.connect(self.manual_aura_toggle)
        self.demo_button.clicked.connect(self.play_demo_sound)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)

    # ... (helper functions eye_aspect_ratio, manual_aura_toggle, set_system_volume, play_demo_sound, and slider label updates are the same)
    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        if C == 0: return 0.3
        ear = (A + B) / (2.0 * C)
        return ear

    def manual_aura_toggle(self, checked): pass

    def set_system_volume(self, level):
        try:
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process and session.Process.name().lower() not in ["python.exe", "py.exe", "projectaura.exe"]:
                    volume.SetMasterVolume(level, None)
        except Exception as e:
            print(f"Error setting volume: {e}")
            
    def play_demo_sound(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.setPosition(0)
        else:
            self.player.play()
    
    def update_threshold_label(self, value): self.threshold_label.setText(f"Focus Threshold ({value / 100.0:.2f}):")
    def update_sensitivity_label(self, value): self.sensitivity_label.setText(f"Detection Stability ({value} frames):")

    def set_aura_status(self, is_active):
        if is_active != self.is_focused:
            self.is_focused = is_active
            if is_active:
                self.status_label.setText('STATUS: ACTIVE')
                self.status_label.setStyleSheet("color: #2ecc71;")
                if not self.aura_toggle.isChecked(): self.aura_toggle.setChecked(True)
                self.set_system_volume(0.2)
            else:
                self.status_label.setText('STATUS: INACTIVE')
                self.status_label.setStyleSheet("color: #FF4757;")
                if self.aura_toggle.isChecked(): self.aura_toggle.setChecked(False)
                self.set_system_volume(1.0)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            size = gray.shape
            
            if self.predictor: 
                faces = self.detector(gray, 0)
                
                if len(faces) > 0:
                    face = faces[0]
                    shape = self.predictor(gray, face)
                    shape = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
                    
                    leftEye = shape[self.lStart:self.lEnd]
                    rightEye = shape[self.rStart:self.rEnd]
                    
                    leftEAR = self.eye_aspect_ratio(leftEye)
                    rightEAR = self.eye_aspect_ratio(rightEye)
                    ear = (leftEAR + rightEAR) / 2.0
                    
                    # --- NEW HEAD POSE LOGIC ---
                    image_points = np.array([
                        (shape[30][0], shape[30][1]),     # Nose tip
                        (shape[8][0], shape[8][1]),       # Chin
                        (shape[45][0], shape[45][1]),     # Left eye left corner
                        (shape[36][0], shape[36][1]),     # Right eye right corner
                        (shape[54][0], shape[54][1]),     # Left Mouth corner
                        (shape[48][0], shape[48][1])      # Right mouth corner
                    ], dtype="double")
                    
                    focal_length = size[1]
                    center = (size[1]/2, size[0]/2)
                    camera_matrix = np.array(
                        [[focal_length, 0, center[0]],
                        [0, focal_length, center[1]],
                        [0, 0, 1]], dtype = "double"
                    )
                    
                    dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
                    (success, rotation_vector, translation_vector) = cv2.solvePnP(self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
                    
                    # Project a 3D point (0, 0, 1000.0) onto the image plane.
                    (nose_end_point2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
                    
                    # Get head pose angles
                    rmat, _ = cv2.Rodrigues(rotation_vector)
                    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
                    yaw = angles[1]

                    # Display angles on the UI
                    self.info_label.setText(f"Head Angle (Yaw): {yaw:.2f}°")

                    # --- UPDATED FOCUS CONDITION ---
                    ear_threshold = self.threshold_slider.value() / 100.0
                    ear_consec_frames = self.sensitivity_slider.value()

                    # Only consider focused if eyes are open AND head is mostly straight
                    if ear > ear_threshold and abs(yaw) < 25:
                        self.focus_counter += 1
                        if self.focus_counter >= ear_consec_frames:
                            self.set_aura_status(True)
                    else:
                        self.focus_counter = 0
                        self.set_aura_status(False)
                    
                    # Draw a line showing head direction
                    p1 = ( int(image_points[0][0]), int(image_points[0][1]))
                    p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
                    cv2.line(frame, p1, p2, (255,0,0), 2)

                else:
                    self.focus_counter = 0
                    self.set_aura_status(False)
                    self.info_label.setText("No face detected.")

            display_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = display_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(display_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            p = convert_to_qt_format.scaled(240, 180, Qt.AspectRatioMode.KeepAspectRatio)
            self.webcam_feed.setPixmap(QPixmap.fromImage(p))

    def closeEvent(self, event):
        self.set_system_volume(1.0)
        self.capture.release()
        event.accept()