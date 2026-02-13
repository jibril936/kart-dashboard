from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

STEER_VISUAL_CLAMP_DEG = 30.0
STEER_SMOOTH_ALPHA = 0.2
STEER_REFRESH_MS = 40


class KartTopViewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_angle_deg = 0.0
        self._display_angle_deg = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(STEER_REFRESH_MS)
        self._timer.timeout.connect(self._tick_animation)
        self._timer.start()

        self.setMinimumHeight(170)

    def set_steer_angle(self, deg: float | None) -> None:
        value = 0.0 if deg is None else float(deg)
        self._target_angle_deg = max(-STEER_VISUAL_CLAMP_DEG, min(STEER_VISUAL_CLAMP_DEG, value))

    @property
    def display_angle_deg(self) -> float:
        return self._display_angle_deg

    def _tick_animation(self) -> None:
        delta = self._target_angle_deg - self._display_angle_deg
        if abs(delta) < 0.05:
            if self._display_angle_deg != self._target_angle_deg:
                self._display_angle_deg = self._target_angle_deg
                self.update()
            return

        self._display_angle_deg += delta * STEER_SMOOTH_ALPHA
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        r = self.rect().adjusted(8, 6, -8, -8)
        if r.width() <= 0 or r.height() <= 0:
            return

        center = r.center()

        # Layer 1: backplate, vignette, and dark glass.
        plate = QPainterPath()
        plate.addRoundedRect(QRectF(r), 18, 18)
        painter.setPen(QPen(QColor("#2a3648"), 1.0))
        bg_grad = QLinearGradient(r.left(), r.top(), r.left(), r.bottom())
        bg_grad.setColorAt(0.0, QColor("#101927"))
        bg_grad.setColorAt(0.65, QColor("#0d1522"))
        bg_grad.setColorAt(1.0, QColor("#0a111c"))
        painter.setBrush(bg_grad)
        painter.drawPath(plate)

        vignette = QRadialGradient(QPointF(center.x(), r.top() + r.height() * 0.45), r.width() * 0.7)
        vignette.setColorAt(0.0, QColor(38, 58, 90, 40))
        vignette.setColorAt(0.7, QColor(14, 22, 35, 20))
        vignette.setColorAt(1.0, QColor(5, 9, 15, 120))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(vignette)
        painter.drawRoundedRect(QRectF(r), 18, 18)

        # Layer 2: perspective platform.
        platform = QRectF(r.left() + r.width() * 0.10, r.top() + r.height() * 0.24, r.width() * 0.80, r.height() * 0.62)
        platform_path = QPainterPath()
        platform_path.moveTo(platform.left() + platform.width() * 0.05, platform.bottom())
        platform_path.lineTo(platform.left() + platform.width() * 0.22, platform.top())
        platform_path.lineTo(platform.right() - platform.width() * 0.22, platform.top())
        platform_path.lineTo(platform.right() - platform.width() * 0.05, platform.bottom())
        platform_path.closeSubpath()

        plat_grad = QLinearGradient(platform.topLeft(), platform.bottomLeft())
        plat_grad.setColorAt(0.0, QColor("#223959"))
        plat_grad.setColorAt(0.5, QColor("#172b47"))
        plat_grad.setColorAt(1.0, QColor("#0d1b30"))
        painter.setPen(QPen(QColor("#3b5270"), 1.1))
        painter.setBrush(plat_grad)
        painter.drawPath(platform_path)

        painter.setPen(QPen(QColor(95, 145, 212, 38), 1))
        painter.drawLine(
            QPointF(platform.left() + platform.width() * 0.27, platform.top() + 2),
            QPointF(platform.left() + platform.width() * 0.12, platform.bottom() - 4),
        )
        painter.drawLine(
            QPointF(platform.right() - platform.width() * 0.27, platform.top() + 2),
            QPointF(platform.right() - platform.width() * 0.12, platform.bottom() - 4),
        )

        # Layer 5: under-glow/shadow.
        glow = QRadialGradient(QPointF(center.x(), platform.bottom() - 10), platform.width() * 0.26)
        glow.setColorAt(0.0, QColor(101, 156, 255, 65))
        glow.setColorAt(1.0, QColor(101, 156, 255, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center.x(), platform.bottom() - 8), platform.width() * 0.28, platform.height() * 0.10)

        shadow = QRadialGradient(QPointF(center.x(), platform.center().y() + 18), platform.width() * 0.30)
        shadow.setColorAt(0.0, QColor(0, 0, 0, 100))
        shadow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(shadow)
        painter.drawEllipse(QPointF(center.x(), platform.center().y() + 20), platform.width() * 0.25, platform.height() * 0.15)

        # Layer 3 + 4: kart body and wheels.
        self._draw_kart(painter, platform)

    def _draw_kart(self, painter: QPainter, platform: QRectF) -> None:
        painter.save()
        center = QPointF(platform.center().x(), platform.center().y() + 4)
        scale = min(platform.width() / 210.0, platform.height() / 260.0)
        painter.translate(center)
        painter.scale(scale, scale)

        # Chassis capsule.
        chassis = QPainterPath()
        chassis.addRoundedRect(QRectF(-36, -88, 72, 166), 32, 32)
        painter.setPen(QPen(QColor("#607fa7"), 1.5))
        body_grad = QLinearGradient(0, -88, 0, 78)
        body_grad.setColorAt(0.0, QColor("#22364f"))
        body_grad.setColorAt(0.55, QColor("#1a2b42"))
        body_grad.setColorAt(1.0, QColor("#111f31"))
        painter.setBrush(body_grad)
        painter.drawPath(chassis)

        painter.setPen(QPen(QColor(132, 174, 227, 75), 1.2))
        painter.drawRoundedRect(QRectF(-22, -64, 44, 100), 20, 20)

        # Seat.
        seat = QPainterPath()
        seat.addRoundedRect(QRectF(-17, -28, 34, 56), 15, 15)
        painter.setPen(QPen(QColor("#6f8fb6"), 1.0))
        seat_grad = QLinearGradient(0, -28, 0, 28)
        seat_grad.setColorAt(0.0, QColor("#22364e"))
        seat_grad.setColorAt(1.0, QColor("#152539"))
        painter.setBrush(seat_grad)
        painter.drawPath(seat)

        # Steering wheel (cockpit item).
        painter.setPen(QPen(QColor("#84a7d4"), 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0, -44), 11, 8)
        painter.drawLine(QPointF(-7, -44), QPointF(7, -44))

        # Rear engine block.
        engine = QRectF(-21, 42, 42, 23)
        engine_grad = QLinearGradient(engine.topLeft(), engine.bottomLeft())
        engine_grad.setColorAt(0.0, QColor("#25364d"))
        engine_grad.setColorAt(1.0, QColor("#18283b"))
        painter.setPen(QPen(QColor("#6e90b9"), 1.0))
        painter.setBrush(engine_grad)
        painter.drawRoundedRect(engine, 8, 8)
        painter.setPen(QPen(QColor(148, 186, 235, 60), 1))
        painter.drawLine(QPointF(-15, 48), QPointF(15, 48))

        # Axles.
        painter.setPen(QPen(QColor("#3f587a"), 2.0))
        painter.drawLine(QPointF(-42, -36), QPointF(42, -36))
        painter.drawLine(QPointF(-42, 36), QPointF(42, 36))

        # Wheels.
        self._draw_wheel(painter, QPointF(-46, -36), self._display_angle_deg, True)
        self._draw_wheel(painter, QPointF(46, -36), self._display_angle_deg, False)
        self._draw_wheel(painter, QPointF(-46, 36), 0.0, True)
        self._draw_wheel(painter, QPointF(46, 36), 0.0, False)

        painter.restore()

    def _draw_wheel(self, painter: QPainter, center: QPointF, angle_deg: float, left: bool) -> None:
        painter.save()
        painter.translate(center)

        if angle_deg != 0.0:
            pivot_x = 5.0 if left else -5.0
            painter.translate(pivot_x, 0)
            painter.rotate(angle_deg)
            painter.translate(-pivot_x, 0)

        tire = QRectF(-8, -16, 16, 32)
        painter.setPen(QPen(QColor("#4d6685"), 1.1))
        wheel_grad = QLinearGradient(tire.topLeft(), tire.bottomLeft())
        wheel_grad.setColorAt(0.0, QColor("#111b29"))
        wheel_grad.setColorAt(1.0, QColor("#090f18"))
        painter.setBrush(wheel_grad)
        painter.drawRoundedRect(tire, 4, 4)

        painter.setPen(QPen(QColor(118, 154, 199, 70), 1.0))
        painter.drawRoundedRect(QRectF(-6, -13, 12, 5), 2, 2)
        painter.restore()
