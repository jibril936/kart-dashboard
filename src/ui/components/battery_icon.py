from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QPainter, QColor, QPen
from qtpy.QtCore import Qt

class BatteryIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percentage = 0
        self.setFixedSize(60, 30)

    def set_value(self, val):
        self.percentage = max(0, min(100, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.drawRoundedRect(2, 2, 50, 26, 3, 3)
        painter.drawRect(52, 10, 4, 10)
        fill = int((self.percentage / 100) * 46)
        color = QColor(0, 255, 127) if self.percentage > 20 else QColor(255, 50, 50)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(4, 4, fill, 22)