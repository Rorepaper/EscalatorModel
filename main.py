import sys
from PyQt6.QtWidgets import QApplication
from ModelWindow import ModelWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModelWindow()
    window.show()
    sys.exit(app.exec())
