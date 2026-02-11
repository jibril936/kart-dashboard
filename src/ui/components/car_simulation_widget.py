from __future__ import annotations

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget


class CarSimulationWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._steering_angle_deg = 0.0
        self._mode = "DRIVE"
        self.setMinimumSize(280, 280)

    def set_state(self, steering_angle_deg: float, mode: str = "DRIVE") -> None:
        self._steering_angle_deg = max(-30.0, min(30.0, steering_angle_deg))
        self._mode = mode
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(14, 14, -14, -14)
        center = rect.center()

        painter.setPen(QPen(QColor("#223142"), 1))
        painter.setBrush(QColor("#101824"))
        painter.drawRoundedRect(rect, 20, 20)

        painter.save()
        painter.translate(center)
        painter.rotate(self._steering_angle_deg)

        body = QPainterPath()
        body.addRoundedRect(-50, -96, 100, 192, 32, 32)
        painter.setPen(QPen(QColor("#5e738d"), 2))
        painter.setBrush(QColor("#2b3d52"))
        painter.drawPath(body)

        painter.setBrush(QColor("#3a4d64"))
        painter.drawRoundedRect(-30, -65, 60, 36, 10, 10)
        painter.drawRoundedRect(-30, 22, 60, 36, 10, 10)

        painter.setBrush(QColor("#10151d"))
        wheel_w, wheel_h = 14, 38
        painter.drawRoundedRect(-64, -76, wheel_w, wheel_h, 5, 5)
        painter.drawRoundedRect(50, -76, wheel_w, wheel_h, 5, 5)
        painter.drawRoundedRect(-64, 40, wheel_w, wheel_h, 5, 5)
        painter.drawRoundedRect(50, 40, wheel_w, wheel_h, 5, 5)

        painter.setBrush(QColor("#6f859f"))
        painter.drawEllipse(QPointF(0, 0), 7, 7)
        painter.restore()

        painter.setPen(QColor("#8ea5be"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(rect.adjusted(0, 8, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, f"MODE • {self._mode}")

        painter.setPen(QColor("#dce8f6"))
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(rect.adjusted(0, 0, 0, 12), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, f"{self._steering_angle_deg:+.1f}°")
