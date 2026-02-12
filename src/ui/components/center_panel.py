from __future__ import annotations

from PyQt6.QtCore import QPointF, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget


class CenterPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._steering_angle_deg = 0.0
        self._display_angle_deg = 0.0
        self._mode: str | None = None
        self._gear: str | None = None
        self._has_steering = False
        self.setMinimumSize(320, 280)

        self._angle_anim = QPropertyAnimation(self, b"display_angle", self)
        self._angle_anim.setDuration(170)

    def _get_display_angle(self) -> float:
        return self._display_angle_deg

    def _set_display_angle(self, value: float) -> None:
        self._display_angle_deg = value
        self.update()

    display_angle = pyqtProperty(float, fget=_get_display_angle, fset=_set_display_angle)

    def set_state(self, steering_angle_deg: float | None, mode: str | None = None, gear: str | None = None) -> None:
        clamped = 0.0 if steering_angle_deg is None else max(-30.0, min(30.0, steering_angle_deg))
        self._steering_angle_deg = clamped
        self._mode = mode
        self._gear = gear
        self._has_steering = steering_angle_deg is not None
        self._angle_anim.stop()
        self._angle_anim.setStartValue(self._display_angle_deg)
        self._angle_anim.setEndValue(clamped)
        self._angle_anim.start()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        center = rect.center()

        painter.setPen(QPen(QColor("#273547"), 1))
        painter.setBrush(QColor("#0f1522"))
        painter.drawRoundedRect(rect, 18, 18)

        top_bar = rect.adjusted(26, 16, -26, -rect.height() + 56)
        painter.setPen(QPen(QColor("#32465f"), 1))
        painter.setBrush(QColor("#111d2f"))
        painter.drawRoundedRect(top_bar, 8, 8)

        if self._mode is not None:
            painter.setPen(QColor("#8ca5bf"))
            painter.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
            painter.drawText(top_bar.adjusted(12, 5, 0, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, "DRIVE MODE")
            painter.setPen(QColor("#d9e7f5"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(top_bar.adjusted(12, 0, 0, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._mode)

        if self._gear is not None:
            painter.setPen(QColor("#7ab6ff"))
            painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            painter.drawText(top_bar.adjusted(0, 0, -14, 0), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._gear)

        stage = rect.adjusted(24, 78, -24, -40)
        stage_path = QPainterPath()
        stage_path.moveTo(stage.left() + 20, stage.bottom())
        stage_path.lineTo(stage.left() + 55, stage.top() + 18)
        stage_path.lineTo(stage.right() - 55, stage.top() + 18)
        stage_path.lineTo(stage.right() - 20, stage.bottom())
        stage_path.closeSubpath()

        grad = QLinearGradient(stage.topLeft().toPointF(), stage.bottomLeft().toPointF())
        grad.setColorAt(0.0, QColor("#2e4fb0"))
        grad.setColorAt(0.5, QColor("#14366c"))
        grad.setColorAt(1.0, QColor("#0a1731"))
        painter.setPen(QPen(QColor("#3d63a7"), 1.2))
        painter.setBrush(grad)
        painter.drawPath(stage_path)

        halo_center = QPointF(center.x(), stage.center().y() + 36)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(129, 162, 255, 36))
        painter.drawEllipse(halo_center, 74, 22)
        painter.setBrush(QColor(194, 211, 255, 75))
        painter.drawEllipse(halo_center, 36, 10)

        painter.save()
        painter.translate(center.x(), stage.center().y() + 2)
        painter.rotate(self._display_angle_deg)
        painter.scale(1.05, 0.83)

        painter.setPen(QPen(QColor("#3f5f8b"), 1.4))
        painter.setBrush(QColor("#101a29"))
        painter.drawRoundedRect(-42, -72, 84, 142, 24, 24)
        painter.setBrush(QColor("#1d2f49"))
        painter.drawRoundedRect(-20, -44, 40, 24, 8, 8)
        painter.drawRoundedRect(-20, 12, 40, 24, 8, 8)

        painter.setBrush(QColor("#0c121e"))
        painter.drawRoundedRect(-52, -54, 10, 30, 3, 3)
        painter.drawRoundedRect(42, -54, 10, 30, 3, 3)
        painter.drawRoundedRect(-52, 24, 10, 30, 3, 3)
        painter.drawRoundedRect(42, 24, 10, 30, 3, 3)
        painter.restore()

        if self._has_steering:
            painter.setPen(QColor("#d8e6f6"))
            painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            painter.drawText(rect.adjusted(0, 0, 0, -8), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, f"{self._display_angle_deg:+.1f}°")
