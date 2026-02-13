from __future__ import annotations

from PyQt6.QtCore import QPointF, QPropertyAnimation, QRectF, Qt, pyqtProperty
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

        stage = rect.adjusted(24, 78, -24, -38)
        stage_path = QPainterPath()
        stage_path.moveTo(stage.left() + 18, stage.bottom())
        stage_path.lineTo(stage.left() + 54, stage.top() + 14)
        stage_path.lineTo(stage.right() - 54, stage.top() + 14)
        stage_path.lineTo(stage.right() - 18, stage.bottom())
        stage_path.closeSubpath()

        grad = QLinearGradient(stage.topLeft().toPointF(), stage.bottomLeft().toPointF())
        grad.setColorAt(0.0, QColor("#3456b8"))
        grad.setColorAt(0.45, QColor("#1c407f"))
        grad.setColorAt(1.0, QColor("#0a1d42"))
        painter.setPen(QPen(QColor("#3d63a7"), 1.2))
        painter.setBrush(grad)
        painter.drawPath(stage_path)

        halo_center = QPointF(center.x(), stage.center().y() + 30)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(129, 162, 255, 36))
        painter.drawEllipse(halo_center, 78, 22)
        painter.setBrush(QColor(194, 211, 255, 64))
        painter.drawEllipse(halo_center, 42, 12)

        kart_center = QPointF(center.x(), stage.center().y() + 4)
        self._draw_kart(painter, kart_center)

        if self._has_steering:
            painter.setPen(QColor("#d8e6f6"))
            painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            painter.drawText(rect.adjusted(0, 0, 0, -8), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, f"{self._display_angle_deg:+.1f}°")

    def _draw_kart(self, painter: QPainter, center: QPointF) -> None:
        painter.save()
        painter.translate(center)

        painter.setPen(QPen(QColor("#2f4f7e"), 1.5))
        painter.setBrush(QColor("#0f1a2b"))

        chassis = QPainterPath()
        chassis.moveTo(-18, -86)
        chassis.lineTo(18, -86)
        chassis.quadTo(32, -72, 32, -56)
        chassis.lineTo(32, 12)
        chassis.quadTo(26, 36, 14, 58)
        chassis.quadTo(4, 72, 0, 74)
        chassis.quadTo(-4, 72, -14, 58)
        chassis.quadTo(-26, 36, -32, 12)
        chassis.lineTo(-32, -56)
        chassis.quadTo(-32, -72, -18, -86)
        painter.drawPath(chassis)

        painter.setPen(QPen(QColor("#3e689d"), 1.2))
        painter.setBrush(QColor("#172841"))
        seat = QPainterPath()
        seat.moveTo(-16, -8)
        seat.quadTo(-24, -34, -8, -52)
        seat.quadTo(0, -58, 8, -52)
        seat.quadTo(24, -34, 16, -8)
        seat.quadTo(12, 12, 0, 18)
        seat.quadTo(-12, 12, -16, -8)
        painter.drawPath(seat)

        painter.setBrush(QColor("#11253e"))
        painter.drawRoundedRect(QRectF(-19, 22, 38, 30), 9, 9)
        painter.setBrush(QColor("#0b1728"))
        painter.drawRoundedRect(QRectF(-13, 28, 26, 18), 7, 7)

        painter.setBrush(QColor("#0f1724"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(-46, -62, 16, 38), 5, 5)
        painter.drawRoundedRect(QRectF(30, -62, 16, 38), 5, 5)
        painter.drawRoundedRect(QRectF(-46, 12, 16, 38), 5, 5)
        painter.drawRoundedRect(QRectF(30, 12, 16, 38), 5, 5)

        painter.setPen(QPen(QColor("#3c5b84"), 2.0))
        painter.drawLine(QPointF(-30, -43), QPointF(30, -43))
        painter.drawLine(QPointF(-30, 30), QPointF(30, 30))

        self._draw_steering_wheel(painter, QPointF(-38, -74), self._display_angle_deg)
        self._draw_steering_wheel(painter, QPointF(38, -74), self._display_angle_deg)

        painter.setPen(QPen(QColor("#4e76ad"), 1.8))
        painter.setBrush(QColor("#111f34"))
        painter.drawEllipse(QPointF(0, 0), 21, 15)
        painter.setPen(QPen(QColor("#41628f"), 1.2))
        painter.drawLine(QPointF(-13, 0), QPointF(13, 0))
        painter.drawLine(QPointF(0, -9), QPointF(0, 9))
        painter.restore()

    def _draw_steering_wheel(self, painter: QPainter, center: QPointF, angle_deg: float) -> None:
        painter.save()
        painter.translate(center)
        painter.rotate(angle_deg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#0c121e"))
        painter.drawRoundedRect(-6, -15, 12, 30, 4, 4)
        painter.setBrush(QColor("#1f334f"))
        painter.drawRoundedRect(-4, -10, 8, 20, 3, 3)
        painter.restore()
