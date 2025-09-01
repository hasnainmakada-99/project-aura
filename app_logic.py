# app_logic.py
import sys
import os
import cv2
import dlib
import numpy as np
import time
import psutil
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from ui_main_window import UiMainWindow

# Import emotion detection system
try:
    from emotion_detection import EmotionDetector
    from emotion_action_system import EmotionActionSystem
    EMOTION_DETECTION_AVAILABLE = True
    print("🧠 Emotion Detection System loaded successfully!")
except ImportError as e:
    print(f"⚠️ Emotion Detection System not available: {e}")
    EMOTION_DETECTION_AVAILABLE = False

# Import audio device manager
try:
    from audio_device_manager import AudioDeviceManager, get_audio_device_manager
    AUDIO_DEVICE_MANAGER_AVAILABLE = True
    print("🎧 Audio Device Manager loaded successfully!")
except ImportError as e:
    print(f"⚠️ Audio Device Manager not available: {e}")
    AUDIO_DEVICE_MANAGER_AVAILABLE = False

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    full_path = os.path.join(base_path, relative_path)
    
    # Handle PyInstaller bug where data files become directories
    if os.path.isdir(full_path):
        # Look for the actual file in the parent directory
        parent_dir = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        
        # Check if file exists in parent directory
        alt_path = os.path.join(parent_dir, filename)
        if os.path.isfile(alt_path):
            return alt_path
            
        # Check in _internal directory structure
        internal_path = os.path.join(base_path, "_internal", relative_path)
        if os.path.isfile(internal_path):
            return internal_path
            
        # Try without the directory structure
        direct_path = os.path.join(base_path, os.path.basename(relative_path))
        if os.path.isfile(direct_path):
            return direct_path
    
    return full_path

def euclidean_distance(point1, point2):
    """Calculate euclidean distance between two points"""
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

