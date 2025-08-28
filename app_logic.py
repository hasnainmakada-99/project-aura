# app_logic.py
import sys
import os
import cv2
import dlib
import numpy as np
import time
import psutil
from scipy.spatial import distance as dist
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from ui_main_window import UiMainWindow
from game_audio_analyzer import GameAudioAnalyzer

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

        # --- AI State Variables ---
        self.focus_counter = 0
        self.is_focused = False
        self.current_volume_level = 1.0
        
        # --- Screen Activity Monitoring ---
        self.last_mouse_pos = None
        self.last_activity_time = time.time()
        self.keyboard_activity_count = 0
        self.mouse_activity_count = 0
        self.activity_window = 10.0  # seconds
        self.activity_threshold = 5  # minimum activities per window
        
        # --- Gaming Audio Intelligence ---
        self.game_audio_analyzer = GameAudioAnalyzer()
        self.gaming_mode_active = False
        self.current_game = "valorant"
        self.game_audio_enhancements = {}
        
        # --- Head Pose Tracking Variables ---
        self.pose_history = []
        self.pose_history_size = 5
        self.last_valid_pose = None
        self.pose_confidence = 0.0

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

        # --- Enhanced 3D Face Model for Head Pose ---
        # Using more accurate 3D coordinates based on anthropometric measurements
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip (33)
            (0.0, -330.0, -65.0),        # Chin (8)
            (-225.0, 170.0, -135.0),     # Left eye left corner (45)
            (225.0, 170.0, -135.0),      # Right eye right corner (36)
            (-150.0, -150.0, -125.0),    # Left mouth corner (54)
            (150.0, -150.0, -125.0),     # Right mouth corner (48)
            (0.0, 100.0, -30.0),         # Nose bridge (27)
            (-75.0, 180.0, -100.0),      # Left eye center (42)
            (75.0, 180.0, -100.0),       # Right eye center (39)
        ], dtype=np.float64)

        # --- Audio Player & UI Setup ---
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
        
        # --- Webcam Setup ---
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # --- Connect UI Signals ---
        self.aura_toggle.toggled.connect(self.manual_aura_toggle)
        self.demo_button.clicked.connect(self.play_demo_sound)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.sensitivity_slider.valueChanged.connect(self.update_sensitivity_label)
        self.gaming_mode_checkbox.toggled.connect(self.toggle_gaming_mode)
        self.game_selector.currentTextChanged.connect(self.change_game_profile)

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        if C == 0: return 0.3
        ear = (A + B) / (2.0 * C)
        return ear

    def calculate_head_pose(self, shape, image_size):
        """Enhanced head pose calculation with confidence scoring"""
        try:
            # Enhanced 2D facial landmarks corresponding to 3D model points
            image_points = np.array([
                (shape[30][0], shape[30][1]),  # Nose tip (33 -> 30 in 68-point model)
                (shape[8][0], shape[8][1]),    # Chin
                (shape[45][0], shape[45][1]),  # Left eye left corner
                (shape[36][0], shape[36][1]),  # Right eye right corner
                (shape[54][0], shape[54][1]),  # Left mouth corner
                (shape[48][0], shape[48][1]),  # Right mouth corner
                (shape[27][0], shape[27][1]),  # Nose bridge
                (shape[42][0], shape[42][1]),  # Left eye center
                (shape[39][0], shape[39][1]),  # Right eye center
            ], dtype=np.float64)
            
            # Enhanced camera matrix with better focal length estimation
            focal_length = image_size[1] * 1.1  # Slightly adjusted for better accuracy
            center = (image_size[1] / 2, image_size[0] / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # Distortion coefficients (assuming minimal lens distortion)
            dist_coeffs = np.zeros((4, 1), dtype=np.float64)
            
            # Solve PnP with iterative refinement for better accuracy
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points, 
                image_points, 
                camera_matrix, 
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return None, 0.0
                
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Extract Euler angles (yaw, pitch, roll)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)
            yaw = angles[1]
            pitch = angles[0]
            roll = angles[2]
            
            # Calculate confidence based on landmark stability and pose validity
            confidence = self.calculate_pose_confidence(shape, yaw, pitch, roll)
            
            pose_data = {
                'yaw': yaw,
                'pitch': pitch,
                'roll': roll,
                'rotation_vector': rotation_vector,
                'translation_vector': translation_vector,
                'confidence': confidence
            }
            
            return pose_data, confidence
            
        except Exception as e:
            print(f"Error in head pose calculation: {e}")
            return None, 0.0

    def calculate_pose_confidence(self, shape, yaw, pitch, roll):
        """Calculate confidence score for head pose estimation"""
        confidence = 1.0
        
        # Reduce confidence for extreme angles
        if abs(yaw) > 45:
            confidence *= 0.7
        if abs(pitch) > 30:
            confidence *= 0.8
        if abs(roll) > 25:
            confidence *= 0.8
            
        # Check facial landmark symmetry for confidence
        left_eye_center = np.mean(shape[36:42], axis=0)
        right_eye_center = np.mean(shape[42:48], axis=0)
        eye_distance = np.linalg.norm(left_eye_center - right_eye_center)
        
        # Expected eye distance ratio (should be relatively stable)
        if eye_distance < 20 or eye_distance > 100:
            confidence *= 0.6
            
        return min(confidence, 1.0)

    def smooth_pose_estimation(self, current_pose):
        """Apply temporal smoothing to head pose estimates"""
        if current_pose is None:
            return self.last_valid_pose
            
        # Add current pose to history
        self.pose_history.append(current_pose)
        if len(self.pose_history) > self.pose_history_size:
            self.pose_history.pop(0)
            
        # Calculate weighted average with more weight on recent poses
        if len(self.pose_history) >= 2:
            weights = np.linspace(0.5, 1.0, len(self.pose_history))
            weights /= np.sum(weights)
            
            smoothed_yaw = np.average([p['yaw'] for p in self.pose_history], weights=weights)
            smoothed_pitch = np.average([p['pitch'] for p in self.pose_history], weights=weights)
            smoothed_roll = np.average([p['roll'] for p in self.pose_history], weights=weights)
            
            smoothed_pose = {
                'yaw': smoothed_yaw,
                'pitch': smoothed_pitch,
                'roll': smoothed_roll,
                'confidence': current_pose['confidence']
            }
            
            self.last_valid_pose = smoothed_pose
            return smoothed_pose
        else:
            self.last_valid_pose = current_pose
            return current_pose

    def get_screen_activity_score(self):
        """Analyze screen activity to determine if user is actively working"""
        try:
            current_time = time.time()
            
            # Get current mouse position
            try:
                import win32gui
                mouse_x, mouse_y = win32gui.GetCursorPos()
                current_mouse_pos = (mouse_x, mouse_y)
                
                # Check for mouse movement
                if self.last_mouse_pos is not None:
                    mouse_distance = ((current_mouse_pos[0] - self.last_mouse_pos[0])**2 + 
                                    (current_mouse_pos[1] - self.last_mouse_pos[1])**2)**0.5
                    if mouse_distance > 10:  # Significant mouse movement
                        self.mouse_activity_count += 1
                        self.last_activity_time = current_time
                
                self.last_mouse_pos = current_mouse_pos
                
            except ImportError:
                # Fallback: use psutil for basic activity detection
                pass
            
            # Check CPU usage as proxy for activity
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 20:  # Moderate CPU usage indicates activity
                self.keyboard_activity_count += 1
                self.last_activity_time = current_time
            
            # Calculate activity score based on recent activity
            time_since_activity = current_time - self.last_activity_time
            
            if time_since_activity < 2.0:  # Very recent activity
                activity_score = 1.0
            elif time_since_activity < 5.0:  # Recent activity
                activity_score = 0.8
            elif time_since_activity < 10.0:  # Some activity
                activity_score = 0.6
            elif time_since_activity < 30.0:  # Little activity
                activity_score = 0.3
            else:  # No recent activity
                activity_score = 0.1
            
            # Reset counters periodically
            if current_time - self.last_activity_time > self.activity_window:
                self.keyboard_activity_count = 0
                self.mouse_activity_count = 0
            
            return activity_score
            
        except Exception as e:
            print(f"Error in screen activity detection: {e}")
            return 0.5  # Default moderate score

    def get_hybrid_focus_score(self, face_detected, pose_valid, confidence, ear_valid, activity_score):
        """Combine facial detection with screen activity for more accurate focus detection"""
        
        # Weight factors for different detection methods
        face_weight = 0.6  # Facial detection still primary
        activity_weight = 0.4  # Screen activity as strong secondary
        
        # Calculate face-based score
        face_score = 0.0
        if face_detected:
            face_score += 0.3  # Base score for face detection
            if pose_valid:
                face_score += 0.4  # Add for valid pose
            if confidence > 0.3:
                face_score += 0.2  # Add for good confidence
            if ear_valid:
                face_score += 0.1  # Add for open eyes
        
        # Combine scores
        hybrid_score = (face_score * face_weight) + (activity_score * activity_weight)
        
        # Boost score if both methods agree on high focus
        if face_score > 0.7 and activity_score > 0.7:
            hybrid_score = min(1.0, hybrid_score * 1.2)
        
        # Special case: High activity but no face detection (multi-monitor scenario)
        if not face_detected and activity_score > 0.8:
            hybrid_score = max(hybrid_score, 0.6)  # Give benefit of doubt for active users
        
        return hybrid_score

    def start_gaming_mode(self, game_name="valorant"):
        """Start gaming mode with audio intelligence"""
        try:
            self.current_game = game_name
            self.game_audio_analyzer.set_game_profile(game_name)
            
            if self.game_audio_analyzer.start_analysis():
                self.gaming_mode_active = True
                self.game_audio_analyzer.enable_enhancement()
                print(f"Started gaming mode for {game_name}")
                return True
            else:
                print("Failed to start audio analysis")
                return False
                
        except Exception as e:
            print(f"Error starting gaming mode: {e}")
            return False
    
    def stop_gaming_mode(self):
        """Stop gaming mode and return to normal operation"""
        try:
            self.gaming_mode_active = False
            self.game_audio_analyzer.stop_analysis()
            print("Stopped gaming mode")
            
        except Exception as e:
            print(f"Error stopping gaming mode: {e}")
    
    def apply_gaming_audio_enhancements(self):
        """Apply intelligent audio enhancements based on game audio analysis"""
        if not self.gaming_mode_active:
            return
            
        try:
            # Get current audio analysis
            analysis = self.game_audio_analyzer.get_current_audio_analysis()
            
            # Check for high-priority sounds (footsteps, gunshots)
            footstep_confidence = analysis.get("footstep_confidence", 0.0)
            detected_sounds = analysis.get("detected_sounds", {})
            
            # Gaming-specific audio enhancement logic
            if footstep_confidence > 0.3:  # Footsteps detected
                # Enhance footstep clarity by reducing other sounds
                self.apply_enhanced_gaming_volume(0.1, "footsteps_detected")
                
            elif any(sound.get("detected") and sound.get("priority") == "high" 
                    for sound in detected_sounds.values()):
                # Other high-priority sounds detected
                self.apply_enhanced_gaming_volume(0.3, "combat_sounds")
                
            elif self.is_focused:
                # Normal gaming focus - moderate reduction
                self.apply_enhanced_gaming_volume(0.4, "gaming_focus")
                
            else:
                # Not focused - normal volume
                self.apply_enhanced_gaming_volume(1.0, "normal")
                
            # Update gaming info in UI
            self.update_gaming_info(analysis, footstep_confidence)
            
        except Exception as e:
            print(f"Error applying gaming enhancements: {e}")
    
    def apply_enhanced_gaming_volume(self, level, reason):
        """Apply volume changes with gaming-specific logic"""
        try:
            # Get apps that should be controlled during gaming
            mute_list_text = self.mute_list_input.text().lower().strip()
            apps_to_control = [app.strip() for app in mute_list_text.split(',') if app.strip()]
            
            # Gaming-specific app handling
            gaming_apps = ["spotify.exe", "discord.exe", "chrome.exe", "firefox.exe", "vlc.exe"]
            game_apps = ["valorant.exe", "cs2.exe", "apex_legends.exe"]
            
            if not apps_to_control:
                apps_to_control = gaming_apps  # Default gaming apps to control
            
            # Import pycaw components
            try:
                from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            except ImportError:
                return
                
            sessions = AudioUtilities.GetAllSessions()
            controlled_apps = []
            
            for session in sessions:
                if session.Process and session.Process.name():
                    process_name = session.Process.name().lower()
                    
                    # Check if this is a game we should NOT control
                    is_game = any(game in process_name for game in game_apps)
                    
                    if not is_game:  # Don't control the game itself
                        # Check if this app should be controlled
                        for app_to_control in apps_to_control:
                            if app_to_control in process_name:
                                try:
                                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                                    clamped_level = max(0.0, min(1.0, level))
                                    volume.SetMasterVolume(clamped_level, None)
                                    controlled_apps.append(process_name)
                                    
                                except Exception as app_error:
                                    print(f"Error setting volume for {process_name}: {app_error}")
            
            # Update gaming volume info
            if controlled_apps:
                self.update_gaming_volume_info(f"Gaming: {reason} | Controlling: {', '.join(set(controlled_apps))}")
                
        except Exception as e:
            print(f"Error in gaming volume control: {e}")
    
    def update_gaming_info(self, analysis, footstep_confidence):
        """Update UI with gaming-specific information"""
        try:
            detected_sounds = analysis.get("detected_sounds", {})
            game_name = analysis.get("game", "unknown")
            
            # Count detected high-priority sounds
            high_priority_sounds = [name for name, data in detected_sounds.items() 
                                  if data.get("detected") and data.get("priority") == "high"]
            
            # Create gaming status message
            gaming_status = f"Game: {game_name.title()} | "
            
            if footstep_confidence > 0.5:
                gaming_status += f"🦶 Footsteps: {footstep_confidence:.1f} | "
            
            if high_priority_sounds:
                gaming_status += f"🔊 Sounds: {', '.join(high_priority_sounds)} | "
            
            gaming_status += f"Enhancement: {'ON' if self.gaming_mode_active else 'OFF'}"
            
            # Update the info label with gaming information
            current_text = self.info_label.text()
            if " | Gaming:" not in current_text:
                self.info_label.setText(f"{current_text} | Gaming: {gaming_status}")
            else:
                # Replace gaming info
                parts = current_text.split(" | Gaming:")
                self.info_label.setText(f"{parts[0]} | Gaming: {gaming_status}")
                
        except Exception as e:
            print(f"Error updating gaming info: {e}")
    
    def update_gaming_volume_info(self, message):
        """Update volume info with gaming-specific information"""
        try:
            # This replaces the normal volume info when in gaming mode
            self.update_volume_info(message)
        except Exception as e:
            print(f"Error updating gaming volume info: {e}")

    def manual_aura_toggle(self, checked): pass

    def set_aura_status(self, is_active):
        if is_active != self.is_focused:
            self.is_focused = is_active
            if is_active:
                self.status_label.setText('STATUS: ACTIVE')
                self.status_label.setStyleSheet("color: #2ecc71;")
                if not self.aura_toggle.isChecked(): self.aura_toggle.setChecked(True)
                self.gradually_set_volume(0.2)
            else:
                self.status_label.setText('STATUS: INACTIVE')
                self.status_label.setStyleSheet("color: #FF4757;")
                if self.aura_toggle.isChecked(): self.aura_toggle.setChecked(False)
                self.gradually_set_volume(1.0)

    def gradually_set_volume(self, target_level, steps=10, delay_ms=50):
        """Gradually change volume to avoid jarring transitions"""
        try:
            current_level = self.current_volume_level
            step_size = (target_level - current_level) / steps
            
            def update_volume_step(step):
                if step >= steps:
                    self.set_system_volume(target_level)
                    self.current_volume_level = target_level
                    return
                    
                new_level = current_level + (step_size * (step + 1))
                self.set_system_volume(new_level)
                
                # Schedule next step
                QTimer.singleShot(delay_ms, lambda: update_volume_step(step + 1))
            
            update_volume_step(0)
            
        except Exception as e:
            print(f"Error in gradual volume change: {e}")
            # Fallback to immediate change
            self.set_system_volume(target_level)
            self.current_volume_level = target_level

    def set_system_volume(self, level):
        """Enhanced volume control with better error handling and options"""
        try:
            mute_list_text = self.mute_list_input.text().lower().strip()
            apps_to_mute = [app.strip() for app in mute_list_text.split(',') if app.strip()]
            
            # If no apps specified, show available processes
            if not apps_to_mute:
                try:
                    from pycaw.pycaw import AudioUtilities
                    sessions = AudioUtilities.GetAllSessions()
                    available_apps = []
                    for session in sessions:
                        if session.Process and session.Process.name():
                            available_apps.append(session.Process.name().lower())
                    self.update_volume_info(f"Available apps: {', '.join(available_apps[:3])}...")
                except Exception as e:
                    print(f"Error listing processes: {e}")
                return

            # Import pycaw components
            try:
                from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
            except ImportError:
                print("ERROR: pycaw not available - volume control disabled")
                self.update_volume_info("pycaw module not found")
                return
                
            sessions = AudioUtilities.GetAllSessions()
            apps_found = []
            
            for session in sessions:
                if session.Process and session.Process.name():
                    process_name = session.Process.name().lower()
                    
                    # Check if this app should be muted
                    for app_to_mute in apps_to_mute:
                        if app_to_mute in process_name:
                            try:
                                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                                
                                # Clamp volume level between 0 and 1
                                clamped_level = max(0.0, min(1.0, level))
                                volume.SetMasterVolume(clamped_level, None)
                                apps_found.append(process_name)
                                
                            except Exception as app_error:
                                print(f"Error setting volume for {process_name}: {app_error}")
            
            # Update info label with found apps
            if apps_found:
                self.update_volume_info(f"Controlling: {', '.join(set(apps_found))}")
            else:
                available_processes = []
                for session in sessions:
                    if session.Process and session.Process.name():
                        available_processes.append(session.Process.name().lower())
                self.update_volume_info(f"No matches. Available: {', '.join(available_processes[:3])}...")
                
        except Exception as e:
            print(f"ERROR in set_system_volume: {e}")
            self.update_volume_info(f"Volume error: {str(e)}")

    def update_volume_info(self, message):
        """Update the info label with volume control information"""
        try:
            current_text = self.info_label.text()
            if "Head Angle" in current_text:
                # Preserve head angle info, add volume info
                parts = current_text.split(" | ")
                head_info = parts[0] if parts else current_text
                self.info_label.setText(f"{head_info} | {message}")
            else:
                self.info_label.setText(message)
        except:
            pass

    def play_demo_sound(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.setPosition(0)
        else:
            self.player.play()
    
    def update_threshold_label(self, value): 
        self.threshold_label.setText(f"Eye Openness Threshold ({value / 100.0:.2f}):")
        
    def update_sensitivity_label(self, value): 
        sensitivity_desc = "Very High" if value > 25 else "High" if value > 20 else "Medium" if value > 10 else "Low"
        self.sensitivity_label.setText(f"Focus Sensitivity - {sensitivity_desc} ({value}):")

    def toggle_gaming_mode(self, enabled):
        """Toggle gaming mode on/off"""
        if enabled:
            game_name = self.game_selector.currentText().lower().replace(" ", "_")
            game_map = {
                "valorant": "valorant",
                "cs2": "cs2", 
                "apex_legends": "apex",
                "general_fps": "general_fps"
            }
            
            mapped_game = game_map.get(game_name, "valorant")
            
            if self.start_gaming_mode(mapped_game):
                self.gaming_mode_checkbox.setStyleSheet("QCheckBox { color: #00FF7F; spacing: 10px; }")
                print(f"🎮 Gaming mode enabled for {self.game_selector.currentText()}")
            else:
                self.gaming_mode_checkbox.setChecked(False)
                self.gaming_mode_checkbox.setStyleSheet("QCheckBox { color: #FF4757; spacing: 10px; }")
                print("❌ Failed to enable gaming mode")
        else:
            self.stop_gaming_mode()
            self.gaming_mode_checkbox.setStyleSheet("QCheckBox { color: #CCC; spacing: 10px; }")
            print("🎮 Gaming mode disabled")
    
    def change_game_profile(self, game_text):
        """Change game profile when dropdown selection changes"""
        if self.gaming_mode_active:
            game_name = game_text.lower().replace(" ", "_")
            game_map = {
                "valorant": "valorant",
                "cs2": "cs2",
                "apex_legends": "apex", 
                "general_fps": "general_fps"
            }
            
            mapped_game = game_map.get(game_name, "valorant")
            self.game_audio_analyzer.set_game_profile(mapped_game)
            self.current_game = mapped_game
            print(f"🎮 Switched to {game_text} profile")

    def update_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return
            
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image_size = gray.shape
        
        if not self.predictor:
            self.info_label.setText("Face detection unavailable - predictor not loaded")
            self.display_frame(frame)
            return
            
        # Detect faces
        faces = self.detector(gray, 0)
        
        if len(faces) > 0:
            # Use the largest face for more stable tracking
            face = max(faces, key=lambda rect: rect.width() * rect.height())
            
            try:
                # Get facial landmarks
                shape = self.predictor(gray, face)
                shape = np.array([(shape.part(i).x, shape.part(i).y) for i in range(68)])
                
                # Calculate eye aspect ratios
                leftEye = shape[self.lStart:self.lEnd]
                rightEye = shape[self.rStart:self.rEnd]
                
                leftEAR = self.eye_aspect_ratio(leftEye)
                rightEAR = self.eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                
                # Enhanced head pose estimation
                pose_data, confidence = self.calculate_head_pose(shape, image_size)
                
                if pose_data and confidence > 0.3:  # Only use poses with reasonable confidence
                    # Apply temporal smoothing
                    smoothed_pose = self.smooth_pose_estimation(pose_data)
                    
                    if smoothed_pose:
                        yaw = smoothed_pose['yaw']
                        pitch = smoothed_pose['pitch']
                        roll = smoothed_pose['roll']
                        
                        # Enhanced focus condition with hybrid detection
                        ear_threshold = self.threshold_slider.value() / 100.0
                        ear_consec_frames = self.sensitivity_slider.value()
                        
                        # Get screen activity score
                        activity_score = self.get_screen_activity_score()
                        
                        # More lenient angle requirements for better multi-monitor support
                        is_looking_forward = (
                            abs(yaw) < 45 and      # Increased from 25° to 45° for side monitors
                            abs(pitch) < 30 and    # Increased from 20° to 30° for better tolerance
                            abs(roll) < 25         # Increased from 15° to 25° for head tilt tolerance
                        )
                        
                        is_eyes_open = ear > ear_threshold
                        has_good_confidence = confidence > 0.3  # Reduced from 0.5 to 0.3 for more sensitive detection
                        
                        # Progressive confidence scaling - lower thresholds for off-angle detection
                        if abs(yaw) > 25:  # Off-angle detection
                            has_good_confidence = confidence > 0.2  # Even more lenient for off-angle
                        
                        # Use hybrid focus scoring
                        hybrid_score = self.get_hybrid_focus_score(
                            face_detected=True,
                            pose_valid=is_looking_forward,
                            confidence=confidence,
                            ear_valid=is_eyes_open,
                            activity_score=activity_score
                        )
                        
                        # Apply sensitivity slider to hybrid score threshold
                        # Lower sensitivity = higher threshold needed
                        # Higher sensitivity = lower threshold needed
                        sensitivity_factor = (self.sensitivity_slider.value() / 30.0)  # 0.033 to 1.0
                        focus_threshold = 0.7 - (sensitivity_factor * 0.3)  # 0.4 to 0.7 threshold range
                        
                        # Update info display with comprehensive information
                        confidence_status = "✓" if has_good_confidence else "✗"
                        angle_status = "✓" if is_looking_forward else "✗"
                        eye_status = "✓" if is_eyes_open else "✗"
                        activity_status = f"{activity_score:.1f}"
                        
                        self.info_label.setText(
                            f"Y{yaw:.0f}°P{pitch:.0f}°R{roll:.0f}° | "
                            f"C{confidence:.2f}{confidence_status} | A{angle_status} | E{eye_status} | "
                            f"Act:{activity_status} | Focus:{hybrid_score:.2f}/{focus_threshold:.2f}"
                        )
                        
                        # Enhanced focus logic with hybrid scoring
                        if hybrid_score > focus_threshold:
                            self.focus_counter += 1
                            if self.focus_counter >= max(1, ear_consec_frames // 2):  # Faster activation
                                self.set_aura_status(True)
                        else:
                            self.focus_counter = max(0, self.focus_counter - 1)  # Gradual decay
                            if self.focus_counter <= 0:
                                self.set_aura_status(False)
                        
                        # Apply gaming audio enhancements if in gaming mode
                        if self.gaming_mode_active:
                            self.apply_gaming_audio_enhancements()
                        
                        # Visualize pose estimation on frame
                        self.draw_pose_visualization(frame, shape, smoothed_pose)
                    else:
                        self.handle_pose_estimation_failure()
                else:
                    self.handle_pose_estimation_failure()
                    
                # Draw facial landmarks for debugging
                self.draw_facial_landmarks(frame, shape)
                
            except Exception as e:
                print(f"Error processing face landmarks: {e}")
                self.handle_pose_estimation_failure()
        else:
            # No face detected - use screen activity as fallback (if enabled)
            if self.multimonitor_checkbox.isChecked():
                activity_score = self.get_screen_activity_score()
                
                # If high screen activity, consider user might be focused on another monitor
                if activity_score > 0.7:
                    hybrid_score = self.get_hybrid_focus_score(
                        face_detected=False,
                        pose_valid=False,
                        confidence=0,
                        ear_valid=False,
                        activity_score=activity_score
                    )
                    
                    sensitivity_factor = (self.sensitivity_slider.value() / 30.0)
                    focus_threshold = 0.7 - (sensitivity_factor * 0.3)
                    
                    self.info_label.setText(
                        f"No face detected | Screen Activity: {activity_score:.2f} | "
                        f"Focus Score: {hybrid_score:.2f}/{focus_threshold:.2f} | Multi-monitor mode"
                    )
                    
                    if hybrid_score > focus_threshold:
                        self.focus_counter += 1
                        if self.focus_counter >= max(1, self.sensitivity_slider.value() // 3):
                            self.set_aura_status(True)
                    else:
                        self.focus_counter = max(0, self.focus_counter - 1)
                        if self.focus_counter <= 0:
                            self.set_aura_status(False)
                    
                    # Apply gaming audio enhancements if in gaming mode
                    if self.gaming_mode_active:
                        self.apply_gaming_audio_enhancements()
                else:
                    # Low activity and no face - definitely not focused
                    self.focus_counter = 0
                    self.set_aura_status(False)
                    
                    # Still apply gaming enhancements even if not focused
                    if self.gaming_mode_active:
                        self.apply_gaming_audio_enhancements()
                    
                    self.info_label.setText(
                        f"No face detected | Low screen activity ({activity_score:.2f}) | "
                        "Position yourself in camera view or increase activity on screen"
                    )
            else:
                # Multi-monitor mode disabled - require face detection
                self.focus_counter = 0
                self.set_aura_status(False)
                self.info_label.setText("No face detected - please position yourself in view of the camera")
            
        self.display_frame(frame)

    def handle_pose_estimation_failure(self):
        """Handle cases where pose estimation fails"""
        self.focus_counter = max(0, self.focus_counter - 3)  # Rapid decay when tracking fails
        if self.focus_counter <= 0:
            self.set_aura_status(False)
        self.info_label.setText("Pose estimation failed - please ensure good lighting and clear face view")

    def draw_pose_visualization(self, frame, shape, pose_data):
        """Draw pose estimation visualization on the frame"""
        try:
            # Draw coordinate axes for head pose
            if pose_data and 'rotation_vector' in pose_data and 'translation_vector' in pose_data:
                # Project 3D axes onto 2D image plane for visualization
                nose_tip = (int(shape[30][0]), int(shape[30][1]))
                
                # Create 3D axis points
                axis_points = np.array([
                    [50, 0, 0],    # X-axis (red)
                    [0, 50, 0],    # Y-axis (green) 
                    [0, 0, -50]    # Z-axis (blue)
                ], dtype=np.float64)
                
                # Camera parameters (simplified)
                focal_length = frame.shape[1] * 1.1
                center = (frame.shape[1] / 2, frame.shape[0] / 2)
                camera_matrix = np.array([
                    [focal_length, 0, center[0]],
                    [0, focal_length, center[1]],
                    [0, 0, 1]
                ], dtype=np.float64)
                dist_coeffs = np.zeros((4, 1))
                
                # Project 3D points to 2D
                projected_points, _ = cv2.projectPoints(
                    axis_points,
                    pose_data['rotation_vector'],
                    pose_data['translation_vector'],
                    camera_matrix,
                    dist_coeffs
                )
                
                # Draw axes
                projected_points = projected_points.reshape(-1, 2).astype(int)
                cv2.line(frame, nose_tip, tuple(projected_points[0]), (0, 0, 255), 3)  # X-axis (red)
                cv2.line(frame, nose_tip, tuple(projected_points[1]), (0, 255, 0), 3)  # Y-axis (green)
                cv2.line(frame, nose_tip, tuple(projected_points[2]), (255, 0, 0), 3)  # Z-axis (blue)
                
        except Exception as e:
            print(f"Error drawing pose visualization: {e}")

    def draw_facial_landmarks(self, frame, shape):
        """Draw facial landmarks with different colors for different features"""
        try:
            # Draw eye landmarks in green
            for i in range(36, 48):
                cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (0, 255, 0), -1)
            
            # Draw nose landmarks in blue
            for i in range(27, 36):
                cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (255, 0, 0), -1)
                
            # Draw mouth landmarks in red
            for i in range(48, 68):
                cv2.circle(frame, (shape[i][0], shape[i][1]), 2, (0, 0, 255), -1)
                
            # Highlight key points used in pose estimation
            key_points = [30, 8, 45, 36, 54, 48, 27, 42, 39]  # Points used in 3D model
            for i in key_points:
                cv2.circle(frame, (shape[i][0], shape[i][1]), 4, (255, 255, 0), 2)
                
        except Exception as e:
            print(f"Error drawing facial landmarks: {e}")

    def display_frame(self, frame):
        """Convert and display the frame in the UI"""
        try:
            display_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = display_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(display_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            p = convert_to_qt_format.scaled(240, 180, Qt.AspectRatioMode.KeepAspectRatio)
            self.webcam_feed.setPixmap(QPixmap.fromImage(p))
        except Exception as e:
            print(f"Error displaying frame: {e}")

    def closeEvent(self, event):
        """Cleanup when application closes"""
        try:
            # Stop gaming mode if active
            if self.gaming_mode_active:
                self.stop_gaming_mode()
            
            # Restore volume to normal levels
            self.set_system_volume(1.0)
            
            # Release camera
            if hasattr(self, 'capture') and self.capture is not None:
                self.capture.release()
                
            # Stop timer
            if hasattr(self, 'timer') and self.timer is not None:
                self.timer.stop()
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            event.accept()