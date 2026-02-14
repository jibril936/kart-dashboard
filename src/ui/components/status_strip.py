from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget


class StatusStrip(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motor_temp = 0.0
        self._battery_temp = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedHeight(52)

    def update_temperatures(self, motor: float, battery: float) -> None:
        self._motor_temp = float(motor)
        self._battery_temp = float(battery)
        self.update()

    @staticmethod
    def _temp_color(value: float) -> QColor:
        if value >= 80.0:
            return QColor("#FF4B4B")
        if value >= 60.0:
            return QColor("#FF9B3D")
        return QColor("#DCE6F7")

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        left = f"🌡️ MOTEUR {self._motor_temp:.0f}°C"
        right = f"🔋 BATT {self._battery_temp:.0f}°C"

        p.setPen(self._temp_color(self._motor_temp))
        p.drawText(self.rect().adjusted(10, 0, -10, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, left)

        p.setPen(self._temp_color(self._battery_temp))
        p.drawText(self.rect().adjusted(10, 0, -10, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, right)
