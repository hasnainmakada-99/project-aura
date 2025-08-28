import cv2
import sys
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

class CameraDetector:
    def __init__(self):
        self.available_cameras = []
        self.selected_camera = None
        
    def detect_cameras(self):
        """Detect all available cameras on the system"""
        self.available_cameras = []
        
        # Test up to 10 possible camera indices
        for camera_index in range(10):
            try:
                cap = cv2.VideoCapture(camera_index)
                if cap.isOpened():
                    # Try to read a frame to verify camera is working
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Get camera info
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        
                        camera_info = {
                            'index': camera_index,
                            'width': width,
                            'height': height,
                            'fps': fps,
                            'name': f"Camera {camera_index} ({width}x{height})"
                        }
                        self.available_cameras.append(camera_info)
                        print(f"✅ Found camera {camera_index}: {width}x{height} @ {fps}fps")
                    cap.release()
                else:
                    # Camera index exists but can't be opened
                    pass
            except Exception as e:
                # Camera index doesn't exist or error occurred
                pass
                
        return len(self.available_cameras) > 0
    
    def get_best_camera(self):
        """Select the best available camera based on resolution"""
        if not self.available_cameras:
            return None
            
        # Sort by resolution (width * height) in descending order
        best_camera = max(self.available_cameras, 
                         key=lambda cam: cam['width'] * cam['height'])
        return best_camera
    
    def test_camera_access(self, camera_index=0):
        """Test if we can actually access and use the camera"""
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return False, "Camera could not be opened"
                
            # Try to read multiple frames to ensure stability
            for i in range(3):
                ret, frame = cap.read()
                if not ret or frame is None:
                    cap.release()
                    return False, "Camera failed to capture frames"
                    
            cap.release()
            return True, "Camera working properly"
            
        except Exception as e:
            return False, f"Camera test failed: {str(e)}"