class AppLogic(QWidget, UiMainWindow):
    def __init__(self, camera_index=0):
        super().__init__()
        self.setupUi(self)

        # --- Camera Configuration ---
        self.camera_index = camera_index
        print(f"🎥 Initializing with camera {camera_index}")

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
        
        # --- Audio Device Management ---
        self.audio_device_manager = None
        self.selected_output_device = None
        self.device_monitor_timer = None
        
        if AUDIO_DEVICE_MANAGER_AVAILABLE:
            self.audio_device_manager = get_audio_device_manager()
            print("🎧 Audio Device Manager initialized!")
        else:
            print("⚠️ Audio Device Manager not available - device selection disabled")
        
        # --- Gaming Audio Intelligence ---
        # ANTI-CHEAT SAFE MODE: Disabled for competitive gaming safety
        self.anti_cheat_safe_mode = True  # Always enabled to prevent bans
        self.game_audio_analyzer = None  # Completely removed for safety - using safe_gaming_enhancer instead
        self.gaming_mode_active = False
        self.current_game = "valorant"
        self.game_audio_enhancements = {}
        
        # Audio analysis completely removed for anti-cheat safety
        # Using safe_gaming_enhancer instead for competitive gaming advantages
        print("✅ ANTI-CHEAT SAFE MODE: Using safe gaming enhancement instead of risky audio analysis")
        
        # Initialize safe gaming enhancer instead
        try:
            from safe_gaming_enhancer import SafeGamingEnhancer
            self.safe_gaming_enhancer = SafeGamingEnhancer()
            self.safe_gaming_enhancer.enhancement_update.connect(self.update_safe_gaming_status)
            print("🛡️ Safe gaming enhancer initialized successfully!")
        except ImportError as e:
            print(f"⚠️ Could not initialize safe gaming enhancer: {e}")
            self.safe_gaming_enhancer = None
        
        # --- Emotion Detection System ---
        self.emotion_detector = None
        self.emotion_action_system = None
        
        if EMOTION_DETECTION_AVAILABLE:
            try:
                self.emotion_detector = EmotionDetector()
                self.emotion_action_system = EmotionActionSystem()
                self.emotion_action_system.set_controllers(
                    audio_controller=self,  # Use self as audio controller
                    ui_controller=self,     # Use self as UI controller
                    notification_callback=self.show_emotion_notification
                )
                print("🧠 Emotion Detection and Action System initialized!")
            except Exception as e:
                print(f"⚠️ Emotion system initialization error: {e}")
                self.emotion_detector = None
                self.emotion_action_system = None
        
        # --- Emotion State Variables ---
        self.current_emotion = "neutral"
        self.emotion_confidence = 0.0
        self.emotion_duration = 0.0
        self.last_emotion_analysis = time.time()
        self.emotion_analysis_interval = 1.0  # Analyze emotions every second
        
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
        print(f"🎥 Connecting to camera {self.camera_index}...")
        self.capture = cv2.VideoCapture(self.camera_index)
        
        # Verify camera connection
        if not self.capture.isOpened():
            print(f"❌ Failed to open camera {self.camera_index}")
            # Try to fallback to default camera
            print("🔄 Trying fallback to camera 0...")
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                print("❌ No camera available - face detection will not work")
            else:
                print("✅ Fallback camera 0 connected")
                self.camera_index = 0
        else:
            print(f"✅ Camera {self.camera_index} connected successfully")
            
        # Configure camera settings for optimal performance
        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            # Get actual camera settings
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            print(f"📹 Camera settings: {width}x{height} @ {fps}fps")
        
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
        
        # --- Connect Audio Device Signals ---
        if hasattr(self, 'refresh_devices_button'):
            self.refresh_devices_button.clicked.connect(self.refresh_audio_devices)
        if hasattr(self, 'output_device_selector'):
            self.output_device_selector.currentTextChanged.connect(self.on_audio_device_changed)
        if hasattr(self, 'auto_detect_devices_checkbox'):
            self.auto_detect_devices_checkbox.toggled.connect(self.toggle_auto_device_detection)
        
        # --- Initialize Audio Device Management ---
        self.setup_audio_device_controls()
        self.refresh_audio_devices()  # Initial device scan
        
        # Setup device monitoring timer
        if self.audio_device_manager and hasattr(self, 'auto_detect_devices_checkbox') and self.auto_detect_devices_checkbox.isChecked():
            self.start_device_monitoring()
        
        # Update camera status in UI
        self.update_camera_status()

    def update_camera_status(self):
        """Update the UI with camera status information"""
        if self.capture.isOpened():
            width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            
            camera_info = f"📹 Camera {self.camera_index}: {width}x{height} @ {fps}fps"
            status_info = f"🎯 AURA is running with verified camera. {camera_info}"
            self.info_label.setText(status_info)
            self.info_label.setStyleSheet("color: #90EE90;")  # Light green for success
        else:
            self.info_label.setText("❌ Camera not available - Face detection disabled")
            self.info_label.setStyleSheet("color: #FF6B6B;")  # Light red for error

    def eye_aspect_ratio(self, eye):
        A = euclidean_distance(eye[1], eye[5])
        B = euclidean_distance(eye[2], eye[4])
        C = euclidean_distance(eye[0], eye[3])
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
        """Start ANTI-CHEAT SAFE gaming mode with focus-based enhancement only"""
        try:
            self.current_game = game_name
            
            if self.anti_cheat_safe_mode:
                print(f"🛡️  SAFE MODE: Focus-based gaming enhancement for {game_name}")
                print("🚫 Audio analysis DISABLED for anti-cheat compatibility (Vanguard/VAC safe)")
                
                # Start safe gaming enhancer if available
                if hasattr(self, 'safe_gaming_enhancer') and self.safe_gaming_enhancer:
                    self.safe_gaming_enhancer.start_safe_enhancement()
                    print("🎯 Safe gaming enhancement started")
                    
                self.gaming_mode_active = True
                return True
            
            # Original risky audio analysis mode - REMOVED for anti-cheat safety
            # Now using safe_gaming_enhancer for competitive advantages without risk
            print("🛡️ Gaming mode activated with safe enhancement (no anti-cheat risk)")
            return True
                
        except Exception as e:
            print(f"Error starting gaming mode: {e}")
            return False
    
    def stop_gaming_mode(self):
        """Stop gaming mode and return to normal operation"""
        try:
            self.gaming_mode_active = False
            
            # Stop safe gaming enhancer if active
            if hasattr(self, 'safe_gaming_enhancer') and self.safe_gaming_enhancer:
                self.safe_gaming_enhancer.stop_safe_enhancement()
                print("🛡️ Safe gaming enhancement stopped")
                
            print("✅ Gaming mode stopped - Safe for competitive play")
            
        except Exception as e:
            print(f"Error stopping gaming mode: {e}")
    
    def apply_gaming_audio_enhancements(self):
        """Apply ANTI-CHEAT SAFE gaming enhancements based on focus detection only"""
        if not self.gaming_mode_active:
            return
            
        try:
            if self.anti_cheat_safe_mode:
                # SAFE MODE: Use safe gaming enhancer if available
                if hasattr(self, 'safe_gaming_enhancer') and self.safe_gaming_enhancer:
                    # Safe enhancer handles its own monitoring and enhancement
                    # Just ensure it's running if gaming mode is active
                    if self.gaming_mode_active and not self.safe_gaming_enhancer.is_monitoring:
                        self.safe_gaming_enhancer.start_safe_enhancement()
                    elif not self.gaming_mode_active and self.safe_gaming_enhancer.is_monitoring:
                        self.safe_gaming_enhancer.stop_safe_enhancement()
                else:
                    # Fallback to basic focus-based enhancement
                    if self.is_focused:
                        # Gaming focus detected - reduce background distractions
                        self.apply_enhanced_gaming_volume(0.3, "gaming_focus_safe")
                        self.update_gaming_volume_info("🎮 Gaming Focus: Background apps reduced")
                    else:
                        # Not focused - normal volume
                        self.apply_enhanced_gaming_volume(1.0, "normal_safe")
                        self.update_gaming_volume_info("🔊 Normal: Full volume restored")
                return
            
            # RISKY MODE: Original audio analysis - COMPLETELY REMOVED for anti-cheat safety
            # All risky audio analysis functionality has been replaced with safe_gaming_enhancer
            return
            
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
    
    def update_safe_gaming_status(self, status_message, enhancement_level):
        """Update UI with safe gaming enhancement status"""
        try:
            # Update the gaming volume info with safe enhancement status
            self.update_gaming_volume_info(status_message)
            
            # Store current enhancement level for reference
            self.current_safe_enhancement = enhancement_level
            
            # Only log when enhancement level changes to reduce spam
            if not hasattr(self, '_last_enhancement_level') or self._last_enhancement_level != enhancement_level:
                print(f"🛡️ Safe Enhancement: {status_message}")
                self._last_enhancement_level = enhancement_level
            
        except Exception as e:
            print(f"Error updating safe gaming status: {e}")
    
    def update_gaming_volume_info(self, message):
        """Update volume info with gaming-specific information"""
        try:
            # This replaces the normal volume info when in gaming mode
            self.update_volume_info(message)
        except Exception as e:
            print(f"Error updating gaming volume info: {e}")

    def manual_aura_toggle(self, checked):
        """Handle manual AURA toggle from UI"""
        try:
            print(f"🎮 Manual AURA toggle: {'ON' if checked else 'OFF'}")
            
            if checked:
                # AURA turned ON
                self.is_focused = True
                if hasattr(self, 'status_title'):
                    self.status_title.setText('STATUS: ACTIVE')
                    self.status_title.setStyleSheet("color: #90EE90; font-size: 16px; font-weight: bold;")
                self.gradually_set_volume(0.2)
                print("✅ AURA Focus Mode Activated")
                
                # Start safe gaming enhancement if available
                if hasattr(self, 'safe_gaming_enhancer') and self.safe_gaming_enhancer:
                    self.safe_gaming_enhancer.start_safe_enhancement()
                    
            else:
                # AURA turned OFF
                self.is_focused = False
                if hasattr(self, 'status_title'):
                    self.status_title.setText('STATUS: INACTIVE')
                    self.status_title.setStyleSheet("color: #FF4757; font-size: 16px; font-weight: bold;")
                self.gradually_set_volume(1.0)
                print("❌ AURA Focus Mode Deactivated")
                
                # Stop safe gaming enhancement if available
                if hasattr(self, 'safe_gaming_enhancer') and self.safe_gaming_enhancer:
                    self.safe_gaming_enhancer.stop_safe_enhancement()
                    
        except Exception as e:
            print(f"❌ Error in manual AURA toggle: {e}")

    def set_aura_status(self, is_active):
        if is_active != self.is_focused:
            self.is_focused = is_active
            if is_active:
                if hasattr(self, 'status_title'):
                    self.status_title.setText('STATUS: ACTIVE')
                    self.status_title.setStyleSheet("color: #2ecc71;")
                elif hasattr(self, 'status_label'):  # Fallback for old UI
                    self.status_label.setText('STATUS: ACTIVE')
                    self.status_label.setStyleSheet("color: #2ecc71;")
                if not self.aura_toggle.isChecked(): self.aura_toggle.setChecked(True)
                self.gradually_set_volume(0.2)
            else:
                if hasattr(self, 'status_title'):
                    self.status_title.setText('STATUS: INACTIVE')
                    self.status_title.setStyleSheet("color: #FF4757;")
                elif hasattr(self, 'status_label'):  # Fallback for old UI
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
            
            # Also control selected audio device if available
            if self.selected_output_device and self.audio_device_manager:
                try:
                    success = self.audio_device_manager.control_device_volume(
                        self.selected_output_device.id, level
                    )
                    if success:
                        current_info = self.info_label.text()
                        device_name = self.selected_output_device.name[:20] + "..." if len(self.selected_output_device.name) > 20 else self.selected_output_device.name
                        self.update_volume_info(f"{current_info} | Device: {device_name}")
                except Exception as device_error:
                    print(f"Error controlling selected device volume: {device_error}")
                
        except Exception as e:
            print(f"ERROR in set_system_volume: {e}")
            self.update_volume_info(f"Volume error: {str(e)}")

    def control_selected_device_volume(self, level):
        """Control volume specifically for the selected audio device"""
        try:
            if not self.selected_output_device or not self.audio_device_manager:
                return False
            
            # Clamp volume level
            clamped_level = max(0.0, min(1.0, level))
            
            success = self.audio_device_manager.control_device_volume(
                self.selected_output_device.id, clamped_level
            )
            
            if success:
                print(f"🔊 Controlled {self.selected_output_device.name}: {clamped_level:.2f}")
                return True
            else:
                print(f"❌ Failed to control {self.selected_output_device.name}")
                return False
                
        except Exception as e:
            print(f"❌ Error controlling selected device volume: {e}")
            return False

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
            # self.game_audio_analyzer.set_game_profile(mapped_game)  # Removed for anti-cheat safety
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
                
                # Initialize pose variables
                yaw, pitch, roll = 0, 0, 0
                if pose_data and confidence > 0.3:  # Only use poses with reasonable confidence
                    # Apply temporal smoothing
                    smoothed_pose = self.smooth_pose_estimation(pose_data)
                    
                    if smoothed_pose:
                        yaw = smoothed_pose['yaw']
                        pitch = smoothed_pose['pitch']
                        roll = smoothed_pose['roll']
                
                # --- EMOTION DETECTION ANALYSIS ---
                current_time = time.time()
                if (self.emotion_detector and 
                    current_time - self.last_emotion_analysis > self.emotion_analysis_interval):
                    
                    # Analyze facial expressions for emotions
                    self.emotion_detector.analyze_facial_expression(shape, frame)
                    
                    # Get current system activity data for behavioral analysis
                    activity_data = self.get_current_activity_data()
                    
                    # Analyze behavioral patterns (now yaw, pitch, roll are defined)
                    pose_data_for_emotion = [yaw, pitch, roll]
                    self.emotion_detector.analyze_behavioral_patterns(pose_data_for_emotion, activity_data)
                    
                    # Update multi-monitor behavior metrics
                    system_data = self.get_system_behavior_data()
                    self.emotion_detector.update_multi_monitor_metrics(system_data)
                    
                    # Detect current emotional state
                    self.emotion_detector.detect_emotion_state()
                    
                    # Get emotion summary
                    emotion_summary = self.emotion_detector.get_emotion_summary()
                    
                    # Update UI with emotion information
                    self.update_emotion_display(emotion_summary)
                    
                    # Process emotions through action system
                    if self.emotion_action_system:
                        self.emotion_action_system.process_emotion_state(emotion_summary)
                    
                    self.last_emotion_analysis = current_time
                
                # Continue with rest of the processing
                if pose_data and confidence > 0.3:
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

    # --- EMOTION DETECTION SUPPORT METHODS ---
    
    def get_current_activity_data(self):
        """Get current system activity data for emotion analysis"""
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            
            # Calculate mouse and keyboard activity (simplified)
            mouse_activity = self.mouse_activity_count
            keyboard_activity = self.keyboard_activity_count
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_info.percent,
                'mouse_activity': mouse_activity,
                'keyboard_activity': keyboard_activity,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"Activity data error: {e}")
            return {}

    def get_system_behavior_data(self):
        """Get system behavior data for multi-monitor analysis"""
        try:
            # Get active window count (simplified)
            active_windows = 1  # Placeholder - could be enhanced with actual window detection
            
            # Get cursor speed (simplified)
            cursor_speed = self.mouse_activity_count * 0.1
            
            # Get keyboard typing rate
            keyboard_rate = self.keyboard_activity_count * 0.1
            
            return {
                'active_windows': active_windows,
                'cursor_speed': cursor_speed,
                'keyboard_rate': keyboard_rate,
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"System behavior data error: {e}")
            return {}

    def update_emotion_display(self, emotion_summary):
        """Update UI with current emotion information"""
        try:
            emotion = emotion_summary['current_emotion']
            confidence = emotion_summary['confidence']
            duration = emotion_summary['duration']
            behavioral_indicators = emotion_summary['behavioral_indicators']
            
            # Update emotion state
            self.current_emotion = emotion
            self.emotion_confidence = confidence
            self.emotion_duration = duration
            
            # Create emotion status with emoji and description
            emotion_emojis = {
                'neutral': '😶',
                'focused': '🎯', 
                'frustrated': '😤',
                'exhausted': '😴',
                'stressed': '😰',
                'happy': '😊',
                'confused': '🤔',
                'concentrated': '🧠',
                'tired': '😪',
                'excited': '🤩'
            }
            
            emoji = emotion_emojis.get(emotion, '�')
            
            # Create confidence indicator
            if confidence > 0.7:
                confidence_indicator = "🔴 High"
                color_style = "color: #90EE90;"  # Light green
            elif confidence > 0.5:
                confidence_indicator = "🟡 Medium" 
                color_style = "color: #FFD700;"  # Gold
            elif confidence > 0.3:
                confidence_indicator = "🟠 Low"
                color_style = "color: #FFA500;"  # Orange
            else:
                confidence_indicator = "⚪ Detecting"
                color_style = "color: #888;"     # Gray
            
            # Update emotion status label (using new UI element names)
            emotion_text = f"{emoji} {emotion.title()} | {confidence_indicator} | {duration:.1f}s"
            if hasattr(self, 'emotion_display'):
                self.emotion_display.setText(emotion_text)
                self.emotion_display.setStyleSheet(f"font-size: 11px; {color_style} margin-bottom: 5px;")
            elif hasattr(self, 'emotion_status_label'):  # Fallback for old UI
                self.emotion_status_label.setText(emotion_text)
                self.emotion_status_label.setStyleSheet(f"font-size: 11px; {color_style} margin-bottom: 5px;")
            
            # Get recommended actions
            if self.emotion_action_system:
                recommended_actions = self.emotion_action_system.get_recommended_actions()
                
                if recommended_actions:
                    actions_text = "💡 Active: " + " | ".join(recommended_actions[:2])  # Show first 2 actions
                    actions_color = "color: #87CEEB;"  # Sky blue
                else:
                    actions_text = "✅ Optimal state - No actions needed"
                    actions_color = "color: #90EE90;"  # Light green
            else:
                actions_text = "🔄 Emotion analysis in progress..."
                actions_color = "color: #888;"
            
            # Update emotion actions label (using new UI element names)
            if hasattr(self, 'emotion_actions'):
                self.emotion_actions.setText(actions_text)
                self.emotion_actions.setStyleSheet(f"font-size: 9px; {actions_color} font-style: italic;")
            elif hasattr(self, 'emotion_actions_label'):  # Fallback for old UI
                self.emotion_actions_label.setText(actions_text)
                self.emotion_actions_label.setStyleSheet(f"font-size: 9px; {actions_color} font-style: italic;")
            
            # Add behavioral indicators to existing info label
            stress_level = behavioral_indicators.get('stress_level', 0)
            fatigue_level = behavioral_indicators.get('fatigue_level', 0)
            attention_span = behavioral_indicators.get('attention_span', 0)
            
            # Create behavioral summary
            behavioral_text = f"Stress:{stress_level:.1f} Fatigue:{fatigue_level:.1f} Focus:{attention_span:.1f}"
            
            # Add emotion info to main status display
            current_info = self.info_label.text()
            
            # Remove any existing emotion info to avoid duplication
            if " | 😊" in current_info or " | 😐" in current_info or " | �" in current_info or " | 😤" in current_info:
                # Find and remove existing emotion info
                parts = current_info.split(" | ")
                filtered_parts = [part for part in parts if not any(emote in part for emote in ['😊', '😐', '😶', '😤', '😴', '😰', '🤔', '🎯', '🧠', '😪', '🤩'])]
                current_info = " | ".join(filtered_parts)
            
            # Add new emotion info
            emotion_info = f" | {emoji} {emotion[:4].title()} | {behavioral_text}"
            self.info_label.setText(current_info + emotion_info)
                
        except Exception as e:
            print(f"Emotion display error: {e}")

    def show_emotion_notification(self, message):
        """Show emotion-based notification in the UI"""
        try:
            # Update info label with emotion notification
            print(f"🧠 EMOTION NOTIFICATION: {message}")
            
            # Could also update a dedicated emotion status area in the UI
            # For now, just print to console and potentially update status
            
        except Exception as e:
            print(f"Emotion notification error: {e}")

    # --- AUDIO CONTROLLER METHODS FOR EMOTION ACTIONS ---
    
    def reduce_background_intensity(self, factor):
        """Reduce background audio intensity (for emotion actions)"""
        try:
            # Implement audio intensity reduction
            print(f"🔊 Reducing background audio intensity by {factor}")
            # This would integrate with the existing audio control system
        except Exception as e:
            print(f"Audio intensity reduction error: {e}")

    def apply_stress_relief_profile(self):
        """Apply stress relief audio profile"""
        try:
            print("🎵 Applying stress relief audio profile")
            # Implement stress-relief audio adjustments
        except Exception as e:
            print(f"Stress relief profile error: {e}")

    def enhance_clarity(self):
        """Enhance audio clarity for confusion reduction"""
        try:
            print("🔊 Enhancing audio clarity")
            # Implement clarity enhancement
        except Exception as e:
            print(f"Audio clarity enhancement error: {e}")

    def maximize_focus_profile(self):
        """Maximize focus audio profile"""
        try:
            print("🎯 Maximizing focus audio profile")
            # Implement focus optimization
        except Exception as e:
            print(f"Focus profile error: {e}")

    def enhance_focus_frequencies(self):
        """Enhance frequencies that improve focus"""
        try:
            print("🎵 Enhancing focus frequencies")
            # Implement focus frequency enhancement
        except Exception as e:
            print(f"Focus frequency enhancement error: {e}")

    def apply_competitive_profile(self):
        """Apply competitive gaming audio profile"""
        try:
            print("🎮 Applying competitive gaming profile")
            # Implement competitive audio enhancements
        except Exception as e:
            print(f"Competitive profile error: {e}")

    def enhance_spatial_audio(self):
        """Enhance spatial audio awareness"""
        try:
            print("🎧 Enhancing spatial audio awareness")
            # Implement spatial audio enhancement
        except Exception as e:
            print(f"Spatial audio error: {e}")

    def optimize_response_audio(self):
        """Optimize audio for faster response times"""
        try:
            print("⚡ Optimizing response audio")
            # Implement response optimization
        except Exception as e:
            print(f"Response audio error: {e}")

    # === AUDIO DEVICE MANAGEMENT METHODS ===
    
    def setup_audio_device_controls(self):
        """Initialize audio device control UI"""
        try:
            if not self.audio_device_manager:
                if hasattr(self, 'device_status_label'):
                    self.device_status_label.setText("❌ Audio device management not available")
                if hasattr(self, 'output_device_selector'):
                    self.output_device_selector.setEnabled(False)
                if hasattr(self, 'refresh_devices_button'):
                    self.refresh_devices_button.setEnabled(False)
                return
            
            if hasattr(self, 'device_status_label'):
                self.device_status_label.setText("🎧 Audio device manager ready")
            print("🎧 Audio device controls initialized")
            
        except Exception as e:
            print(f"Error setting up audio device controls: {e}")
            if hasattr(self, 'device_status_label'):
                self.device_status_label.setText(f"❌ Setup error: {str(e)}")
    
    def refresh_audio_devices(self):
        """Refresh and update the audio device list"""
        try:
            if not self.audio_device_manager:
                return
            
            print("🔄 Refreshing audio devices...")
            if hasattr(self, 'device_status_label'):
                self.device_status_label.setText("🔄 Scanning for audio devices...")
            
            # Clear current items
            if hasattr(self, 'output_device_selector'):
                self.output_device_selector.clear()
            
            # Get output devices
            output_devices = self.audio_device_manager.get_output_devices()
            
            if not output_devices:
                if hasattr(self, 'output_device_selector'):
                    self.output_device_selector.addItem("❌ No audio devices found")
                if hasattr(self, 'device_status_label'):
                    self.device_status_label.setText("❌ No audio output devices detected")
                return
            
            # Add devices to selector
            default_index = 0
            if hasattr(self, 'output_device_selector'):
                for i, device in enumerate(output_devices):
                    # Create display text with status indicators
                    status_icon = "🔊" if device.is_active else "🔇"
                    default_text = " (Default)" if device.is_default else ""
                    display_text = f"{status_icon} {device.name}{default_text}"
                    
                    self.output_device_selector.addItem(display_text)
                    
                    # Set data for easy retrieval
                    self.output_device_selector.setItemData(i, device.id)
                    
                    # Remember default device index
                    if device.is_default:
                        default_index = i
                
                # Select default device
                self.output_device_selector.setCurrentIndex(default_index)
            
            # Update status
            device_count = len(output_devices)
            active_count = len([d for d in output_devices if d.is_active])
            auto_detect_on = hasattr(self, 'auto_detect_devices_checkbox') and self.auto_detect_devices_checkbox.isChecked()
            
            if hasattr(self, 'device_status_label'):
                self.device_status_label.setText(
                    f"✅ Found {device_count} devices ({active_count} active) | "
                    f"🔌 Auto-detect: {'ON' if auto_detect_on else 'OFF'}"
                )
            
            print(f"🎧 Refreshed {device_count} audio devices")
            
            # Also log device info for debugging
            if output_devices:
                print("🎧 Available output devices:")
                for device in output_devices:
                    print(f"  {device}")
            
        except Exception as e:
            print(f"❌ Error refreshing audio devices: {e}")
            if hasattr(self, 'device_status_label'):
                self.device_status_label.setText(f"❌ Refresh error: {str(e)}")
    
    def on_audio_device_changed(self, device_text):
        """Handle audio device selection change"""
        try:
            if not self.audio_device_manager or not device_text:
                return
            
            # Get device ID from current selection
            current_index = self.output_device_selector.currentIndex()
            if current_index < 0:
                return
            
            device_id = self.output_device_selector.itemData(current_index)
            if not device_id:
                return
            
            # Find device object
            output_devices = self.audio_device_manager.get_output_devices()
            selected_device = None
            for device in output_devices:
                if device.id == device_id:
                    selected_device = device
                    break
            
            if not selected_device:
                print(f"❌ Could not find device with ID: {device_id}")
                return
            
            # Update selected device
            self.selected_output_device = selected_device
            
            # Update status
            status_icon = "🔊" if selected_device.is_active else "🔇"
            self.device_status_label.setText(
                f"{status_icon} Selected: {selected_device.name} | "
                f"State: {selected_device.state.title()}"
            )
            
            print(f"🎧 Selected audio device: {selected_device.name}")
            
            # If device is not active, warn user
            if not selected_device.is_active:
                print(f"⚠️ Warning: Selected device '{selected_device.name}' is not active")
            
        except Exception as e:
            print(f"❌ Error changing audio device: {e}")
    
    def toggle_auto_device_detection(self, enabled):
        """Toggle automatic device detection"""
        try:
            if enabled:
                self.start_device_monitoring()
                print("🔌 Auto-device detection enabled")
            else:
                self.stop_device_monitoring()
                print("🔌 Auto-device detection disabled")
            
            # Update status
            current_text = self.device_status_label.text()
            if "Auto-detect:" in current_text:
                parts = current_text.split(" | Auto-detect:")
                new_text = f"{parts[0]} | Auto-detect: {'ON' if enabled else 'OFF'}"
                self.device_status_label.setText(new_text)
            
        except Exception as e:
            print(f"❌ Error toggling auto-device detection: {e}")
    
    def start_device_monitoring(self):
        """Start monitoring for audio device changes"""
        try:
            if not self.audio_device_manager:
                return
            
            # Stop existing timer if running
            self.stop_device_monitoring()
            
            # Create and start device monitoring timer
            self.device_monitor_timer = QTimer()
            self.device_monitor_timer.timeout.connect(self.check_device_changes)
            self.device_monitor_timer.start(10000)  # Check every 10 seconds
            
            print("🔌 Device monitoring started")
            
        except Exception as e:
            print(f"❌ Error starting device monitoring: {e}")
    
    def stop_device_monitoring(self):
        """Stop monitoring for audio device changes"""
        try:
            if self.device_monitor_timer:
                self.device_monitor_timer.stop()
                self.device_monitor_timer = None
                print("🔌 Device monitoring stopped")
            
        except Exception as e:
            print(f"❌ Error stopping device monitoring: {e}")
    
    def check_device_changes(self):
        """Check for audio device changes and update UI"""
        try:
            if not self.audio_device_manager:
                return
            
            # Get current device count
            current_devices = self.audio_device_manager.get_output_devices()
            current_count = len(current_devices)
            
            # Get UI device count
            ui_count = self.output_device_selector.count()
            if self.output_device_selector.itemText(0).startswith("❌"):
                ui_count = 0  # No devices in UI
            
            # Check if device count changed
            if current_count != ui_count:
                print(f"🔌 Device count changed: {ui_count} → {current_count}")
                
                # Find new devices
                if current_count > ui_count:
                    new_devices = current_devices[ui_count:]
                    for device in new_devices:
                        print(f"🔌 New device detected: {device.name}")
                    
                    # Update status with notification
                    self.device_status_label.setText(
                        f"🔌 NEW DEVICE DETECTED! Refreshing... (Found {current_count} devices)"
                    )
                
                elif current_count < ui_count:
                    print(f"🔌 Device disconnected (Count: {current_count})")
                    self.device_status_label.setText(
                        f"🔌 Device disconnected! Refreshing... (Found {current_count} devices)"
                    )
                
                # Refresh the device list
                self.refresh_audio_devices()
            
        except Exception as e:
            print(f"❌ Error checking device changes: {e}")

    def closeEvent(self, event):
        """Cleanup when application closes"""
        try:
            # Stop device monitoring
            self.stop_device_monitoring()
            
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
                
            print("🔧 AURA cleanup completed")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            event.accept()