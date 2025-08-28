#!/usr/bin/env python3
"""
Camera Detection Test Script
Tests the camera detection dialog system
"""

import sys
from PyQt6.QtWidgets import QApplication
from camera_detector import CameraDetector, CameraRequirementDialog

def test_no_camera_dialog():
    """Test the no camera detected dialog"""
    print("🧪 Testing No Camera Dialog...")
    
    app = QApplication(sys.argv)
    dialog = CameraRequirementDialog()
    
    # Simulate no camera detected scenario
    result = dialog.show_no_camera_dialog()
    
    if result == dialog.show_no_camera_dialog.__class__.__module__:
        print("✅ Dialog appeared and user interacted")
    else:
        print(f"📝 Dialog result: {result}")
    
    return result

def test_camera_detection():
    """Test the full camera detection system"""
    print("🧪 Testing Full Camera Detection System...")
    
    app = QApplication(sys.argv)
    detector = CameraDetector()
    dialog = CameraRequirementDialog()
    
    # Force show the no camera dialog for testing
    print("🎥 Simulating no camera detected...")
    result = dialog.show_no_camera_dialog()
    print(f"📝 User action result: {result}")
    
    return result

def test_mock_camera():
    """Test with a mock camera for demonstration"""
    print("🧪 Testing Mock Camera Detection...")
    
    detector = CameraDetector()
    
    # Add a mock camera for testing
    mock_camera = {
        'index': 0,
        'width': 640,
        'height': 480,
        'fps': 30,
        'name': "Mock Camera 0 (640x480)"
    }
    detector.available_cameras = [mock_camera]
    
    print(f"✅ Mock camera added: {mock_camera['name']}")
    return mock_camera

if __name__ == "__main__":
    print("🚀 Camera Detection Dialog Test Suite")
    print("=" * 50)
    
    # Test 1: No Camera Dialog
    print("\n📋 Test 1: No Camera Detected Dialog")
    test_no_camera_dialog()
    
    # Test 2: Mock Camera
    print("\n📋 Test 2: Mock Camera Detection")
    mock_cam = test_mock_camera()
    
    print("\n✅ All tests completed!")
    print("💡 The dialogs should appear as system popups when no camera is detected.")