class CameraRequirementDialog:
    def __init__(self, parent=None):
        self.parent = parent
        
    def show_no_camera_dialog(self):
        """Show dialog when no camera is detected"""
        msg = QMessageBox()
        msg.setWindowTitle("🎥 Camera Required - Project AURA")
        msg.setIcon(QMessageBox.Icon.Warning)
        
        # Make sure dialog appears on top and gets focus
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg.activateWindow()
        msg.raise_()
        
        msg.setText("📷 No Camera Detected!")
        msg.setInformativeText(
            "Project AURA requires a working camera for focus detection.\n\n"
            "🎯 Why we need your camera:\n"
            "• Face detection for focus tracking\n"
            "• Eye movement analysis\n"
            "• Attention level measurement\n"
            "• Gaming performance optimization\n\n"
            "🔒 Privacy: All processing is done locally on your device.\n"
            "No video data is transmitted or stored online.\n\n"
            "Please connect a camera and restart the application."
        )
        
        msg.setStandardButtons(
            QMessageBox.StandardButton.Retry | 
            QMessageBox.StandardButton.Close
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Retry)
        
        # Style the dialog
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QMessageBox QLabel {
                color: white;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #106ebe;
            }
            QMessageBox QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        return msg.exec()
    
    def show_camera_permission_dialog(self):
        """Show dialog when camera permission is needed"""
        msg = QMessageBox()
        msg.setWindowTitle("🔐 Camera Permission - Project AURA")
        msg.setIcon(QMessageBox.Icon.Information)
        
        # Make sure dialog appears on top and gets focus
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        msg.activateWindow()
        msg.raise_()
        
        msg.setText("📷 Camera Permission Required")
        msg.setInformativeText(
            "Project AURA needs permission to access your camera.\n\n"
            "🛡️ Privacy Protection:\n"
            "• All processing happens locally on your device\n"
            "• No video data is sent to the internet\n"
            "• No recordings are saved to disk\n"
            "• Camera is only used for real-time focus detection\n\n"
            "📋 How to grant permission:\n"
            "1. Check Windows Camera Privacy Settings\n"
            "2. Ensure camera access is enabled for desktop apps\n"
            "3. Close other applications using the camera\n"
            "4. Try a different camera if available\n\n"
            "Would you like to retry camera detection?"
        )
        
        msg.setStandardButtons(
            QMessageBox.StandardButton.Retry | 
            QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Retry)
        
        # Style the dialog
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                color: white;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QMessageBox QLabel {
                color: white;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #106ebe;
            }
            QMessageBox QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        return msg.exec()
    
    def show_multiple_cameras_dialog(self, cameras):
        """Show dialog to select from multiple cameras"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
        
        dialog = QDialog()
        dialog.setWindowTitle("📷 Select Camera - Project AURA")
        dialog.setModal(True)
        dialog.resize(400, 250)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🎥 Multiple Cameras Detected")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00FF7F; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Select the camera you'd like to use for focus detection:")
        desc.setStyleSheet("color: white; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # Camera selector
        camera_combo = QComboBox()
        for camera in cameras:
            camera_combo.addItem(camera['name'], camera['index'])
        camera_combo.setStyleSheet("""
            QComboBox {
                background-color: #3C3C3C;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        layout.addWidget(camera_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        test_button = QPushButton("🧪 Test Camera")
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        
        ok_button = QPushButton("✅ Use This Camera")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        
        button_layout.addWidget(test_button)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
        """)
        
        # Connect buttons
        selected_camera = None
        
        def test_camera():
            camera_index = camera_combo.currentData()
            detector = CameraDetector()
            success, message = detector.test_camera_access(camera_index)
            
            test_msg = QMessageBox()
            test_msg.setWindowTitle("🧪 Camera Test Result")
            if success:
                test_msg.setIcon(QMessageBox.Icon.Information)
                test_msg.setText("✅ Camera Test Successful!")
                test_msg.setInformativeText(f"Camera {camera_index} is working properly.")
            else:
                test_msg.setIcon(QMessageBox.Icon.Warning)
                test_msg.setText("❌ Camera Test Failed")
                test_msg.setInformativeText(f"Camera {camera_index} error: {message}")
            
            test_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b2b;
                    color: white;
                }
                QMessageBox QLabel {
                    color: white;
                }
                QMessageBox QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
            test_msg.exec()
        
        def accept_camera():
            nonlocal selected_camera
            selected_camera = camera_combo.currentData()
            dialog.accept()
        
        def cancel_selection():
            dialog.reject()
        
        test_button.clicked.connect(test_camera)
        ok_button.clicked.connect(accept_camera)
        cancel_button.clicked.connect(cancel_selection)
        
        result = dialog.exec()
        return selected_camera if result == QDialog.DialogCode.Accepted else None

def check_camera_requirements():
    """Main function to check camera requirements before starting the app"""
    print("🎥 Checking camera requirements...")
    
    detector = CameraDetector()
    dialog = CameraRequirementDialog()
    
    while True:
        # Detect available cameras
        has_cameras = detector.detect_cameras()
        
        if not has_cameras:
            print("❌ No cameras detected")
            result = dialog.show_no_camera_dialog()
            
            if result == QMessageBox.StandardButton.Retry:
                print("🔄 Retrying camera detection...")
                continue
            else:
                print("🚪 User chose to exit")
                return None
        
        # Test camera access
        if len(detector.available_cameras) == 1:
            # Single camera - test it
            camera = detector.available_cameras[0]
            success, message = detector.test_camera_access(camera['index'])
            
            if success:
                print(f"✅ Camera {camera['index']} is ready")
                return camera['index']
            else:
                print(f"❌ Camera access failed: {message}")
                result = dialog.show_camera_permission_dialog()
                
                if result == QMessageBox.StandardButton.Retry:
                    continue
                else:
                    return None
        
        else:
            # Multiple cameras - let user choose
            print(f"🎥 Found {len(detector.available_cameras)} cameras")
            selected_camera = dialog.show_multiple_cameras_dialog(detector.available_cameras)
            
            if selected_camera is not None:
                # Test the selected camera
                success, message = detector.test_camera_access(selected_camera)
                
                if success:
                    print(f"✅ Selected camera {selected_camera} is ready")
                    return selected_camera
                else:
                    print(f"❌ Selected camera failed: {message}")
                    result = dialog.show_camera_permission_dialog()
                    
                    if result == QMessageBox.StandardButton.Retry:
                        continue
                    else:
                        return None
            else:
                print("🚪 User cancelled camera selection")
                return None

if __name__ == "__main__":
    # Test the camera detection system
    app = QApplication(sys.argv)
    
    camera_index = check_camera_requirements()
    if camera_index is not None:
        print(f"🎉 Camera {camera_index} ready for Project AURA!")
    else:
        print("❌ Cannot start without camera access")
    
    sys.exit(0)
