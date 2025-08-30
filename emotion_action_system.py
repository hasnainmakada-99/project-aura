"""
Intelligent Action System for Project AURA
Automatically responds to detected human emotions and behaviors
Provides personalized assistance and environmental optimization
"""

import time
import json
import os
from enum import Enum
from collections import deque
import threading
import winsound
import subprocess

class ActionType(Enum):
    AUDIO_ADJUSTMENT = "audio_adjustment"
    BREAK_SUGGESTION = "break_suggestion"
    MUSIC_CONTROL = "music_control"
    ENVIRONMENT_OPTIMIZATION = "environment_optimization"
    NOTIFICATION = "notification"
    SYSTEM_OPTIMIZATION = "system_optimization"
    GAMING_ENHANCEMENT = "gaming_enhancement"

class ActionPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class EmotionActionSystem:
    def __init__(self):
        """Initialize the intelligent action system"""
        
        # --- Action Configuration ---
        self.enabled_actions = {
            ActionType.AUDIO_ADJUSTMENT: True,
            ActionType.BREAK_SUGGESTION: True,
            ActionType.MUSIC_CONTROL: True,
            ActionType.ENVIRONMENT_OPTIMIZATION: True,
            ActionType.NOTIFICATION: True,
            ActionType.SYSTEM_OPTIMIZATION: True,
            ActionType.GAMING_ENHANCEMENT: True,
        }
        
        # --- Action History and Timing ---
        self.action_history = deque(maxlen=50)
        self.last_action_time = {}
        self.action_cooldowns = {
            ActionType.BREAK_SUGGESTION: 300,    # 5 minutes
            ActionType.MUSIC_CONTROL: 60,        # 1 minute
            ActionType.NOTIFICATION: 120,        # 2 minutes
            ActionType.AUDIO_ADJUSTMENT: 30,     # 30 seconds
            ActionType.ENVIRONMENT_OPTIMIZATION: 180,  # 3 minutes
            ActionType.SYSTEM_OPTIMIZATION: 240, # 4 minutes
            ActionType.GAMING_ENHANCEMENT: 45,   # 45 seconds
        }
        
        # --- User Preferences and Learning ---
        self.user_preferences = self.load_user_preferences()
        self.action_effectiveness = {}  # Track which actions work best
        self.user_response_history = deque(maxlen=20)
        
        # --- Current State ---
        self.current_actions = []
        self.active_optimizations = {}
        self.break_timer = None
        self.music_player = None
        
        # --- Callback Functions ---
        self.audio_controller = None
        self.ui_controller = None
        self.notification_callback = None
        
        print("🎯 Emotion Action System initialized!")
        print("🤖 Ready to provide intelligent assistance based on emotional state")

    def set_controllers(self, audio_controller, ui_controller, notification_callback):
        """Set up controller references for taking actions"""
        self.audio_controller = audio_controller
        self.ui_controller = ui_controller
        self.notification_callback = notification_callback

    def process_emotion_state(self, emotion_summary):
        """Process detected emotion and trigger appropriate actions"""
        try:
            emotion = emotion_summary['current_emotion']
            confidence = emotion_summary['confidence']
            duration = emotion_summary['duration']
            behavioral_indicators = emotion_summary['behavioral_indicators']
            
            # Only act on high-confidence emotions that have persisted
            if confidence < 0.5 or duration < 2:
                return
            
            # Generate actions based on emotion
            if emotion == 'frustrated':
                self._handle_frustration(emotion_summary)
            elif emotion == 'exhausted':
                self._handle_exhaustion(emotion_summary)
            elif emotion == 'stressed':
                self._handle_stress(emotion_summary)
            elif emotion == 'concentrated':
                self._handle_concentration(emotion_summary)
            elif emotion == 'confused':
                self._handle_confusion(emotion_summary)
            elif emotion == 'happy':
                self._handle_happiness(emotion_summary)
            elif emotion == 'sad':
                self._handle_sadness(emotion_summary)
                
            # Additional behavioral-based actions
            self._handle_behavioral_indicators(behavioral_indicators)
            
        except Exception as e:
            print(f"⚠️ Action processing error: {e}")

    def _handle_frustration(self, emotion_summary):
        """Handle detected frustration with calming interventions"""
        duration = emotion_summary['duration']
        confidence = emotion_summary['confidence']
        
        # Progressive intervention based on duration and confidence
        if duration > 30 and confidence > 0.7:  # Sustained frustration
            self._execute_action({
                'type': ActionType.BREAK_SUGGESTION,
                'priority': ActionPriority.HIGH,
                'title': "Frustration Detected - Break Recommended",
                'message': "You've been frustrated for over 30 seconds. Consider taking a 2-minute break to reset your mindset.",
                'actions': ['Take a deep breath', 'Step away from screen', 'Stretch your shoulders'],
                'auto_audio': 'calming'
            })
            
        elif duration > 10:  # Initial frustration
            self._execute_action({
                'type': ActionType.AUDIO_ADJUSTMENT,
                'priority': ActionPriority.MEDIUM,
                'adjustment': 'reduce_intensity',
                'target': 'background_apps',
                'reason': 'Reducing audio distractions to help with frustration'
            })
            
            self._execute_action({
                'type': ActionType.MUSIC_CONTROL,
                'priority': ActionPriority.MEDIUM,
                'action': 'play_calming',
                'volume': 0.3,
                'message': "Playing calming background audio to help reduce frustration"
            })

    def _handle_exhaustion(self, emotion_summary):
        """Handle detected exhaustion with energy management"""
        duration = emotion_summary['duration']
        behavioral_indicators = emotion_summary['behavioral_indicators']
        fatigue_level = behavioral_indicators.get('fatigue_level', 0)
        
        if fatigue_level > 0.7 or duration > 60:  # High fatigue or sustained exhaustion
            self._execute_action({
                'type': ActionType.BREAK_SUGGESTION,
                'priority': ActionPriority.CRITICAL,
                'title': "High Exhaustion Detected",
                'message': "Your fatigue levels are high. Consider taking a 15-30 minute break for optimal performance.",
                'actions': [
                    'Take a longer break (15-30 min)',
                    'Get some fresh air',
                    'Have a healthy snack',
                    'Do light stretching',
                    'Hydrate with water'
                ],
                'auto_execute': ['reduce_screen_brightness', 'pause_intensive_apps']
            })
            
        elif duration > 20:  # Moderate exhaustion
            self._execute_action({
                'type': ActionType.ENVIRONMENT_OPTIMIZATION,
                'priority': ActionPriority.HIGH,
                'optimizations': [
                    'increase_audio_clarity',
                    'reduce_background_noise',
                    'optimize_focus_settings'
                ],
                'message': "Optimizing environment to reduce cognitive load"
            })

    def _handle_stress(self, emotion_summary):
        """Handle detected stress with calming and clarity interventions"""
        stress_level = emotion_summary['behavioral_indicators'].get('stress_level', 0)
        duration = emotion_summary['duration']
        
        if stress_level > 0.6:  # High stress
            self._execute_action({
                'type': ActionType.AUDIO_ADJUSTMENT,
                'priority': ActionPriority.HIGH,
                'adjustment': 'stress_relief_profile',
                'effects': [
                    'enhance_clarity',
                    'reduce_harsh_frequencies',
                    'add_subtle_ambient'
                ],
                'message': "Activating stress-relief audio profile"
            })
            
            self._execute_action({
                'type': ActionType.NOTIFICATION,
                'priority': ActionPriority.MEDIUM,
                'title': "Stress Management Suggestion",
                'message': "Try the 4-7-8 breathing technique: Inhale for 4, hold for 7, exhale for 8",
                'type': 'breathing_exercise',
                'duration': 60
            })

    def _handle_concentration(self, emotion_summary):
        """Handle detected concentration by optimizing the environment"""
        attention_span = emotion_summary['behavioral_indicators'].get('attention_span', 0)
        duration = emotion_summary['duration']
        
        if duration > 10 and attention_span > 0.7:  # Good concentration
            self._execute_action({
                'type': ActionType.ENVIRONMENT_OPTIMIZATION,
                'priority': ActionPriority.HIGH,
                'optimizations': [
                    'enable_do_not_disturb',
                    'maximize_audio_focus',
                    'minimize_distractions'
                ],
                'message': "Concentration detected - Optimizing environment for deep focus"
            })
            
            self._execute_action({
                'type': ActionType.GAMING_ENHANCEMENT,
                'priority': ActionPriority.HIGH,
                'enhancements': [
                    'boost_competitive_audio',
                    'enhance_spatial_awareness',
                    'optimize_response_clarity'
                ],
                'message': "Enhancing gaming performance for concentrated play"
            })

    def _handle_confusion(self, emotion_summary):
        """Handle detected confusion with clarity and guidance"""
        confusion_level = emotion_summary['behavioral_indicators'].get('confusion_level', 0)
        
        if confusion_level > 0.5:
            self._execute_action({
                'type': ActionType.AUDIO_ADJUSTMENT,
                'priority': ActionPriority.MEDIUM,
                'adjustment': 'clarity_enhancement',
                'effects': [
                    'simplify_audio_mix',
                    'enhance_important_frequencies',
                    'reduce_audio_complexity'
                ],
                'message': "Simplifying audio for better clarity"
            })
            
            self._execute_action({
                'type': ActionType.NOTIFICATION,
                'priority': ActionPriority.LOW,
                'title': "Clarity Assistant",
                'message': "Take a moment to reassess your current task. Break it into smaller steps.",
                'suggestions': [
                    'Review your current objective',
                    'Break the task into smaller parts',
                    'Check if you need additional resources'
                ]
            })

    def _handle_happiness(self, emotion_summary):
        """Handle detected happiness by reinforcing positive conditions"""
        duration = emotion_summary['duration']
        confidence = emotion_summary['confidence']
        
        if confidence > 0.6:  # Strong happiness detection
            self._execute_action({
                'type': ActionType.ENVIRONMENT_OPTIMIZATION,
                'priority': ActionPriority.LOW,
                'optimizations': ['maintain_current_settings', 'boost_positive_audio'],
                'message': "😊 Happiness detected! Maintaining optimal conditions to keep you in the zone"
            })
            
            # Optional uplifting music if sustained happiness
            if duration > 15:
                self._execute_action({
                    'type': ActionType.MUSIC_CONTROL,
                    'priority': ActionPriority.LOW,
                    'action': 'play_uplifting',
                    'volume': 0.25,
                    'message': "🎵 Playing subtle uplifting background music"
                })

    def _handle_sadness(self, emotion_summary):
        """Handle detected sadness with supportive interventions"""
        duration = emotion_summary['duration']
        confidence = emotion_summary['confidence']
        behavioral_indicators = emotion_summary['behavioral_indicators']
        
        if confidence > 0.6:  # Strong sadness detection
            # Gentle intervention for initial sadness
            if duration > 10:
                self._execute_action({
                    'type': ActionType.MUSIC_CONTROL,
                    'priority': ActionPriority.MEDIUM,
                    'action': 'play_comforting',
                    'volume': 0.3,
                    'message': "🎶 Playing gentle, comforting background audio"
                })
                
                self._execute_action({
                    'type': ActionType.NOTIFICATION,
                    'priority': ActionPriority.LOW,
                    'title': "🌟 Gentle Reminder",
                    'message': "Taking breaks and staying hydrated can help improve your mood. You're doing great!",
                    'auto_dismiss': 8000  # 8 seconds
                })
            
            # More active intervention for sustained sadness
            if duration > 60:  # 1 minute of sadness
                self._execute_action({
                    'type': ActionType.BREAK_SUGGESTION,
                    'priority': ActionPriority.MEDIUM,
                    'title': "💙 Wellness Break Suggestion",
                    'message': "Consider taking a few minutes to step outside, stretch, or do something you enjoy.",
                    'actions': [
                        'Take a 5-10 minute walk',
                        'Listen to your favorite music',
                        'Do some light stretching',
                        'Chat with a friend or colleague'
                    ]
                })

    def _handle_positive_state(self, emotion_summary):
        """Handle positive emotional states by maintaining optimal conditions"""
        # This method is kept for backward compatibility
        self._handle_happiness(emotion_summary)

    def _handle_behavioral_indicators(self, behavioral_indicators):
        """Handle specific behavioral patterns"""
        
        # High restlessness
        if behavioral_indicators.get('restlessness', 0) > 0.7:
            self._execute_action({
                'type': ActionType.BREAK_SUGGESTION,
                'priority': ActionPriority.MEDIUM,
                'title': "Movement Break",
                'message': "High restlessness detected. A quick movement break might help.",
                'duration': 120  # 2 minutes
            })
        
        # Poor attention span
        if behavioral_indicators.get('attention_span', 1.0) < 0.3:
            self._execute_action({
                'type': ActionType.ENVIRONMENT_OPTIMIZATION,
                'priority': ActionPriority.MEDIUM,
                'optimizations': ['reduce_distractions', 'enhance_focus_audio'],
                'message': "Attention optimization activated"
            })

    def _execute_action(self, action_config):
        """Execute a specific action with proper timing and user preferences"""
        try:
            action_type = action_config['type']
            
            # Check cooldown
            if not self._is_action_available(action_type):
                return False
                
            # Check user preferences
            if not self.enabled_actions.get(action_type, True):
                return False
                
            # Execute based on action type
            success = False
            
            if action_type == ActionType.AUDIO_ADJUSTMENT:
                success = self._execute_audio_adjustment(action_config)
                
            elif action_type == ActionType.BREAK_SUGGESTION:
                success = self._execute_break_suggestion(action_config)
                
            elif action_type == ActionType.MUSIC_CONTROL:
                success = self._execute_music_control(action_config)
                
            elif action_type == ActionType.ENVIRONMENT_OPTIMIZATION:
                success = self._execute_environment_optimization(action_config)
                
            elif action_type == ActionType.NOTIFICATION:
                success = self._execute_notification(action_config)
                
            elif action_type == ActionType.GAMING_ENHANCEMENT:
                success = self._execute_gaming_enhancement(action_config)
                
            # Record action
            if success:
                self._record_action(action_config)
                self.last_action_time[action_type] = time.time()
                
            return success
            
        except Exception as e:
            print(f"⚠️ Action execution error: {e}")
            return False

    def _execute_audio_adjustment(self, config):
        """Execute audio adjustments"""
        try:
            if self.audio_controller:
                adjustment = config.get('adjustment', 'none')
                
                if adjustment == 'reduce_intensity':
                    self.audio_controller.reduce_background_intensity(0.7)
                elif adjustment == 'stress_relief_profile':
                    self.audio_controller.apply_stress_relief_profile()
                elif adjustment == 'clarity_enhancement':
                    self.audio_controller.enhance_clarity()
                    
                message = config.get('message', 'Audio adjusted')
                if self.notification_callback:
                    self.notification_callback(f"🔊 {message}")
                    
                return True
        except Exception as e:
            print(f"Audio adjustment error: {e}")
        return False

    def _execute_break_suggestion(self, config):
        """Execute break suggestions with UI integration"""
        try:
            title = config.get('title', 'Break Suggestion')
            message = config.get('message', 'Consider taking a break')
            actions = config.get('actions', [])
            
            if self.notification_callback:
                full_message = f"{message}\n\nSuggested actions:\n" + "\n".join(f"• {action}" for action in actions)
                self.notification_callback(f"⏰ {title}: {full_message}")
                
            # Auto-execute any specified actions
            auto_execute = config.get('auto_execute', [])
            for auto_action in auto_execute:
                self._execute_auto_action(auto_action)
                
            return True
        except Exception as e:
            print(f"Break suggestion error: {e}")
        return False

    def _execute_music_control(self, config):
        """Execute music and ambient sound control"""
        try:
            action = config.get('action', 'none')
            volume = config.get('volume', 0.5)
            
            if action == 'play_calming':
                # Play calming sounds (if available)
                self._play_ambient_sound('calming', volume)
            elif action == 'play_energizing':
                self._play_ambient_sound('energizing', volume)
            elif action == 'stop':
                self._stop_ambient_sound()
                
            message = config.get('message', 'Music control executed')
            if self.notification_callback:
                self.notification_callback(f"🎵 {message}")
                
            return True
        except Exception as e:
            print(f"Music control error: {e}")
        return False

    def _execute_environment_optimization(self, config):
        """Execute environment optimizations"""
        try:
            optimizations = config.get('optimizations', [])
            
            for optimization in optimizations:
                if optimization == 'enable_do_not_disturb':
                    self._enable_do_not_disturb()
                elif optimization == 'maximize_audio_focus':
                    if self.audio_controller:
                        self.audio_controller.maximize_focus_profile()
                elif optimization == 'reduce_distractions':
                    self._reduce_environmental_distractions()
                elif optimization == 'enhance_focus_audio':
                    if self.audio_controller:
                        self.audio_controller.enhance_focus_frequencies()
                        
            message = config.get('message', 'Environment optimized')
            if self.notification_callback:
                self.notification_callback(f"🏠 {message}")
                
            return True
        except Exception as e:
            print(f"Environment optimization error: {e}")
        return False

    def _execute_notification(self, config):
        """Execute user notifications and suggestions"""
        try:
            title = config.get('title', 'AURA Assistant')
            message = config.get('message', '')
            suggestions = config.get('suggestions', [])
            
            if suggestions:
                full_message = f"{message}\n\nSuggestions:\n" + "\n".join(f"• {suggestion}" for suggestion in suggestions)
            else:
                full_message = message
                
            if self.notification_callback:
                self.notification_callback(f"💡 {title}: {full_message}")
                
            return True
        except Exception as e:
            print(f"Notification error: {e}")
        return False

    def _execute_gaming_enhancement(self, config):
        """Execute gaming-specific enhancements"""
        try:
            enhancements = config.get('enhancements', [])
            
            for enhancement in enhancements:
                if enhancement == 'boost_competitive_audio':
                    if self.audio_controller:
                        self.audio_controller.apply_competitive_profile()
                elif enhancement == 'enhance_spatial_awareness':
                    if self.audio_controller:
                        self.audio_controller.enhance_spatial_audio()
                elif enhancement == 'optimize_response_clarity':
                    if self.audio_controller:
                        self.audio_controller.optimize_response_audio()
                        
            message = config.get('message', 'Gaming performance enhanced')
            if self.notification_callback:
                self.notification_callback(f"🎮 {message}")
                
            return True
        except Exception as e:
            print(f"Gaming enhancement error: {e}")
        return False

    def _is_action_available(self, action_type):
        """Check if action is available (not in cooldown)"""
        last_time = self.last_action_time.get(action_type, 0)
        cooldown = self.action_cooldowns.get(action_type, 60)
        return (time.time() - last_time) >= cooldown

    def _record_action(self, action_config):
        """Record action for learning and analysis"""
        self.action_history.append({
            'timestamp': time.time(),
            'type': action_config['type'].value,
            'priority': action_config.get('priority', ActionPriority.MEDIUM).value,
            'config': action_config
        })

    def _play_ambient_sound(self, sound_type, volume):
        """Play ambient sounds for mood regulation"""
        try:
            # Simple system beep for now - can be expanded with actual audio files
            if sound_type == 'calming':
                frequency = 440  # A note
                duration = 200   # milliseconds
            elif sound_type == 'energizing':
                frequency = 660  # E note
                duration = 150
            else:
                return
                
            # Play in a separate thread to avoid blocking
            threading.Thread(target=lambda: winsound.Beep(frequency, duration), daemon=True).start()
        except Exception as e:
            print(f"Ambient sound error: {e}")

    def _stop_ambient_sound(self):
        """Stop any playing ambient sounds"""
        # Implementation depends on audio system used
        pass

    def _enable_do_not_disturb(self):
        """Enable do not disturb mode"""
        self.active_optimizations['do_not_disturb'] = True

    def _reduce_environmental_distractions(self):
        """Reduce environmental distractions"""
        self.active_optimizations['minimal_distractions'] = True

    def _execute_auto_action(self, action_name):
        """Execute automatic actions"""
        if action_name == 'reduce_screen_brightness':
            # Could integrate with Windows brightness API
            pass
        elif action_name == 'pause_intensive_apps':
            # Could pause non-essential background apps
            pass

    def load_user_preferences(self):
        """Load user preferences from file"""
        try:
            if os.path.exists('aura_preferences.json'):
                with open('aura_preferences.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Preferences load error: {e}")
        
        return {
            'break_reminders': True,
            'audio_adjustments': True,
            'music_control': True,
            'notification_frequency': 'medium',
            'gaming_enhancements': True
        }

    def save_user_preferences(self):
        """Save user preferences to file"""
        try:
            with open('aura_preferences.json', 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
        except Exception as e:
            print(f"Preferences save error: {e}")

    def get_action_summary(self):
        """Get summary of recent actions and effectiveness"""
        recent_actions = list(self.action_history)[-10:]  # Last 10 actions
        
        action_types = {}
        for action in recent_actions:
            action_type = action['type']
            if action_type not in action_types:
                action_types[action_type] = 0
            action_types[action_type] += 1
            
        return {
            'recent_action_count': len(recent_actions),
            'action_distribution': action_types,
            'active_optimizations': self.active_optimizations.copy(),
            'session_actions': len(self.action_history)
        }

    def get_recommended_actions(self):
        """Get current recommended actions based on recent emotion analysis"""
        try:
            # Get recent actions from history
            recent_actions = list(self.action_history)[-5:]  # Last 5 actions
            
            if not recent_actions:
                return []
            
            # Extract action messages from recent actions
            recommendations = []
            for action in recent_actions:
                config = action.get('config', {})
                message = config.get('message', '')
                title = config.get('title', '')
                
                if message:
                    # Clean up message for display
                    clean_message = message.replace('🎵', '').replace('🔊', '').replace('💡', '').strip()
                    if clean_message and len(clean_message) > 10:  # Only meaningful messages
                        recommendations.append(clean_message)
                elif title:
                    clean_title = title.replace('🎵', '').replace('🔊', '').replace('💡', '').strip()
                    if clean_title and len(clean_title) > 10:
                        recommendations.append(clean_title)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_recommendations = []
            for rec in recommendations:
                if rec not in seen:
                    seen.add(rec)
                    unique_recommendations.append(rec)
            
            return unique_recommendations[:3]  # Return max 3 recommendations
            
        except Exception as e:
            print(f"Get recommendations error: {e}")
            return []
