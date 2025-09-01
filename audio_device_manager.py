# audio_device_manager.py
import sys
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

try:
    # Try basic pycaw imports that should work
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    PYCAW_AVAILABLE = True
    print("🎧 Audio Device Manager: pycaw loaded successfully!")
except ImportError as e:
    print(f"⚠️ Audio Device Manager: pycaw not available: {e}")
    PYCAW_AVAILABLE = False

@dataclass
class AudioDevice:
    """Represents an audio device with its properties"""
    id: str
    name: str
    is_default: bool
    is_active: bool
    device_type: str  # "render" (output) or "capture" (input)
    state: str  # "active", "disabled", "unplugged"
    volume: float = 0.0
    
    def __str__(self):
        status = "🔊" if self.is_active else "🔇"
        default = " (Default)" if self.is_default else ""
        return f"{status} {self.name}{default} - {self.device_type.title()}"

class AudioDeviceManager:
    """Manages audio device detection, selection, and control"""
    
    def __init__(self):
        self.available = PYCAW_AVAILABLE
        self.current_output_device = None
        self.current_input_device = None
        self.cached_devices = {}
        self.last_scan_time = 0
        self.scan_interval = 5.0  # Scan for devices every 5 seconds
        self.last_device_count = 0  # Track device count changes
        
        if self.available:
            self.refresh_devices()
    
    def refresh_devices(self) -> bool:
        """Refresh the list of available audio devices"""
        if not self.available:
            return False
            
        current_time = time.time()
        if current_time - self.last_scan_time < self.scan_interval:
            return True  # Skip refresh if too recent
            
        try:
            # Get basic device info from AudioUtilities
            new_devices = {
                'output': self._get_basic_output_devices(),
                'input': []  # Input devices require more complex APIs
            }
            
            # Only update and log if device count changed
            new_device_count = len(new_devices.get('output', []))
            if new_device_count != self.last_device_count:
                self.cached_devices = new_devices
                self.last_device_count = new_device_count
                print(f"🎧 Device change detected: {new_device_count} output devices")
            else:
                # Update cached devices silently
                self.cached_devices = new_devices
                
            self.last_scan_time = current_time
            return True
            
        except Exception as e:
            print(f"❌ Error refreshing audio devices: {e}")
            return False
    
    def _get_basic_output_devices(self) -> List[AudioDevice]:
        """Get basic output device information using AudioUtilities"""
        devices = []
        
        try:
            # Get all audio sessions to identify available output devices
            sessions = AudioUtilities.GetAllSessions()
            device_names = set()
            
            # Create a basic default device entry
            default_device = AudioDevice(
                id="default_output",
                name="Default Audio Output Device",
                is_default=True,
                is_active=True,
                device_type="output",
                state="active"
            )
            devices.append(default_device)
            
            # Try to get system device info
            try:
                import winreg
                # This is a simplified approach - in a full implementation
                # we would enumerate actual hardware devices
                system_device = AudioDevice(
                    id="system_output",
                    name="System Audio Output",
                    is_default=False,
                    is_active=True,
                    device_type="output",
                    state="active"
                )
                devices.append(system_device)
            except:
                pass
            
            # Only log on first detection or device count changes
            return devices
            
        except Exception as e:
            print(f"❌ Error getting output devices: {e}")
            return devices
    
    def get_output_devices(self) -> List[AudioDevice]:
        """Get all available output (render) devices"""
        self.refresh_devices()
        return self.cached_devices.get('output', [])
    
    def get_input_devices(self) -> List[AudioDevice]:
        """Get all available input (capture) devices"""
        self.refresh_devices()
        return self.cached_devices.get('input', [])
    
    def get_all_devices(self) -> List[AudioDevice]:
        """Get all available audio devices"""
        self.refresh_devices()
        all_devices = []
        all_devices.extend(self.cached_devices.get('output', []))
        all_devices.extend(self.cached_devices.get('input', []))
        return all_devices
    
    def get_default_output_device(self) -> Optional[AudioDevice]:
        """Get the current default output device"""
        output_devices = self.get_output_devices()
        for device in output_devices:
            if device.is_default:
                return device
        return None
    
    def get_default_input_device(self) -> Optional[AudioDevice]:
        """Get the current default input device"""
        input_devices = self.get_input_devices()
        for device in input_devices:
            if device.is_default:
                return device
        return None
    
    def control_device_volume(self, device_id: str, volume_level: float) -> bool:
        """Control volume for a specific device (simplified implementation)"""
        if not self.available:
            return False
            
        try:
            # Clamp volume between 0.0 and 1.0
            volume_level = max(0.0, min(1.0, volume_level))
            
            # Use AudioUtilities to control application volumes as a proxy
            sessions = AudioUtilities.GetAllSessions()
            controlled_count = 0
            
            for session in sessions:
                if session.Process:
                    try:
                        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                        volume.SetMasterVolume(volume_level, None)
                        controlled_count += 1
                    except:
                        continue
            
            if controlled_count > 0:
                print(f"🔊 Controlled {controlled_count} audio sessions for device {device_id}: {volume_level:.2f}")
                return True
            else:
                print(f"❌ No audio sessions found to control for device {device_id}")
                return False
            
        except Exception as e:
            print(f"❌ Error controlling device volume: {e}")
            return False
    
    def detect_device_changes(self) -> Tuple[List[AudioDevice], List[AudioDevice]]:
        """Detect newly connected and disconnected devices"""
        if not self.available:
            return [], []
            
        # For the simplified version, we'll just return empty lists
        # In a full implementation, this would compare previous and current device lists
        return [], []
    
    def get_device_info_string(self) -> str:
        """Get a formatted string with current device information"""
        if not self.available:
            return "❌ Audio device management not available"
        
        output_devices = self.get_output_devices()
        input_devices = self.get_input_devices()
        
        info_lines = [
            "🎧 === AUDIO DEVICE STATUS ===",
            f"📊 Output Devices: {len(output_devices)}",
            f"🎤 Input Devices: {len(input_devices)}"
        ]
        
        if output_devices:
            info_lines.append("\n🔊 OUTPUT DEVICES:")
            for device in output_devices:
                info_lines.append(f"  {device}")
        
        if input_devices:
            info_lines.append("\n🎤 INPUT DEVICES:")
            for device in input_devices:
                info_lines.append(f"  {device}")
        
        return "\n".join(info_lines)

# Global instance for easy access
audio_device_manager = AudioDeviceManager()

def get_audio_device_manager() -> AudioDeviceManager:
    """Get the global audio device manager instance"""
    return audio_device_manager
