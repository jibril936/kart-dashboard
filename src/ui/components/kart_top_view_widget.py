from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

STEER_VISUAL_CLAMP_DEG = 30.0
ACKERMANN_FACTOR = 0.12
STEER_ANIM_MIN_MS = 90
STEER_ANIM_MAX_MS = 220


class KartTopViewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_angle_deg = 0.0
        self._display_angle_deg = 0.0
        self._compact = False
        self._ui_scale = 1.0

        self._steer_anim = QPropertyAnimation(self, b"steerAngleDeg", self)
        self._steer_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._steer_anim.setDuration(STEER_ANIM_MIN_MS)

        self.setMinimumHeight(170)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        self.update()

    def set_steer_angle(self, deg: float | None) -> None:
        value = 0.0 if deg is None else float(deg)
        self._target_angle_deg = max(-STEER_VISUAL_CLAMP_DEG, min(STEER_VISUAL_CLAMP_DEG, value))
        delta = abs(self._target_angle_deg - self._display_angle_deg)
        if delta < 0.05:
            self._set_steer_angle_internal(self._target_angle_deg)
            return

        duration = int(min(STEER_ANIM_MAX_MS, max(STEER_ANIM_MIN_MS, 6.0 * delta + 85.0)))
        self._steer_anim.stop()
        self._steer_anim.setDuration(duration)
        self._steer_anim.setStartValue(self._display_angle_deg)
        self._steer_anim.setEndValue(self._target_angle_deg)
        self._steer_anim.start()

    @property
    def display_angle_deg(self) -> float:
        return self._display_angle_deg

    def _set_steer_angle_internal(self, value: float) -> None:
        self._display_angle_deg = float(value)
        self.update()

    @pyqtProperty(float)
    def steerAngleDeg(self) -> float:  # noqa: N802
        return self._display_angle_deg

    @steerAngleDeg.setter
    def steerAngleDeg(self, value: float) -> None:  # noqa: N802
        self._set_steer_angle_internal(value)

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self.rect().adjusted(int(8 * self._ui_scale), int(6 * self._ui_scale), -int(8 * self._ui_scale), -int(6 * self._ui_scale))
        if r.width() <= 0 or r.height() <= 0:
            return

        plate = QPainterPath()
        plate.addRoundedRect(QRectF(r), 16, 16)
        painter.setPen(QPen(QColor("#4f6378"), 1.2))
        shell = QLinearGradient(QPointF(r.topLeft()), QPointF(r.bottomRight()))
        shell.setColorAt(0.0, QColor("#0f1724"))
        shell.setColorAt(0.5, QColor("#0a111b"))
        shell.setColorAt(1.0, QColor("#060b11"))
        painter.setBrush(shell)
        painter.drawPath(plate)

        painter.setPen(QPen(QColor(86, 226, 248, 36), 1.0))
        step = 18
        for i in range(int(r.left()), int(r.right()), step):
            painter.drawLine(i, int(r.top()), i + int(r.height() * 0.25), int(r.bottom()))

        glow = QRadialGradient(QPointF(r.center().x(), r.center().y()), r.width() * 0.45)
        glow.setColorAt(0.0, QColor(0, 240, 255, 36))
        glow.setColorAt(1.0, QColor(0, 240, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(r.center()), r.width() * 0.36, r.height() * 0.36)

        self._draw_kart(painter, QRectF(r))

    def _draw_kart(self, painter: QPainter, zone: QRectF) -> None:
        painter.save()
        center = QPointF(zone.center().x(), zone.center().y() + 6)
        scale = min(zone.width() / 220.0, zone.height() / 260.0)
        painter.translate(center)
        painter.scale(scale, scale)

        chassis = QPainterPath()
        chassis.moveTo(-18, -98)
        chassis.lineTo(18, -98)
        chassis.quadTo(30, -82, 28, -58)
        chassis.lineTo(24, 26)
        chassis.quadTo(20, 72, 38, 96)
        chassis.lineTo(-38, 96)
        chassis.quadTo(-20, 72, -24, 26)
        chassis.lineTo(-28, -58)
        chassis.quadTo(-30, -82, -18, -98)
        chassis.closeSubpath()

        body = QLinearGradient(0, -98, 0, 96)
        body.setColorAt(0.0, QColor("#6ef1ff"))
        body.setColorAt(0.12, QColor("#2acfff"))
        body.setColorAt(0.35, QColor("#103d60"))
        body.setColorAt(1.0, QColor("#0b1827"))
        painter.setPen(QPen(QColor("#98f8ff"), 1.3))
        painter.setBrush(body)
        painter.drawPath(chassis)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(154, 243, 255, 165), 1.0))
        painter.drawRoundedRect(QRectF(-14, -16, 28, 54), 10, 10)
        painter.drawEllipse(QPointF(0, -44), 10, 10)
        painter.drawLine(QPointF(-6, -44), QPointF(6, -44))
        painter.drawEllipse(QPointF(0, 12), 8, 8)

        painter.setPen(QPen(QColor(103, 232, 255, 130), 1.1))
        painter.drawLine(QPointF(-42, 50), QPointF(42, 50))

        angle = self._display_angle_deg
        inner = angle * (1.0 + ACKERMANN_FACTOR)
        outer = angle * (1.0 - ACKERMANN_FACTOR)
        left_front = inner if angle > 0 else outer
        right_front = outer if angle > 0 else inner

        self._draw_wheel(painter, QPointF(-50, -34), left_front, True)
        self._draw_wheel(painter, QPointF(50, -34), right_front, False)
        self._draw_wheel(painter, QPointF(-54, 50), 0.0, True)
        self._draw_wheel(painter, QPointF(54, 50), 0.0, False)

        painter.restore()

    def _draw_wheel(self, painter: QPainter, center: QPointF, angle_deg: float, left: bool) -> None:
        painter.save()
        painter.translate(center)

        if angle_deg != 0.0:
            pivot_x = 5.0 if left else -5.0
            painter.translate(pivot_x, 0)
            painter.rotate(angle_deg)
            painter.translate(-pivot_x, 0)

        tire = QRectF(-8, -18, 16, 36)
        painter.setPen(QPen(QColor("#78e9ff"), 1.0))
        wheel_grad = QLinearGradient(tire.topLeft(), tire.bottomLeft())
        wheel_grad.setColorAt(0.0, QColor("#0d1b29"))
        wheel_grad.setColorAt(1.0, QColor("#04080e"))
        painter.setBrush(wheel_grad)
        painter.drawRoundedRect(tire, 4, 4)

        painter.setPen(QPen(QColor(170, 248, 255, 105), 1.0))
        painter.drawLine(QPointF(-4, -8), QPointF(4, -8))
        painter.drawLine(QPointF(-4, 0), QPointF(4, 0))
        painter.restore()
