"""
Gaming Audio Intelligence Engine for Project AURA
Provides real-time audio analysis and game-specific sound enhancement
"""

import numpy as np
import librosa
import pyaudio
import threading
import time
from scipy import signal
from scipy.signal import butter, filtfilt
import json
import os

class GameAudioAnalyzer:
    def __init__(self):
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 2
        self.format = pyaudio.paFloat32
        
        # Audio processing
        self.audio = None
        self.stream = None
        self.is_analyzing = False
        self.analysis_thread = None
        
        # Game audio profiles
        self.game_profiles = {
            "valorant": {
                "footsteps": {"freq_range": [100, 2000], "boost": 3.0, "priority": "high"},
                "gunshots": {"freq_range": [1000, 8000], "boost": 1.5, "priority": "high"},
                "voice_comms": {"freq_range": [300, 3400], "boost": 2.0, "priority": "medium"},
                "ambient": {"freq_range": [50, 200], "boost": 0.3, "priority": "low"},
                "music": {"freq_range": [80, 15000], "boost": 0.2, "priority": "low"},
                "ui_sounds": {"freq_range": [2000, 8000], "boost": 0.5, "priority": "low"}
            },
            "cs2": {
                "footsteps": {"freq_range": [200, 2500], "boost": 2.8, "priority": "high"},
                "gunshots": {"freq_range": [1500, 9000], "boost": 1.8, "priority": "high"},
                "voice_comms": {"freq_range": [300, 3400], "boost": 2.0, "priority": "medium"},
                "ambient": {"freq_range": [50, 300], "boost": 0.4, "priority": "low"},
                "music": {"freq_range": [80, 15000], "boost": 0.1, "priority": "low"}
            },
            "apex": {
                "footsteps": {"freq_range": [150, 1800], "boost": 2.5, "priority": "high"},
                "gunshots": {"freq_range": [800, 7000], "boost": 1.6, "priority": "high"},
                "abilities": {"freq_range": [500, 4000], "boost": 1.2, "priority": "medium"},
                "voice_comms": {"freq_range": [300, 3400], "boost": 2.0, "priority": "medium"},
                "ambient": {"freq_range": [50, 250], "boost": 0.3, "priority": "low"}
            },
            "general_fps": {
                "footsteps": {"freq_range": [150, 2000], "boost": 2.5, "priority": "high"},
                "gunshots": {"freq_range": [1000, 8000], "boost": 1.5, "priority": "high"},
                "voice_comms": {"freq_range": [300, 3400], "boost": 2.0, "priority": "medium"},
                "ambient": {"freq_range": [50, 300], "boost": 0.4, "priority": "low"},
                "music": {"freq_range": [80, 15000], "boost": 0.2, "priority": "low"}
            }
        }
        
        # Current analysis state
        self.current_game = "valorant"
        self.audio_features = {}
        self.enhancement_active = False
        
        # Audio buffers for analysis
        self.audio_buffer = np.zeros(self.chunk_size * 4)  # 4 chunks buffer
        self.spectral_features = []
        
    def initialize_audio(self):
        """Initialize PyAudio for real-time processing"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find the default input device
            default_device = self.audio.get_default_input_device_info()
            print(f"Using audio device: {default_device['name']}")
            
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            
            return True
            
        except Exception as e:
            print(f"Error initializing audio: {e}")
            return False
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Real-time audio processing callback"""
        try:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            if len(audio_data) > 0:
                # Update audio buffer
                self.audio_buffer = np.roll(self.audio_buffer, -len(audio_data))
                self.audio_buffer[-len(audio_data):] = audio_data
                
                # Trigger analysis if we have enough data
                if len(self.audio_buffer) >= self.chunk_size:
                    self.analyze_audio_chunk(self.audio_buffer[-self.chunk_size:])
            
            return (in_data, pyaudio.paContinue)
            
        except Exception as e:
            print(f"Error in audio callback: {e}")
            return (in_data, pyaudio.paContinue)
    
    def analyze_audio_chunk(self, audio_chunk):
        """Analyze a chunk of audio for game-specific features"""
        try:
            if len(audio_chunk) < 512:  # Need minimum samples
                return
                
            # Compute spectral features
            fft = np.fft.fft(audio_chunk)
            magnitude = np.abs(fft)
            freqs = np.fft.fftfreq(len(audio_chunk), 1/self.sample_rate)
            
            # Only use positive frequencies
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]
            
            # Analyze game-specific frequency bands
            profile = self.game_profiles.get(self.current_game, self.game_profiles["general_fps"])
            
            detected_sounds = {}
            for sound_type, config in profile.items():
                freq_range = config["freq_range"]
                
                # Find energy in this frequency range
                mask = (positive_freqs >= freq_range[0]) & (positive_freqs <= freq_range[1])
                if np.any(mask):
                    energy = np.mean(positive_magnitude[mask])
                    detected_sounds[sound_type] = {
                        "energy": float(energy),
                        "config": config,
                        "detected": energy > self.get_detection_threshold(sound_type)
                    }
            
            # Update audio features
            self.audio_features = detected_sounds
            
            # Apply real-time enhancement if active
            if self.enhancement_active:
                self.apply_game_enhancement(detected_sounds)
                
        except Exception as e:
            print(f"Error analyzing audio chunk: {e}")
    
    def get_detection_threshold(self, sound_type):
        """Get detection threshold for different sound types"""
        thresholds = {
            "footsteps": 0.01,
            "gunshots": 0.05,
            "voice_comms": 0.02,
            "ambient": 0.005,
            "music": 0.01,
            "ui_sounds": 0.02,
            "abilities": 0.03
        }
        return thresholds.get(sound_type, 0.01)
    
    def apply_game_enhancement(self, detected_sounds):
        """Apply real-time audio enhancement based on detected sounds"""
        try:
            # This will be called by the main app to adjust system audio
            enhancement_data = {
                "timestamp": time.time(),
                "detected_sounds": detected_sounds,
                "recommended_adjustments": {}
            }
            
            # Calculate recommended volume adjustments
            for sound_type, data in detected_sounds.items():
                if data["detected"]:
                    config = data["config"]
                    enhancement_data["recommended_adjustments"][sound_type] = {
                        "boost": config["boost"],
                        "priority": config["priority"]
                    }
            
            # Store for main app to use
            self.current_enhancement_data = enhancement_data
            
        except Exception as e:
            print(f"Error applying enhancement: {e}")
    
    def get_footstep_detection_confidence(self):
        """Get confidence level for footstep detection"""
        if not self.audio_features or "footsteps" not in self.audio_features:
            return 0.0
            
        footstep_data = self.audio_features["footsteps"]
        if footstep_data["detected"]:
            # Calculate confidence based on energy level
            energy = footstep_data["energy"]
            threshold = self.get_detection_threshold("footsteps")
            confidence = min(1.0, energy / (threshold * 5))  # Normalize to 0-1
            return confidence
        
        return 0.0
    
    def get_current_audio_analysis(self):
        """Get current audio analysis results"""
        analysis = {
            "game": self.current_game,
            "timestamp": time.time(),
            "detected_sounds": {},
            "footstep_confidence": self.get_footstep_detection_confidence(),
            "enhancement_active": self.enhancement_active
        }
        
        for sound_type, data in self.audio_features.items():
            analysis["detected_sounds"][sound_type] = {
                "detected": data["detected"],
                "energy_level": data["energy"],
                "priority": data["config"]["priority"]
            }
        
        return analysis
    
    def set_game_profile(self, game_name):
        """Switch to a specific game profile"""
        if game_name in self.game_profiles:
            self.current_game = game_name
            print(f"Switched to {game_name} audio profile")
            return True
        else:
            print(f"Game profile '{game_name}' not found")
            return False
    
    def start_analysis(self):
        """Start real-time audio analysis"""
        if self.initialize_audio():
            self.is_analyzing = True
            self.stream.start_stream()
            print("Started real-time audio analysis")
            return True
        return False
    
    def stop_analysis(self):
        """Stop audio analysis"""
        self.is_analyzing = False
        self.enhancement_active = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.audio:
            self.audio.terminate()
        
        print("Stopped audio analysis")
    
    def enable_enhancement(self):
        """Enable real-time audio enhancement"""
        self.enhancement_active = True
        print(f"Enabled audio enhancement for {self.current_game}")
    
    def disable_enhancement(self):
        """Disable audio enhancement"""
        self.enhancement_active = False
        print("Disabled audio enhancement")

# Utility functions for frequency analysis
def create_bandpass_filter(lowcut, highcut, fs, order=4):
    """Create a bandpass filter"""
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Apply bandpass filter to audio data"""
    b, a = create_bandpass_filter(lowcut, highcut, fs, order=order)
    filtered_data = filtfilt(b, a, data)
    return filtered_data

def detect_transients(audio_data, threshold=0.1):
    """Detect transient sounds (like footsteps, gunshots)"""
    # Calculate onset strength
    onset_strength = librosa.onset.onset_strength(y=audio_data, sr=44100)
    
    # Find peaks that might be transients
    peaks = signal.find_peaks(onset_strength, height=threshold)[0]
    
    return len(peaks) > 0, peaks
