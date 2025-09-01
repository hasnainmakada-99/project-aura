# ui_main_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QSlider, QCheckBox, QLineEdit, QFrame, 
                            QComboBox, QScrollArea, QSizePolicy)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QMediaPlayer

class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle('Project AURA')
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

        # (The top and middle sections are the same)
        # --- TOP SECTION: STATUS ---
        status_layout = QHBoxLayout()
        self.webcam_feed = QLabel('Webcam not found.')
        self.webcam_feed.setStyleSheet("background-color: #1A1A1A; color: #555; border: 1px solid #444; font-size: 16px; qproperty-alignment: 'AlignCenter';")
        self.webcam_feed.setFixedSize(240, 180)
        status_layout.addWidget(self.webcam_feed)
        
        status_text_layout = QVBoxLayout()
        self.status_label = QLabel('STATUS: INACTIVE')
        self.status_label.setFont(QFont('Segoe UI', 24, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #FF4757;")
        self.info_label = QLabel("AURA is running. Adjust sensitivity below.")
        self.info_label.setFont(QFont('Segoe UI', 10))
        self.info_label.setStyleSheet("color: #CCC;")
        self.info_label.setWordWrap(True)
        status_text_layout.addWidget(self.status_label)
        status_text_layout.addWidget(self.info_label)
        status_layout.addLayout(status_text_layout)
        
        main_layout.addLayout(status_layout)

        # --- EMOTION DETECTION SECTION ---
        emotion_frame = QFrame()
        emotion_frame.setStyleSheet("background-color: #2A2A2A; border: 1px solid #444; border-radius: 5px; padding: 10px;")
        emotion_layout = QVBoxLayout()
        
        emotion_title = QLabel('🧠 EMOTION & BEHAVIOR ANALYSIS')
        emotion_title.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        emotion_title.setStyleSheet("color: #90EE90; margin-bottom: 5px;")
        emotion_layout.addWidget(emotion_title)
        
        # Current emotion display
        self.emotion_status_label = QLabel('😶 Neutral | Analyzing your state...')
        self.emotion_status_label.setFont(QFont('Segoe UI', 10))
        self.emotion_status_label.setStyleSheet("color: #CCC; margin-bottom: 5px;")
        emotion_layout.addWidget(self.emotion_status_label)
        
        # Emotion actions display
        self.emotion_actions_label = QLabel('💡 No active recommendations')
        self.emotion_actions_label.setFont(QFont('Segoe UI', 9))
        self.emotion_actions_label.setStyleSheet("color: #888; font-style: italic;")
        self.emotion_actions_label.setWordWrap(True)
        emotion_layout.addWidget(self.emotion_actions_label)
        
        emotion_frame.setLayout(emotion_layout)
        main_layout.addWidget(emotion_frame)

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

        # --- BOTTOM SECTION: SETTINGS ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        main_layout.addWidget(line)

        settings_grid = QVBoxLayout()
        settings_grid.setContentsMargins(20, 10, 20, 20)
        
        # FIRST: Audio Device Management Section (Most Important)
        audio_device_frame = QFrame()
        audio_device_frame.setStyleSheet("""
            QFrame {
                background-color: #1a4f1a;
                border: 2px solid #90EE90;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """)
        audio_device_layout = QVBoxLayout(audio_device_frame)
        audio_device_layout.setContentsMargins(15, 15, 15, 15)
        
        # Audio device section header
        audio_device_header = QLabel("🎧 AUDIO DEVICE MANAGEMENT")
        audio_device_header.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        audio_device_header.setStyleSheet("color: #90EE90; margin-bottom: 8px; border: none; background: transparent;")
        audio_device_layout.addWidget(audio_device_header)
        
        # Output device selection
        output_device_layout = QHBoxLayout()
        output_label = QLabel("🔊 Output Device:")
        output_label.setFont(QFont('Segoe UI', 10))
        output_label.setStyleSheet("color: #CCC;")
        output_label.setFixedWidth(120)
        
        self.output_device_selector = QComboBox()
        self.output_device_selector.setFont(QFont('Segoe UI', 9))
        self.output_device_selector.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #2B2B2B;
                border: 2px solid #007BFF;
                border-radius: 5px;
                padding: 8px;
                min-width: 200px;
                font-size: 10px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #007BFF;
                border-radius: 3px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNEw2IDdMOSA0IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QComboBox QAbstractItemView {
                background-color: #2B2B2B;
                color: white;
                selection-background-color: #007BFF;
                border: 1px solid #007BFF;
            }
        """)
        
        self.refresh_devices_button = QPushButton("🔄 Refresh")
        self.refresh_devices_button.setFont(QFont('Segoe UI', 9))
        self.refresh_devices_button.setFixedWidth(80)
        self.refresh_devices_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 3px;
                padding: 5px;
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
        self.device_status_label.setFont(QFont('Segoe UI', 10))
        self.device_status_label.setStyleSheet("color: #FFF; font-style: italic; margin: 5px 0px; border: none; background: transparent;")
        self.device_status_label.setWordWrap(True)
        audio_device_layout.addWidget(self.device_status_label)
        
        # Auto-detect new devices checkbox
        auto_detect_layout = QHBoxLayout()
        self.auto_detect_devices_checkbox = QCheckBox("🔌 Auto-detect new devices (Recommended)")
        self.auto_detect_devices_checkbox.setFont(QFont('Segoe UI', 10))
        self.auto_detect_devices_checkbox.setStyleSheet("QCheckBox { color: #90EE90; spacing: 8px; border: none; background: transparent; }")
        self.auto_detect_devices_checkbox.setChecked(True)  # Default enabled
        auto_detect_layout.addWidget(self.auto_detect_devices_checkbox)
        auto_detect_layout.addStretch()
        audio_device_layout.addLayout(auto_detect_layout)
        
        # Add audio device frame to settings (HIGH PRIORITY)
        settings_grid.addWidget(audio_device_frame)
        
        # Add a separator
        audio_separator = QFrame()
        audio_separator.setFrameShape(QFrame.Shape.HLine)
        audio_separator.setFrameShadow(QFrame.Shadow.Sunken)
        audio_separator.setStyleSheet("background-color: #555; margin: 10px 0px;")
        settings_grid.addWidget(audio_separator)
        
        # Row 1 & 2: Enhanced Sliders with better labels
        slider_frame = QFrame()
        slider_frame.setStyleSheet("""
            QFrame {
                background-color: #353535;
                border-radius: 5px;
                padding: 10px;
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
        self.sensitivity_slider.setRange(1, 30)
        self.sensitivity_slider.setValue(15)
        self.sensitivity_slider.setFixedWidth(200)
        sensitivity_layout.addWidget(self.sensitivity_label)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        sensitivity_layout.addStretch()
        settings_grid.addLayout(sensitivity_layout)

        # NEW: Row 3 for Gaming Mode Controls (ANTI-CHEAT SAFE)
        
        # Anti-cheat safety warning
        safety_warning = QLabel("🛡️ ANTI-CHEAT SAFE MODE - Compatible with Vanguard/VAC")
        safety_warning.setFont(QFont('Segoe UI', 9, QFont.Weight.Bold))
        safety_warning.setStyleSheet("""
            QLabel {
                background-color: #2d5a27;
                color: #90EE90;
                padding: 6px;
                border-radius: 4px;
                margin-bottom: 5px;
            }
        """)
        settings_grid.addWidget(safety_warning)
        
        gaming_layout = QHBoxLayout()
        self.gaming_mode_checkbox = QCheckBox("🎮 Gaming Focus Mode (Safe)")
        self.gaming_mode_checkbox.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        self.gaming_mode_checkbox.setStyleSheet("QCheckBox { color: #90EE90; spacing: 10px; }")
        self.gaming_mode_checkbox.setToolTip("🛡️ 100% Anti-cheat safe!\nFocus-based background volume control only.")
        gaming_layout.addWidget(self.gaming_mode_checkbox)
        
        # Game selection dropdown
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
        gaming_layout.addWidget(self.game_selector)
        gaming_layout.addStretch()
        settings_grid.addLayout(gaming_layout)

        # NEW: Row 4 for Multi-Monitor Mode
        multimonitor_layout = QHBoxLayout()
        self.multimonitor_checkbox = QCheckBox("Multi-Monitor Mode (Use screen activity when face not detected)")
        self.multimonitor_checkbox.setFont(QFont('Segoe UI', 10))
        self.multimonitor_checkbox.setStyleSheet("QCheckBox { color: #CCC; spacing: 10px; }")
        self.multimonitor_checkbox.setChecked(True)  # Default enabled
        multimonitor_layout.addWidget(self.multimonitor_checkbox)
        multimonitor_layout.addStretch()
        settings_grid.addLayout(multimonitor_layout)

        # NEW: Row 5 for Mute List with improved styling
        mute_list_layout = QHBoxLayout()
        mute_label = QLabel("Apps to Control (e.g., spotify.exe,discord.exe,chrome.exe):")
        mute_label.setFont(QFont('Segoe UI', 10))
        mute_label.setStyleSheet("color: #CCC;")
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
        # Set default apps that are commonly running (gaming-focused)
        self.mute_list_input.setText("spotify.exe,discord.exe,chrome.exe,firefox.exe,vlc.exe,obs64.exe")
        mute_list_layout.addWidget(mute_label)
        mute_list_layout.addWidget(self.mute_list_input)
        settings_grid.addLayout(mute_list_layout)

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