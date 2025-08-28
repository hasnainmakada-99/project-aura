# ui_main_window.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLineEdit, QFrame, QSlider
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle('Project AURA')
        MainWindow.setGeometry(300, 300, 800, 650) # Made window slightly taller

        main_layout = QVBoxLayout()
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
        main_layout.addStretch(1)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        main_layout.addWidget(line)

        settings_grid = QVBoxLayout()
        settings_grid.setContentsMargins(20, 10, 20, 20)
        
        # Row 1 & 2: Enhanced Sliders with better labels
        threshold_layout = QHBoxLayout()
        self.threshold_label = QLabel("Eye Openness Threshold (0.25):")
        self.threshold_label.setFont(QFont('Segoe UI', 10))
        self.threshold_label.setStyleSheet("color: #CCC;")
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(15, 40)
        self.threshold_slider.setValue(25)
        self.threshold_slider.setFixedWidth(200)
        threshold_layout.addWidget(self.threshold_label)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addStretch()
        settings_grid.addLayout(threshold_layout)
        
        sensitivity_layout = QHBoxLayout()
        self.sensitivity_label = QLabel("Focus Sensitivity - High=More Sensitive (15):")
        self.sensitivity_label.setFont(QFont('Segoe UI', 10))
        self.sensitivity_label.setStyleSheet("color: #CCC;")
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
        from PyQt6.QtWidgets import QComboBox
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

        MainWindow.setLayout(main_layout)
        MainWindow.setStyleSheet("background-color: #2B2B2B;")