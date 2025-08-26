# app_logic.py
import sys
import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from ui_main_window import UiMainWindow

class AppLogic(QWidget, UiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.focus_counter = 0
        self.is_focused = False

        # --- HYBRID DETECTOR SETUP ---
        try:
            self.face_cascade = cv2.CascadeClassifier('./assets/haarcascade_frontalface_default.xml')
            self.predictor = dlib.shape_predictor('./assets/shape_predictor_68_face_landmarks.dat')
            (self.lStart, self.lEnd) = (42, 48)
            (self.rStart, self.rEnd) = (36, 42)
        except Exception as e:
            print(f"CRITICAL ERROR loading models: {e}")
            self.face_cascade = None
            self.predictor = None

        # --- (The rest of __init__ is the same) ---
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        source = QUrl.fromLocalFile('./assets/demo_sound.mp3')
        self.player.setSource(source)

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.aura_toggle.toggled.connect(self.manual_aura_toggle)
        self.demo_button.clicked.connect(self.play_demo_sound)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        if C == 0: return 0.3
        ear = (A + B) / (2.0 * C)
        return ear

    def manual_aura_toggle(self, checked):
        pass

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

    def set_system_volume(self, level):
        try:
            from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process and session.Process.name().lower() not in ["python.exe", "py.exe"]:
                    volume.SetMasterVolume(level, None)
        except Exception as e:
            print(f"Error setting volume: {e}")

    def play_demo_sound(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.setPosition(0)
        else:
            self.player.play()
    
    def update_threshold_label(self, value):
        self.threshold_label.setText(f"Focus Threshold ({value / 100.0:.2f}):")
        
    def update_sensitivity_label(self, value):
        self.sensitivity_label.setText(f"Detection Stability ({value} frames):")

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.face_cascade and self.predictor: 
                ear_threshold = self.threshold_slider.value() / 100.0
                ear_consec_frames = self.sensitivity_slider.value()

                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
                
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]
                    dlib_rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
                    
                    shape = self.predictor(gray, dlib_rect)
                    shape = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
                    
                    leftEye = shape[self.lStart:self.lEnd]
                    rightEye = shape[self.rStart:self.rEnd]
                    
                    leftEAR = self.eye_aspect_ratio(leftEye)
                    rightEAR = self.eye_aspect_ratio(rightEye)
                    ear = (leftEAR + rightEAR) / 2.0
                    
                    if ear > ear_threshold:
                        self.focus_counter += 1
                        if self.focus_counter >= ear_consec_frames:
                            self.set_aura_status(True)
                    else:
                        self.focus_counter = 0
                        self.set_aura_status(False)
                    
                    for (sx, sy) in shape:
                        cv2.circle(frame, (sx, sy), 2, (0, 255, 0), -1)
                else:
                    self.focus_counter = 0
                    self.set_aura_status(False)

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