#!/usr/bin/env python3
"""
Test script to demonstrate the camera detection dialog
This version forces the "no camera detected" scenario to show the popup
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from camera_detector import CameraRequirementDialog

def simulate_no_camera_scenario():
    """Simulate the no camera detected scenario to test the popup"""
    print("🚀 Starting Project AURA - Camera Detection Demo")
    print("🎥 Simulating 'No Camera Detected' scenario...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Project AURA - Camera Test")
    
    # Create dialog
    dialog = CameraRequirementDialog()
    
    print("📱 Showing 'No Camera Detected' dialog...")
    print("💡 A system popup should appear now!")
    
    # Show the dialog
    result = dialog.show_no_camera_dialog()
    
    print(f"📝 Dialog result: {result}")
    
    if result == QMessageBox.StandardButton.Retry:
        print("✅ User clicked 'Retry'")
        print("🔄 In the real app, this would retry camera detection")
    elif result == QMessageBox.StandardButton.Close:
        print("❌ User clicked 'Close'")  
        print("🚪 In the real app, this would exit the application")
    else:
        print(f"🤔 User performed other action: {result}")
    
    print("\n🎯 Demo completed!")
    print("💡 This demonstrates how the popup appears when no camera is detected")

def simulate_permission_dialog():
    """Simulate the camera permission dialog"""
    print("\n🔐 Simulating 'Camera Permission' scenario...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    dialog = CameraRequirementDialog()
    
    print("📱 Showing 'Camera Permission' dialog...")
    
    result = dialog.show_camera_permission_dialog()
    
    print(f"📝 Permission dialog result: {result}")
    
    if result == QMessageBox.StandardButton.Retry:
        print("✅ User chose to retry camera access")
    else:
        print("❌ User cancelled camera access")

if __name__ == "__main__":
    print("🎥 PROJECT AURA - Camera Detection Dialog Demo")
    print("=" * 55)
    print("This demo shows the system popups that appear when:")
    print("1. No camera is detected")
    print("2. Camera permission issues occur")
    print("=" * 55)
    
    # Test 1: No Camera Dialog
    simulate_no_camera_scenario()
    
    # Test 2: Permission Dialog  
    simulate_permission_dialog()
    
    print("\n🏆 All dialogs demonstrated!")
    print("✅ These popups ensure users get proper guidance when camera issues occur")
    print("🎮 This provides a professional user experience for Project AURA!")
