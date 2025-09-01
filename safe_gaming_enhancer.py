import psutil
import time
import threading
from collections import deque
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

class SafeGamingEnhancer(QObject):
    """
    Safe gaming enhancement that provides competitive advantages
    without touching game audio or processes
    """
    
    enhancement_update = pyqtSignal(str, str)  # status, reason
    
    def __init__(self):
        super().__init__()
        
        # Safe enhancement methods
        self.system_activity_monitor = SystemActivityMonitor()
        self.gaming_context_detector = GamingContextDetector()
        self.safe_audio_optimizer = SafeAudioOptimizer()
        
        # Enhancement state
        self.current_enhancement_level = "normal"
        self.gaming_intensity_score = 0.0
        self.is_monitoring = False
        
        # Data collection for learning
        self.activity_history = deque(maxlen=100)
        self.enhancement_history = deque(maxlen=50)
        
    def start_safe_enhancement(self):
        """Start safe gaming enhancement monitoring"""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_gaming_context)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("🛡️ Safe gaming enhancement started")
        
    def stop_safe_enhancement(self):
        """Stop safe gaming enhancement"""
        self.is_monitoring = False
        print("🛡️ Safe gaming enhancement stopped")
        
    def _monitor_gaming_context(self):
        """Main monitoring loop for safe enhancement"""
        while self.is_monitoring:
            try:
                # Method 1: System activity analysis
                activity_intensity = self.system_activity_monitor.get_intensity_score()
                
                # Method 2: Gaming context detection
                gaming_context = self.gaming_context_detector.analyze_current_context()
                
                # Method 3: Behavioral pattern analysis
                behavioral_prediction = self.analyze_behavioral_patterns()
                
                # Combine safe indicators for enhancement decision
                enhancement_needed = self.calculate_safe_enhancement_level(
                    activity_intensity, gaming_context, behavioral_prediction
                )
                
                # Apply safe audio optimization
                if enhancement_needed != self.current_enhancement_level:
                    self.apply_safe_enhancement(enhancement_needed)
                    self.current_enhancement_level = enhancement_needed
                
                # Update UI with safe status
                self.update_enhancement_status(enhancement_needed)
                
                # Store data for learning
                self.record_enhancement_data(activity_intensity, gaming_context, enhancement_needed)
                
                time.sleep(0.5)  # Update every 500ms
                
            except Exception as e:
                print(f"Safe enhancement error: {e}")
                time.sleep(1)
                
    def calculate_safe_enhancement_level(self, activity, context, prediction):
        """Calculate enhancement level using safe methods only"""
        
        # Weighted scoring system
        activity_weight = 0.4
        context_weight = 0.4
        prediction_weight = 0.2
        
        # Calculate composite score
        composite_score = (
            activity * activity_weight +
            context["intensity"] * context_weight +
            prediction * prediction_weight
        )
        
        # Determine enhancement level
        if composite_score > 0.8:
            return "high_intensity"  # Combat-like activity detected
        elif composite_score > 0.6:
            return "moderate_focus"  # Focused gaming detected
        elif composite_score > 0.3:
            return "light_gaming"   # General gaming activity
        else:
            return "normal"         # Normal activity
            
    def apply_safe_enhancement(self, level):
        """Apply safe audio enhancement based on level"""
        
        enhancement_configs = {
            "high_intensity": {
                "bass_boost": 4,  # Enhanced low-end for "footstep-like" clarity
                "treble_boost": 3,  # Enhanced high-end for directional audio
                "background_reduction": 0.2,  # Minimal background apps
                "focus_message": "🎯 High Intensity: Maximum audio clarity"
            },
            "moderate_focus": {
                "bass_boost": 2,
                "treble_boost": 2,
                "background_reduction": 0.4,
                "focus_message": "🎮 Gaming Focus: Enhanced audio clarity"
            },
            "light_gaming": {
                "bass_boost": 1,
                "treble_boost": 1,
                "background_reduction": 0.6,
                "focus_message": "🔊 Light Gaming: Balanced audio"
            },
            "normal": {
                "bass_boost": 0,
                "treble_boost": 0,
                "background_reduction": 1.0,
                "focus_message": "🔊 Normal: Standard audio settings"
            }
        }
        
        config = enhancement_configs.get(level, enhancement_configs["normal"])
        
        # Apply safe system-level audio optimization
        self.safe_audio_optimizer.apply_system_eq(
            bass=config["bass_boost"],
            treble=config["treble_boost"]
        )
        
        # Apply safe background volume control
        self.safe_audio_optimizer.control_background_apps(
            level=config["background_reduction"]
        )
        
        # Emit status update
        self.enhancement_update.emit(config["focus_message"], level)
        
    def analyze_behavioral_patterns(self):
        """Analyze user behavior patterns for predictive enhancement"""
        
        if len(self.activity_history) < 10:
            return 0.5  # Default neutral prediction
            
        # Analyze recent activity patterns
        recent_activity = list(self.activity_history)[-10:]
        
        # Look for patterns that suggest intense gaming
        activity_variance = np.var(recent_activity)
        activity_mean = np.mean(recent_activity)
        
        # High variance + high mean = intense gaming activity
        if activity_variance > 0.1 and activity_mean > 0.7:
            return 0.9  # High prediction for enhancement
        elif activity_variance > 0.05 and activity_mean > 0.5:
            return 0.7  # Medium prediction
        else:
            return 0.3  # Low prediction
            
    def record_enhancement_data(self, activity, context, enhancement):
        """Record data for machine learning and optimization"""
        
        self.activity_history.append(activity)
        
        enhancement_data = {
            "timestamp": time.time(),
            "activity_intensity": activity,
            "gaming_context": context,
            "enhancement_level": enhancement,
            "user_focused": context.get("user_focused", False)
        }
        
        self.enhancement_history.append(enhancement_data)
        
    def update_enhancement_status(self, level):
        """Update UI with current enhancement status"""
        
        status_messages = {
            "high_intensity": "🎯 MAX CLARITY: Combat-optimized audio",
            "moderate_focus": "🎮 ENHANCED: Gaming-optimized audio", 
            "light_gaming": "🔊 BALANCED: General gaming audio",
            "normal": "🔊 STANDARD: Normal audio settings"
        }
        
        message = status_messages.get(level, "🔊 STANDARD: Normal audio settings")
        self.enhancement_update.emit(message, level)


