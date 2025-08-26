# main.py
import sys
from PyQt6.QtWidgets import QApplication
from app_logic import AppLogic

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppLogic()
    ex.show()
    sys.exit(app.exec())