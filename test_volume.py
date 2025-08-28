#!/usr/bin/env python3
"""
Simple test script to check if volume control is working
"""

def test_volume_control():
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
        print("✓ pycaw imported successfully")
        
        sessions = AudioUtilities.GetAllSessions()
        print(f"✓ Found {len(sessions)} audio sessions")
        
        print("\nAvailable audio processes:")
        active_processes = []
        for session in sessions:
            if session.Process and session.Process.name():
                process_name = session.Process.name()
                active_processes.append(process_name)
                print(f"  - {process_name}")
        
        if not active_processes:
            print("❌ No active audio processes found")
            return False
            
        # Test volume control on first process
        if active_processes:
            test_process = active_processes[0]
            print(f"\n🔧 Testing volume control on: {test_process}")
            
            for session in sessions:
                if session.Process and session.Process.name() == test_process:
                    try:
                        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                        current_volume = volume.GetMasterVolume()
                        print(f"  Current volume: {current_volume:.2f}")
                        
                        # Test setting volume to 50%
                        volume.SetMasterVolume(0.5, None)
                        new_volume = volume.GetMasterVolume()
                        print(f"  Set to 0.5, new volume: {new_volume:.2f}")
                        
                        # Restore original volume
                        volume.SetMasterVolume(current_volume, None)
                        restored_volume = volume.GetMasterVolume()
                        print(f"  Restored volume: {restored_volume:.2f}")
                        
                        print("✓ Volume control test successful!")
                        return True
                        
                    except Exception as e:
                        print(f"❌ Error controlling volume: {e}")
                        return False
        
        return False
        
    except ImportError as e:
        print(f"❌ pycaw import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔊 Testing Volume Control System")
    print("=" * 40)
    success = test_volume_control()
    print("=" * 40)
    if success:
        print("🎉 Volume control is working correctly!")
    else:
        print("❌ Volume control test failed!")
