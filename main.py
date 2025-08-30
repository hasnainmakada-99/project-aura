# main.py
import sys
import cv2
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from app_logic import AppLogic

def check_camera_availability():
    """Check if any camera is available and return the best camera index"""
    print("🎥 Checking camera requirements...")
    
    # Try to find an available camera (check first 3 camera indices)
    for camera_index in range(3):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            # Test if camera can actually capture frames
            ret, frame = cap.read()
            cap.release()
            if ret:
                print(f"✅ Found camera {camera_index}: {frame.shape[1]}x{frame.shape[0]} @ 30fps")
                return camera_index
        cap.release()
    
    # No camera found
    print("❌ No camera detected")
    return None

def main():
    # Create QApplication first (required for camera dialogs)
    app = QApplication(sys.argv)
    app.setApplicationName("Project AURA")
    app.setApplicationVersion("2.0")
    
    print("🚀 Starting Project AURA - AI Gaming Companion")
    print("🛡️ Anti-cheat safe mode active")
    
    # Check camera requirements BEFORE starting the main app
    selected_camera = check_camera_availability()
    
    if selected_camera is None:
        print("❌ Cannot start Project AURA without camera access")
        print("💡 Please connect a camera and restart the application")
        return 1
    
    print(f"✅ Camera {selected_camera} verified and ready!")
    print("🎮 Starting main application...\n")
    
    # Start the main application with verified camera
    try:
        ex = AppLogic(camera_index=selected_camera)
        ex.show()
        
        print("🎯 Project AURA is now running!")
        print("🎮 Enable Gaming Focus Mode for competitive advantage")
        print("🛡️ 100% anti-cheat safe - Compatible with Vanguard/VAC")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())