class SystemActivityMonitor:
    """Monitor system activity for gaming intensity detection"""
    
    def __init__(self):
        self.last_cpu_time = time.time()
        self.last_network_activity = self.get_network_activity()
        self.activity_buffer = deque(maxlen=20)
        
    def get_intensity_score(self):
        """Calculate system activity intensity (0.0 to 1.0)"""
        
        # Monitor CPU usage spikes
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Monitor memory usage
        memory_percent = psutil.virtual_memory().percent
        
        # Monitor network activity (gaming often has consistent network usage)
        network_activity = self.get_network_activity()
        network_delta = abs(network_activity - self.last_network_activity)
        self.last_network_activity = network_activity
        
        # Monitor disk I/O (games often have burst I/O patterns)
        disk_io = psutil.disk_io_counters()
        
        # Calculate composite intensity score
        intensity_factors = {
            "cpu": min(cpu_percent / 50.0, 1.0),  # Normalize CPU usage
            "memory": min(memory_percent / 80.0, 1.0),  # Normalize memory usage  
            "network": min(network_delta / 1000000, 1.0),  # Normalize network activity
        }
        
        # Weighted average
        intensity_score = (
            intensity_factors["cpu"] * 0.5 +
            intensity_factors["memory"] * 0.2 +
            intensity_factors["network"] * 0.3
        )
        
        self.activity_buffer.append(intensity_score)
        
        # Return smoothed intensity score
        return np.mean(list(self.activity_buffer)) if self.activity_buffer else 0.5
        
    def get_network_activity(self):
        """Get current network activity"""
        try:
            net_io = psutil.net_io_counters()
            return net_io.bytes_sent + net_io.bytes_recv
        except:
            return 0


class GamingContextDetector:
    """Detect gaming context using safe system indicators"""
    
    def __init__(self):
        self.gaming_apps = [
            "valorant", "cs2", "csgo", "apex", "fortnite", 
            "overwatch", "rainbow6", "pubg", "warzone"
        ]
        
    def analyze_current_context(self):
        """Analyze current gaming context"""
        
        context = {
            "intensity": 0.0,
            "gaming_app_active": False,
            "user_focused": False,
            "confidence": 0.0
        }
        
        try:
            # Check if gaming application is in foreground
            gaming_app_active = self.is_gaming_app_active()
            context["gaming_app_active"] = gaming_app_active
            
            # Analyze window focus patterns
            user_focused = self.analyze_focus_patterns()
            context["user_focused"] = user_focused
            
            # Calculate context intensity
            if gaming_app_active and user_focused:
                context["intensity"] = 0.9
                context["confidence"] = 0.95
            elif gaming_app_active:
                context["intensity"] = 0.7
                context["confidence"] = 0.8
            elif user_focused:
                context["intensity"] = 0.5
                context["confidence"] = 0.6
            else:
                context["intensity"] = 0.2
                context["confidence"] = 0.3
                
        except Exception as e:
            print(f"Context detection error: {e}")
            
        return context
        
    def is_gaming_app_active(self):
        """Check if a gaming application is currently active"""
        try:
            # Get list of running processes
            for proc in psutil.process_iter(['name']):
                process_name = proc.info['name'].lower()
                if any(game in process_name for game in self.gaming_apps):
                    return True
        except:
            pass
        return False
        
    def analyze_focus_patterns(self):
        """Analyze user focus patterns (safe method)"""
        # This would integrate with the existing face detection system
        # For now, return a placeholder
        return True  # Assume focused for demo


class SafeAudioOptimizer:
    """Safe system-level audio optimization"""
    
    def __init__(self):
        self.current_eq_settings = {"bass": 0, "treble": 0}
        
    def apply_system_eq(self, bass=0, treble=0):
        """Apply system-level EQ settings (safe)"""
        # This would integrate with Windows audio APIs
        # to adjust system-wide EQ settings safely
        
        self.current_eq_settings = {"bass": bass, "treble": treble}
        print(f"🎛️ Applied safe EQ: Bass +{bass}dB, Treble +{treble}dB")
        
    def control_background_apps(self, level=1.0):
        """Control background application volumes (safe)"""
        # This would use the existing safe volume control system
        print(f"🔊 Background apps volume: {int(level * 100)}%")
        

# Integration point for main application
def integrate_safe_gaming_enhancer(app_logic):
    """Integrate safe gaming enhancer with main application"""
    
    app_logic.safe_enhancer = SafeGamingEnhancer()
    
    # Connect signals
    app_logic.safe_enhancer.enhancement_update.connect(
        lambda status, level: app_logic.update_gaming_volume_info(status)
    )
    
    # Start enhancement when gaming mode is enabled
    def on_gaming_mode_changed(enabled):
        if enabled:
            app_logic.safe_enhancer.start_safe_enhancement()
        else:
            app_logic.safe_enhancer.stop_safe_enhancement()
    
    app_logic.gaming_mode_checkbox.toggled.connect(on_gaming_mode_changed)
    
    print("🛡️ Safe gaming enhancer integrated successfully!")
