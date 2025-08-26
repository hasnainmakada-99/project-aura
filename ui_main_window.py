# ui_main_window.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QComboBox, QFrame, QSlider
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class UiMainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle('Project AURA')
        MainWindow.setGeometry(300, 300, 800, 600)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

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
        
        threshold_layout = QHBoxLayout()
        self.threshold_label = QLabel("Focus Threshold (0.25):")
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
        self.sensitivity_label = QLabel("Detection Stability (15 frames):")
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

        # RE-ADDED THE HELP LABEL
        self.help_label = QLabel("Tip: Lower 'Focus Threshold' if it's too hard to activate. Increase 'Detection Stability' if the status flickers too much.")
        self.help_label.setFont(QFont('Segoe UI', 8))
        self.help_label.setStyleSheet("color: #888;")
        self.help_label.setWordWrap(True)
        settings_grid.addWidget(self.help_label)


        main_layout.addLayout(settings_grid)

        MainWindow.setLayout(main_layout)
        MainWindow.setStyleSheet("background-color: #2B2B2B;")