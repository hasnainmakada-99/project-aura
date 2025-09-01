"""
Human Expression & Behavior Detection System for Project AURA
Detects emotions like frustration, exhaustion, stress, and happiness
Provides actionable insights and automated responses
"""

import cv2
import numpy as np
import time
import psutil
from collections import deque
from enum import Enum
import math

class EmotionState(Enum):
    NEUTRAL = "neutral"
    FOCUSED = "focused"
    FRUSTRATED = "frustrated"
    EXHAUSTED = "exhausted"
    STRESSED = "stressed"
    HAPPY = "happy"
    SAD = "sad"
    CONFUSED = "confused"
    CONCENTRATED = "concentrated"
    TIRED = "tired"
    EXCITED = "excited"

class BehaviorPattern(Enum):
    NORMAL = "normal"
    INTENSE_GAMING = "intense_gaming"
    STUDY_SESSION = "study_session"
    TAKING_BREAK = "taking_break"
    MULTITASKING = "multitasking"
    PROBLEM_SOLVING = "problem_solving"

class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detection system"""
        
        # --- Emotion Detection Parameters ---
        self.emotion_history = deque(maxlen=30)  # 30 frames of emotion history
        self.behavior_history = deque(maxlen=60)  # 60 seconds of behavior history
        self.current_emotion = EmotionState.NEUTRAL
        self.current_behavior = BehaviorPattern.NORMAL
        self.emotion_confidence = 0.0
        
        # --- Facial Expression Analysis ---
        self.expression_metrics = {
            'brow_furrow': 0.0,      # Frustration indicator
            'eye_squint': 0.0,       # Concentration/strain indicator
            'mouth_tension': 0.0,    # Stress indicator
            'eye_openness': 0.0,     # Alertness/exhaustion indicator
            'head_tilt_frequency': 0.0,  # Confusion indicator
            'micro_expressions': 0.0,    # Subtle emotion changes
            'happiness': 0.0,        # Smile detection and positive expressions
            'sadness': 0.0,          # Frown detection and negative expressions
        }
        
        # --- Behavioral Pattern Analysis ---
        self.behavior_metrics = {
            'typing_rhythm': deque(maxlen=20),     # Typing pattern analysis
            'mouse_movement_jitter': deque(maxlen=20),  # Mouse movement stress
            'screen_focus_duration': deque(maxlen=10),  # Attention span
            'head_movement_frequency': deque(maxlen=15), # Restlessness
            'blinking_pattern': deque(maxlen=25),       # Fatigue indicator
            'posture_changes': deque(maxlen=12),        # Comfort level
        }
        
        # --- Multi-Monitor Behavior Detection ---
        self.multi_monitor_metrics = {
            'window_switching_frequency': 0.0,
            'cursor_speed_variance': 0.0,
            'app_focus_duration': {},
            'keyboard_typing_intensity': 0.0,
            'break_frequency': 0.0,
        }
        
        # --- Timing and State ---
        self.last_analysis_time = time.time()
        self.session_start_time = time.time()
        self.last_emotion_change = time.time()
        self.emotion_stability_timer = 0.0
        
        # --- Baseline Calibration ---
        self.baseline_established = False
        self.baseline_metrics = {}
        self.calibration_frames = 0
        self.calibration_required = 60  # 60 frames for baseline
        
        print("🧠 Emotion Detection System initialized!")
        print("📊 Ready to analyze human expressions and behavior patterns")

    def analyze_facial_expression(self, landmarks, frame):
        """Analyze facial landmarks to detect emotions"""
        if landmarks is None or len(landmarks) < 68:
            return
            
        try:
            # --- Brow Analysis (Frustration/Concentration) ---
            left_brow = np.array([landmarks[17], landmarks[18], landmarks[19], landmarks[20], landmarks[21]])
            right_brow = np.array([landmarks[22], landmarks[23], landmarks[24], landmarks[25], landmarks[26]])
            
            # Calculate brow furrow (distance between inner brow points)
            brow_center_distance = np.linalg.norm(landmarks[21] - landmarks[22])
            brow_height = (landmarks[19][1] + landmarks[24][1]) / 2
            
            # Normalize brow furrow (lower = more furrowed = frustrated)
            self.expression_metrics['brow_furrow'] = max(0, (brow_center_distance - 15) / 25)
            
            # --- Eye Analysis (Alertness/Exhaustion) ---
            left_eye = landmarks[36:42]
            right_eye = landmarks[42:48]
            
            # Calculate eye aspect ratio for both eyes
            left_ear = self._calculate_eye_aspect_ratio(left_eye)
            right_ear = self._calculate_eye_aspect_ratio(right_eye)
            avg_ear = (left_ear + right_ear) / 2
            
            # Eye openness (lower = more tired/exhausted)
            self.expression_metrics['eye_openness'] = min(1.0, avg_ear * 4)
            
            # Eye squinting (higher = more concentration/strain)
            self.expression_metrics['eye_squint'] = max(0, (0.25 - avg_ear) * 5)
            
            # --- Enhanced Mouth Analysis (Happiness/Sadness Detection) ---
            mouth_landmarks = landmarks[48:68]
            
            # Mouth corner analysis for emotion detection
            left_corner = landmarks[48]   # Left mouth corner
            right_corner = landmarks[54]  # Right mouth corner
            mouth_center = landmarks[51]  # Top lip center
            mouth_bottom = landmarks[57]  # Bottom lip center
            
            # Calculate mouth dimensions
            mouth_width = np.linalg.norm(left_corner - right_corner)
            mouth_height = np.linalg.norm(mouth_center - mouth_bottom)
            
            # --- HAPPINESS DETECTION ---
            # Calculate smile curvature (corners HIGHER than center means LOWER Y values)
            corner_height_avg = (left_corner[1] + right_corner[1]) / 2
            # For smiles: corners are above (lower Y) the mouth center
            smile_curvature = max(0, (corner_height_avg - mouth_center[1]) / mouth_width * -1)
            # Normalize and amplify only if significantly curved
            smile_curvature = max(0, smile_curvature * 8) if smile_curvature >= 0.08 else 0  # Lowered threshold
            
            # Cheek elevation detection (more reliable happiness indicator)
            left_cheek = landmarks[31]   # Left nostril base
            right_cheek = landmarks[35]  # Right nostril base
            nostril_height = (left_cheek[1] + right_cheek[1]) / 2
            # When smiling, nostrils tend to move up (lower Y) relative to mouth
            cheek_elevation = max(0, (mouth_center[1] - nostril_height) / 25)  # More sensitive
            
            # Eye constriction during genuine smile (Duchenne markers)
            left_eye_height = abs(landmarks[37][1] - landmarks[41][1])  # Left eye height
            right_eye_height = abs(landmarks[44][1] - landmarks[46][1])  # Right eye height
            avg_eye_height = (left_eye_height + right_eye_height) / 2
            # Smaller eye height during smiles (but not too small)
            eye_smile_indicator = max(0, (10 - avg_eye_height) / 10) if avg_eye_height < 10 else 0
            
            # Combined happiness score - require positive indicators
            happiness_indicators = [smile_curvature, cheek_elevation, eye_smile_indicator]
            if sum(1 for x in happiness_indicators if x > 0.15) >= 1:  # At least 1 strong indicator
                happiness_score = (smile_curvature * 0.6 + 
                                 cheek_elevation * 0.3 + 
                                 eye_smile_indicator * 0.1)
            else:
                happiness_score = 0
            self.expression_metrics['happiness'] = min(1.0, happiness_score)
            
            # --- SADNESS DETECTION ---
            # Mouth corners drooping (corners LOWER than center means HIGHER Y values)
            frown_curvature = max(0, (corner_height_avg - mouth_center[1]) / mouth_width)
            # Only consider significant frowns
            frown_curvature = frown_curvature * 8 if frown_curvature >= 0.08 else 0  # Match happiness threshold
            
            # Inner brow raising (sadness indicator)
            inner_brow_left = landmarks[21]
            inner_brow_right = landmarks[22]
            outer_brow_left = landmarks[17]
            outer_brow_right = landmarks[26]
            
            # Calculate brow inner elevation relative to outer
            inner_brow_height = (inner_brow_left[1] + inner_brow_right[1]) / 2
            outer_brow_height = (outer_brow_left[1] + outer_brow_right[1]) / 2
            # Inner brow higher (lower Y) during sadness
            brow_inner_raise = max(0, (outer_brow_height - inner_brow_height) / 12)  # More sensitive
            
            # Upper eyelid drooping (sadness/tiredness)
            eyelid_droop = max(0, (8 - avg_eye_height) / 8) if avg_eye_height < 6 else 0
            
            # Combined sadness score - avoid conflict with happiness
            if happiness_score < 0.4:  # Only detect sadness when not clearly happy
                sadness_indicators = [frown_curvature, brow_inner_raise, eyelid_droop]
                if sum(1 for x in sadness_indicators if x > 0.15) >= 1:  # At least 1 indicator
                    sadness_score = (frown_curvature * 0.6 + 
                                   brow_inner_raise * 0.3 + 
                                   eyelid_droop * 0.1)
                else:
                    sadness_score = 0
            else:
                sadness_score = 0
            self.expression_metrics['sadness'] = min(1.0, sadness_score)
            
            # Mouth tension (stress indicator) - updated calculation
            mouth_opening = np.linalg.norm(mouth_center - mouth_bottom)
            mouth_compression = max(0, (mouth_width / 40) - (mouth_opening / 10))
            self.expression_metrics['mouth_tension'] = min(1.0, mouth_compression)
            
            # --- Advanced Micro-Expression Detection ---
            self._detect_micro_expressions(landmarks)
            
        except Exception as e:
            print(f"⚠️ Expression analysis error: {e}")

    def _calculate_eye_aspect_ratio(self, eye_landmarks):
        """Calculate eye aspect ratio for alertness detection"""
        try:
            # Vertical eye landmarks
            A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
            B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
            
            # Horizontal eye landmark
            C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
            
            if C == 0:
                return 0.25
                
            ear = (A + B) / (2.0 * C)
            return ear
        except:
            return 0.25

    def _detect_micro_expressions(self, landmarks):
        """Detect subtle micro-expressions that indicate emotional state"""
        try:
            # Nostril flare detection (stress/anger)
            nostril_width = np.linalg.norm(landmarks[31] - landmarks[35])
            
            # Lip compression (frustration)
            upper_lip = landmarks[51]
            lower_lip = landmarks[57]
            lip_compression = np.linalg.norm(upper_lip - lower_lip)
            
            # Jaw tension (stress)
            jaw_left = landmarks[3]
            jaw_right = landmarks[13]
            jaw_center = landmarks[8]
            jaw_tension = abs((jaw_left[1] + jaw_right[1]) / 2 - jaw_center[1])
            
            # Combine micro-expressions
            micro_stress = (nostril_width / 20) + (1 / max(lip_compression, 1)) + (jaw_tension / 10)
            self.expression_metrics['micro_expressions'] = min(1.0, micro_stress / 3)
            
        except Exception as e:
            pass  # Micro-expressions are optional

    def analyze_behavioral_patterns(self, head_pose, activity_data):
        """Analyze behavioral patterns from head movement and system activity"""
        current_time = time.time()
        
        try:
            # --- Head Movement Pattern Analysis ---
            if head_pose and len(head_pose) >= 3:
                yaw, pitch, roll = head_pose[:3]
                
                # Calculate head movement frequency (restlessness indicator)
                movement_magnitude = abs(yaw) + abs(pitch) + abs(roll)
                self.behavior_metrics['head_movement_frequency'].append(movement_magnitude)
                
                # Head tilt frequency (confusion indicator)
                if abs(roll) > 5:  # Significant head tilt
                    self.expression_metrics['head_tilt_frequency'] += 0.1
                else:
                    self.expression_metrics['head_tilt_frequency'] *= 0.95
                    
                self.expression_metrics['head_tilt_frequency'] = min(1.0, self.expression_metrics['head_tilt_frequency'])
            
            # --- System Activity Analysis ---
            if activity_data:
                cpu_usage = activity_data.get('cpu_usage', 0)
                memory_usage = activity_data.get('memory_usage', 0)
                mouse_activity = activity_data.get('mouse_activity', 0)
                keyboard_activity = activity_data.get('keyboard_activity', 0)
                
                # Typing rhythm analysis (stress indicator)
                self.behavior_metrics['typing_rhythm'].append(keyboard_activity)
                
                # Mouse jitter analysis (frustration indicator)
                self.behavior_metrics['mouse_movement_jitter'].append(mouse_activity)
                
                # Screen focus duration (attention span)
                focus_duration = current_time - self.last_analysis_time
                self.behavior_metrics['screen_focus_duration'].append(focus_duration)
            
        except Exception as e:
            print(f"⚠️ Behavioral analysis error: {e}")
        
        self.last_analysis_time = current_time

    def detect_emotion_state(self):
        """Determine current emotional state based on all metrics"""
        try:
            # --- HAPPINESS DETECTION ---
            happiness_score = (
                self.expression_metrics['happiness'] * 0.6 +        # Primary indicator
                (1 - self.expression_metrics['mouth_tension']) * 0.2 +  # Relaxed mouth
                self.expression_metrics['eye_openness'] * 0.2       # Alert, bright eyes
            )
            
            # --- SADNESS DETECTION ---
            sadness_score = (
                self.expression_metrics['sadness'] * 0.5 +          # Primary indicator
                (1 - self.expression_metrics['eye_openness']) * 0.25 +  # Droopy eyes
                self.expression_metrics['brow_furrow'] * 0.25       # Furrowed brow
            )
            
            # --- FRUSTRATION DETECTION ---
            frustration_score = (
                (1 - self.expression_metrics['brow_furrow']) * 0.3 +
                self.expression_metrics['mouth_tension'] * 0.25 +
                self.expression_metrics['micro_expressions'] * 0.2 +
                self._get_behavioral_stress_score() * 0.25
            )
            
            # --- EXHAUSTION DETECTION ---
            exhaustion_score = (
                (1 - self.expression_metrics['eye_openness']) * 0.4 +
                self._get_blinking_fatigue_score() * 0.3 +
                self._get_posture_fatigue_score() * 0.3
            )
            
            # --- STRESS DETECTION ---
            stress_score = (
                self.expression_metrics['micro_expressions'] * 0.3 +
                self.expression_metrics['mouth_tension'] * 0.25 +
                self._get_behavioral_stress_score() * 0.45
            )
            
            # --- CONCENTRATION DETECTION ---
            concentration_score = (
                self.expression_metrics['eye_squint'] * 0.3 +
                (1 - self._get_head_movement_score()) * 0.4 +
                self._get_focus_duration_score() * 0.3
            )
            
            # --- CONFUSION DETECTION ---
            confusion_score = (
                self.expression_metrics['head_tilt_frequency'] * 0.4 +
                self._get_behavioral_confusion_score() * 0.6
            )
            
            # --- DETERMINE DOMINANT EMOTION ---
            emotion_scores = {
                EmotionState.HAPPY: happiness_score,
                EmotionState.SAD: sadness_score,
                EmotionState.FRUSTRATED: frustration_score,
                EmotionState.EXHAUSTED: exhaustion_score,
                EmotionState.STRESSED: stress_score,
                EmotionState.CONCENTRATED: concentration_score,
                EmotionState.CONFUSED: confusion_score,
            }
            
            # Find highest scoring emotion
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            # Enhanced confidence thresholds for better detection
            if max_emotion[1] > 0.5:  # Lowered threshold for better sensitivity
                new_emotion = max_emotion[0]
                self.emotion_confidence = min(0.95, max_emotion[1])
            elif max_emotion[1] > 0.3:  # Medium confidence
                new_emotion = max_emotion[0]
                self.emotion_confidence = max_emotion[1] * 0.8
            else:
                new_emotion = EmotionState.NEUTRAL
                self.emotion_confidence = 0.3
            
            # Special handling for happy/sad states (more immediate detection)
            if new_emotion in [EmotionState.HAPPY, EmotionState.SAD]:
                if max_emotion[1] > 0.4:  # Lower threshold for emotional states
                    self.current_emotion = new_emotion
                    self.emotion_confidence = max_emotion[1]
                    self.last_emotion_change = time.time()
                    self.emotion_stability_timer = 0
                    
                    # Update emotion history immediately for emotional states
                    self.emotion_history.append({
                        'emotion': self.current_emotion,
                        'confidence': self.emotion_confidence,
                        'timestamp': time.time(),
                        'scores': emotion_scores
                    })
                    return
            
            # Smooth emotion transitions for other states
            if new_emotion != self.current_emotion:
                if self.emotion_stability_timer > 2:  # Reduced from 3 to 2 seconds
                    self.current_emotion = new_emotion
                    self.last_emotion_change = time.time()
                    self.emotion_stability_timer = 0
                else:
                    self.emotion_stability_timer += 0.1
            else:
                self.emotion_stability_timer += 0.1
            
            # Update emotion history
            self.emotion_history.append({
                'emotion': self.current_emotion,
                'confidence': self.emotion_confidence,
                'timestamp': time.time(),
                'scores': emotion_scores
            })
            
        except Exception as e:
            print(f"⚠️ Emotion detection error: {e}")
            self.current_emotion = EmotionState.NEUTRAL
            self.emotion_confidence = 0.0

    def _get_behavioral_stress_score(self):
        """Calculate stress score from behavioral patterns"""
        if not self.behavior_metrics['mouse_movement_jitter']:
            return 0.0
            
        # High mouse jitter + erratic typing = stress
        mouse_variance = np.var(list(self.behavior_metrics['mouse_movement_jitter']))
        typing_variance = np.var(list(self.behavior_metrics['typing_rhythm'])) if self.behavior_metrics['typing_rhythm'] else 0
        
        return min(1.0, (mouse_variance / 100 + typing_variance / 50) / 2)

    def _get_blinking_fatigue_score(self):
        """Calculate fatigue score from blinking patterns"""
        if not self.behavior_metrics['blinking_pattern']:
            return 0.0
            
        # Slow, prolonged blinks indicate fatigue
        blink_duration = np.mean(list(self.behavior_metrics['blinking_pattern']))
        return min(1.0, blink_duration / 10)

    def _get_posture_fatigue_score(self):
        """Calculate fatigue from posture changes"""
        if not self.behavior_metrics['posture_changes']:
            return 0.0
            
        # Frequent posture changes = discomfort/fatigue
        posture_frequency = len(self.behavior_metrics['posture_changes']) / 12
        return min(1.0, posture_frequency)

    def _get_head_movement_score(self):
        """Calculate restlessness from head movement"""
        if not self.behavior_metrics['head_movement_frequency']:
            return 0.0
            
        movement_avg = np.mean(list(self.behavior_metrics['head_movement_frequency']))
        return min(1.0, movement_avg / 20)

    def _get_focus_duration_score(self):
        """Calculate attention span score"""
        if not self.behavior_metrics['screen_focus_duration']:
            return 0.5
            
        avg_focus = np.mean(list(self.behavior_metrics['screen_focus_duration']))
        return min(1.0, avg_focus / 30)  # 30 seconds = good focus

    def _get_behavioral_confusion_score(self):
        """Calculate confusion from behavioral patterns"""
        # Rapid window switching + cursor hesitation = confusion
        window_switching = self.multi_monitor_metrics.get('window_switching_frequency', 0)
        cursor_variance = self.multi_monitor_metrics.get('cursor_speed_variance', 0)
        
        return min(1.0, (window_switching / 10 + cursor_variance / 5) / 2)

    def get_emotion_summary(self):
        """Get comprehensive emotion and behavior summary"""
        return {
            'current_emotion': self.current_emotion.value,
            'confidence': self.emotion_confidence,
            'duration': time.time() - self.last_emotion_change,
            'expression_metrics': self.expression_metrics.copy(),
            'behavioral_indicators': {
                'stress_level': self._get_behavioral_stress_score(),
                'fatigue_level': self._get_blinking_fatigue_score() + self._get_posture_fatigue_score(),
                'restlessness': self._get_head_movement_score(),
                'attention_span': self._get_focus_duration_score(),
                'confusion_level': self._get_behavioral_confusion_score()
            },
            'session_duration': time.time() - self.session_start_time
        }

    def get_recommended_actions(self):
        """Get recommended actions based on detected emotional state"""
        actions = []
        
        if self.current_emotion == EmotionState.FRUSTRATED:
            actions = [
                "🎵 Play calming background music",
                "💡 Suggest a 5-minute break",
                "🎯 Reduce audio sensitivity to minimize distractions",
                "🧘 Display breathing exercise reminder",
                "🔊 Lower game volume to reduce audio stress"
            ]
            
        elif self.current_emotion == EmotionState.EXHAUSTED:
            actions = [
                "☕ Suggest taking a longer break (15-30 minutes)",
                "💤 Recommend hydration and eye rest",
                "🔅 Suggest reducing screen brightness",
                "⏰ Set a reminder to finish the session soon",
                "🎶 Play energizing but gentle music"
            ]
            
        elif self.current_emotion == EmotionState.STRESSED:
            actions = [
                "🎵 Activate stress-relief audio profile",
                "🧘 Suggest 2-minute mindfulness exercise",
                "🔊 Optimize audio for better clarity (reduce confusion)",
                "💡 Recommend organizing workspace",
                "📊 Show progress to boost confidence"
            ]
            
        elif self.current_emotion == EmotionState.CONCENTRATED:
            actions = [
                "🔒 Enter 'Do Not Disturb' mode",
                "🎯 Optimize audio for maximum focus",
                "🔇 Minimize background noise",
                "⚡ Boost gaming audio enhancement",
                "📊 Track this productive session"
            ]
            
        elif self.current_emotion == EmotionState.CONFUSED:
            actions = [
                "📚 Offer helpful tutorials or guides",
                "🔊 Enhance audio clarity and reduce complexity",
                "💡 Suggest taking a step back",
                "🎯 Simplify current audio settings",
                "📖 Display relevant help information"
            ]
            
        return actions

    def update_multi_monitor_metrics(self, system_data):
        """Update metrics specific to multi-monitor behavior analysis"""
        try:
            if system_data:
                # Window switching frequency
                active_window_count = system_data.get('active_windows', 1)
                self.multi_monitor_metrics['window_switching_frequency'] = min(10, active_window_count)
                
                # Cursor speed variance (hesitation indicator)
                cursor_speed = system_data.get('cursor_speed', 0)
                if hasattr(self, 'cursor_speeds'):
                    self.cursor_speeds.append(cursor_speed)
                    if len(self.cursor_speeds) > 10:
                        self.cursor_speeds.pop(0)
                    self.multi_monitor_metrics['cursor_speed_variance'] = np.var(self.cursor_speeds)
                else:
                    self.cursor_speeds = [cursor_speed]
                    
                # Keyboard intensity
                keyboard_rate = system_data.get('keyboard_rate', 0)
                self.multi_monitor_metrics['keyboard_typing_intensity'] = min(10, keyboard_rate)
                
        except Exception as e:
            print(f"⚠️ Multi-monitor metrics error: {e}")
