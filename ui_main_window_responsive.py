# ui_main_window_responsive.py - Fully Responsive UI for Project AURA
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSlider, QCheckBox, QLineEdit, QFrame, 
                            QComboBox, QScrollArea, QSizePolicy, QGridLayout)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QMediaPlayer

class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle('Project AURA - Audio Device Management')
        MainWindow.setMinimumSize(1000, 700)  # Minimum responsive size
        MainWindow.resize(1200, 850)  # Default size with more height
        
        # Create main widget
        main_widget = QWidget()
        MainWindow.setCentralWidget(main_widget)
        
        # Create scroll area for responsive design
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #2B2B2B;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #3C3C3C;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)
        
        # Create scrollable content widget
        scroll_content = QWidget()
        scroll_content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Main layout for scrollable content
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- TOP SECTION: STATUS ---
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(20, 10, 20, 10)

        self.webcam_feed = QLabel("📹 Camera Feed")
        self.webcam_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.webcam_feed.setStyleSheet("border: 2px solid #007BFF; background-color: #1a1a1a; color: #90EE90; font-size: 14px; border-radius: 5px;")
        self.webcam_feed.setFixedSize(240, 180)
        status_layout.addWidget(self.webcam_feed)

        status_info_layout = QVBoxLayout()
        self.status_title = QLabel("STATUS: ACTIVE")
        self.status_title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        self.status_title.setStyleSheet("color: #90EE90; margin-bottom: 10px;")
        status_info_layout.addWidget(self.status_title)

        self.info_label = QLabel("Y19°P-14°R-3° | C1.00✓ | AY | EY | Act:1.0 | Focus:1.00/0.55")
        self.info_label.setFont(QFont('Segoe UI', 10))
        self.info_label.setStyleSheet("color: #CCC;")
        status_info_layout.addWidget(self.info_label)

        self.emotion_frame = QFrame()
        self.emotion_frame.setStyleSheet("background-color: #3C3C3C; border-radius: 5px; padding: 10px; margin-top: 15px;")
        emotion_layout = QVBoxLayout(self.emotion_frame)
        
        emotion_header = QLabel("🧠 EMOTION & BEHAVIOR ANALYSIS")
        emotion_header.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        emotion_header.setStyleSheet("color: #FF69B4; margin-bottom: 5px;")
        emotion_layout.addWidget(emotion_header)
        
        self.emotion_display = QLabel("😊 Happy | 🔥 High | 18.9s")
        self.emotion_display.setFont(QFont('Segoe UI', 10))
        self.emotion_display.setStyleSheet("color: #FFD700; margin-bottom: 5px;")
        emotion_layout.addWidget(self.emotion_display)
        
        self.emotion_actions = QLabel("💡 Active: High restlessness detected. A quick movement break might help. | Attention optimization activated")
        self.emotion_actions.setFont(QFont('Segoe UI', 9))
        self.emotion_actions.setStyleSheet("color: #87CEEB;")
        self.emotion_actions.setWordWrap(True)
        emotion_layout.addWidget(self.emotion_actions)
        
        status_info_layout.addWidget(self.emotion_frame)
        status_layout.addWidget(QWidget())
        status_layout.addLayout(status_info_layout)
        main_layout.addLayout(status_layout)

        # --- MIDDLE SECTION: DEMO ---
        demo_layout = QHBoxLayout()
        demo_layout.setContentsMargins(20,10,20,10)
        self.demo_button = QPushButton('▶ Play Demo Sound')
        self.demo_button.setFont(QFont('Segoe UI', 14))
        self.demo_button.setMinimumHeight(60)
        self.demo_button.setStyleSheet("QPushButton { background-color: #007BFF; color: white; border-radius: 5px; } QPushButton:hover { background-color: #0056b3; }")
        demo_layout.addWidget(self.demo_button)

        self.aura_toggle = QCheckBox("AURA FOCUS MODE")
        self.aura_toggle.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        self.aura_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{ width: 90px; height: 60px; }}
            QCheckBox::indicator:unchecked {{ image: url(./assets/toggle_off.png); }}
            QCheckBox::indicator:checked {{ image: url(./assets/toggle_on.png); }}
            QCheckBox {{ color: white; spacing: 15px; }}
        """)
        demo_layout.addWidget(self.aura_toggle)
        main_layout.addLayout(demo_layout)

        # --- AUDIO DEVICE MANAGEMENT SECTION (PROMINENT) ---
        # FIRST: Audio Device Management Section (Most Important)
        audio_device_frame = QFrame()
        audio_device_frame.setStyleSheet("""
            QFrame {
                background-color: #1a4f1a;
                border: 3px solid #90EE90;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
            }
        """)
        audio_device_layout = QVBoxLayout(audio_device_frame)
        audio_device_layout.setContentsMargins(20, 20, 20, 20)
        
        # Audio device section header
        audio_device_header = QLabel("🎧 AUDIO DEVICE MANAGEMENT")
        audio_device_header.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        audio_device_header.setStyleSheet("color: #90EE90; margin-bottom: 15px; border: none; background: transparent;")
        audio_device_layout.addWidget(audio_device_header)
        
        # Output device selection
        output_device_layout = QHBoxLayout()
        output_label = QLabel("🔊 Output Device:")
        output_label.setFont(QFont('Segoe UI', 11))
        output_label.setStyleSheet("color: #FFF; border: none; background: transparent;")
        output_label.setFixedWidth(130)
        
        self.output_device_selector = QComboBox()
        self.output_device_selector.setFont(QFont('Segoe UI', 10))
        self.output_device_selector.setMinimumHeight(35)
        self.output_device_selector.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #2B2B2B;
                border: 2px solid #007BFF;
                border-radius: 5px;
                padding: 8px;
                min-width: 250px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #007BFF;
                border-radius: 3px;
                width: 25px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                color: white;
            }
            QComboBox QAbstractItemView {
                background-color: #2B2B2B;
                color: white;
                selection-background-color: #007BFF;
                border: 1px solid #007BFF;
            }
        """)
        
        self.refresh_devices_button = QPushButton("🔄 Refresh Devices")
        self.refresh_devices_button.setFont(QFont('Segoe UI', 10))
        self.refresh_devices_button.setMinimumHeight(35)
        self.refresh_devices_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        output_device_layout.addWidget(output_label)
        output_device_layout.addWidget(self.output_device_selector)
        output_device_layout.addWidget(self.refresh_devices_button)
        output_device_layout.addStretch()
        audio_device_layout.addLayout(output_device_layout)
        
        # Device status display
        self.device_status_label = QLabel("📊 Device Status: Scanning for audio devices...")
        self.device_status_label.setFont(QFont('Segoe UI', 11))
        self.device_status_label.setStyleSheet("color: #FFF; font-style: italic; margin: 10px 0px; border: none; background: transparent;")
        self.device_status_label.setWordWrap(True)
        audio_device_layout.addWidget(self.device_status_label)
        
        # Auto-detect new devices checkbox
        auto_detect_layout = QHBoxLayout()
        self.auto_detect_devices_checkbox = QCheckBox("🔌 Auto-detect new devices (Recommended)")
        self.auto_detect_devices_checkbox.setFont(QFont('Segoe UI', 11))
        self.auto_detect_devices_checkbox.setStyleSheet("QCheckBox { color: #90EE90; spacing: 10px; border: none; background: transparent; }")
        self.auto_detect_devices_checkbox.setChecked(True)  # Default enabled
        auto_detect_layout.addWidget(self.auto_detect_devices_checkbox)
        auto_detect_layout.addStretch()
        audio_device_layout.addLayout(auto_detect_layout)
        
        # Add audio device frame to main layout (HIGH PRIORITY)
        main_layout.addWidget(audio_device_frame)

        # --- SETTINGS SECTION ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        main_layout.addWidget(line)

        settings_grid = QVBoxLayout()
        settings_grid.setContentsMargins(20, 10, 20, 20)
        
        # Row 1 & 2: Enhanced Sliders with better labels
        slider_frame = QFrame()
        slider_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        slider_layout = QVBoxLayout(slider_frame)
        
        threshold_layout = QHBoxLayout()
        self.threshold_label = QLabel("Eye Openness Threshold (0.25):")
        self.threshold_label.setFont(QFont('Segoe UI', 10))
        self.threshold_label.setStyleSheet("color: #CCC; border: none; background: transparent;")
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(15, 40)
        self.threshold_slider.setValue(25)
        self.threshold_slider.setMinimumWidth(200)
        threshold_layout.addWidget(self.threshold_label)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addStretch()
        slider_layout.addLayout(threshold_layout)
        
        sensitivity_layout = QHBoxLayout()
        self.sensitivity_label = QLabel("Focus Sensitivity - High=More Sensitive (15):")
        self.sensitivity_label.setFont(QFont('Segoe UI', 10))
        self.sensitivity_label.setStyleSheet("color: #CCC; border: none; background: transparent;")
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(5, 30)
        self.sensitivity_slider.setValue(15)
        self.sensitivity_slider.setMinimumWidth(200)
        sensitivity_layout.addWidget(self.sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        sensitivity_layout.addStretch()
        slider_layout.addLayout(sensitivity_layout)
        
        settings_grid.addWidget(slider_frame)

        # ANTI-CHEAT INFO
        anticheat_frame = QFrame()
        anticheat_frame.setStyleSheet("""
            QFrame {
                background-color: #1a3d1a;
                border: 1px solid #90EE90;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
        """)
        anticheat_layout = QVBoxLayout(anticheat_frame)
        anticheat_label = QLabel("🛡️ ANTI-CHEAT SAFE MODE - Compatible with Vanguard/VAC")
        anticheat_label.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        anticheat_label.setStyleSheet("color: #90EE90; border: none; background: transparent;")
        anticheat_layout.addWidget(anticheat_label)
        settings_grid.addWidget(anticheat_frame)

        # Row 3: Gaming Mode
        gaming_frame = QFrame()
        gaming_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
        """)
        gaming_layout = QVBoxLayout(gaming_frame)
        
        gaming_checkbox_layout = QHBoxLayout()
        self.gaming_mode_checkbox = QCheckBox("🎮 Gaming Focus Mode (Safe)")
        self.gaming_mode_checkbox.setFont(QFont('Segoe UI', 10))
        self.gaming_mode_checkbox.setStyleSheet("QCheckBox { color: #90EE90; spacing: 10px; border: none; background: transparent; }")
        gaming_checkbox_layout.addWidget(self.gaming_mode_checkbox)
        gaming_checkbox_layout.addStretch()
        
        game_selector_layout = QHBoxLayout()
        game_label = QLabel("Game Profile:")
        game_label.setFont(QFont('Segoe UI', 10))
        game_label.setStyleSheet("color: #CCC; border: none; background: transparent;")
        self.game_selector = QComboBox()
        self.game_selector.addItems(["Valorant", "CS2", "Apex Legends", "General FPS"])
        self.game_selector.setFont(QFont('Segoe UI', 9))
        self.game_selector.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #3C3C3C;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        game_selector_layout.addWidget(game_label)
        game_selector_layout.addWidget(self.game_selector)
        game_selector_layout.addStretch()
        
        gaming_layout.addLayout(gaming_checkbox_layout)
        gaming_layout.addLayout(game_selector_layout)
        settings_grid.addWidget(gaming_frame)

        # Row 4: Multi-Monitor Mode
        multimonitor_layout = QHBoxLayout()
        self.multimonitor_checkbox = QCheckBox("Multi-Monitor Mode (Use screen activity when face not detected)")
        self.multimonitor_checkbox.setFont(QFont('Segoe UI', 10))
        self.multimonitor_checkbox.setStyleSheet("QCheckBox { color: #CCC; spacing: 10px; }")
        self.multimonitor_checkbox.setChecked(True)  # Default enabled
        multimonitor_layout.addWidget(self.multimonitor_checkbox)
        multimonitor_layout.addStretch()
        settings_grid.addLayout(multimonitor_layout)

        # Row 5: Mute List
        mute_frame = QFrame()
        mute_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
        """)
        mute_layout = QVBoxLayout(mute_frame)
        
        mute_label = QLabel("Apps to Control (e.g., spotify.exe,discord.exe,chrome.exe):")
        mute_label.setFont(QFont('Segoe UI', 10))
        mute_label.setStyleSheet("color: #CCC; border: none; background: transparent;")
        self.mute_list_input = QLineEdit()
        self.mute_list_input.setFont(QFont('Segoe UI', 10))
        self.mute_list_input.setStyleSheet("""
            QLineEdit { 
                color: white; 
                border: 1px solid #555; 
                border-radius: 3px; 
                padding: 5px; 
                background-color: #3C3C3C; 
            }
            QLineEdit:focus {
                border: 1px solid #007BFF;
            }
        """)
        self.mute_list_input.setPlaceholderText("Enter application names separated by commas...")
        self.mute_list_input.setText("spotify.exe,discord.exe,chrome.exe,firefox.exe,vlc.exe,obs64.exe")
        mute_layout.addWidget(mute_label)
        mute_layout.addWidget(self.mute_list_input)
        settings_grid.addWidget(mute_frame)

        main_layout.addLayout(settings_grid)

        # Set up the scroll area
        scroll_area.setWidget(scroll_content)
        
        # Create layout for main widget and add scroll area
        main_widget_layout = QVBoxLayout(main_widget)
        main_widget_layout.setContentsMargins(0, 0, 0, 0)
        main_widget_layout.addWidget(scroll_area)
        
        # Apply styling
        MainWindow.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: white;
            }
            QMainWindow {
                background-color: #2B2B2B;
            }
        """)
