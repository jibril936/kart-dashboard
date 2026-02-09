import sys
from PyQt6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
w = QLabel("Kart Dashboard PyQt6 ✅")
w.setStyleSheet("font-size: 42px; padding: 40px;")
w.show()
sys.exit(app.exec())
