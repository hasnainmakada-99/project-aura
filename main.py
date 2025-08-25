import sys
from PyQt6.QtWidgets import QApplication, QWidget

# --- Main Application Class ---
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Project AURA')
        self.setGeometry(300, 300, 800, 600) # x, y, width, height

        # Set a dark theme for the window
        self.setStyleSheet("background-color: #2B2B2B;")


# --- Run the Application ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())