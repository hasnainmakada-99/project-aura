# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app_logic import AppLogic
from camera_detector import check_camera_requirements

def main():
    # Create QApplication first (required for camera dialogs)
    app = QApplication(sys.argv)
    app.setApplicationName("Project AURA")
    app.setApplicationVersion("2.0")
    
    print("🚀 Starting Project AURA - AI Gaming Companion")
    print("🛡️ Anti-cheat safe mode active")
    
    # Check camera requirements BEFORE starting the main app
    print("\n🎥 Checking camera requirements...")
    selected_camera = check_camera_requirements()
    
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