from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

STEER_VISUAL_CLAMP_DEG = 30.0
STEER_SMOOTH_ALPHA = 0.2
STEER_REFRESH_MS = 40
ACKERMANN_FACTOR = 0.12


class KartTopViewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_angle_deg = 0.0
        self._display_angle_deg = 0.0
        self._compact = False
        self._ui_scale = 1.0

        self._timer = QTimer(self)
        self._timer.setInterval(STEER_REFRESH_MS)
        self._timer.timeout.connect(self._tick_animation)
        self._timer.start()

        self.setMinimumHeight(170)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        self.update()

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

        pad_x = int(8 * self._ui_scale)
        pad_y = int(6 * self._ui_scale)
        r = self.rect().adjusted(pad_x, pad_y, -pad_x, -pad_y)
        if r.width() <= 0 or r.height() <= 0:
            return

        center = r.center()

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
        vignette.setColorAt(0.0, QColor(30, 46, 68, 28))
        vignette.setColorAt(0.7, QColor(14, 22, 35, 18))
        vignette.setColorAt(1.0, QColor(5, 9, 15, 110))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(vignette)
        painter.drawRoundedRect(QRectF(r), 18, 18)

        self._draw_track(painter, r)

    def _draw_track(self, painter: QPainter, r: QRectF) -> None:
        track = QRectF(r.left() + r.width() * 0.12, r.top() + r.height() * 0.18, r.width() * 0.76, r.height() * 0.70)
        track_path = QPainterPath()
        track_path.moveTo(track.left() + track.width() * 0.08, track.bottom())
        track_path.lineTo(track.left() + track.width() * 0.24, track.top())
        track_path.lineTo(track.right() - track.width() * 0.24, track.top())
        track_path.lineTo(track.right() - track.width() * 0.08, track.bottom())
        track_path.closeSubpath()

        lane_grad = QLinearGradient(track.topLeft(), track.bottomLeft())
        lane_grad.setColorAt(0.0, QColor("#0b1119"))
        lane_grad.setColorAt(1.0, QColor("#1a2433"))
        painter.setPen(QPen(QColor("#26364d"), 1.0))
        painter.setBrush(lane_grad)
        painter.drawPath(track_path)

        if not self._compact:
            guide_color = QColor(165, 188, 214, 70)
            painter.setPen(QPen(guide_color, 1.0))
            painter.drawLine(
                QPointF(track.left() + track.width() * 0.30, track.top() + 3),
                QPointF(track.left() + track.width() * 0.16, track.bottom() - 6),
            )
            painter.drawLine(
                QPointF(track.right() - track.width() * 0.30, track.top() + 3),
                QPointF(track.right() - track.width() * 0.16, track.bottom() - 6),
            )

        glow = QRadialGradient(QPointF(track.center().x(), track.bottom() - 16), track.width() * 0.26)
        glow.setColorAt(0.0, QColor(112, 160, 220, 48))
        glow.setColorAt(1.0, QColor(112, 160, 220, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(track.center().x(), track.bottom() - 14), track.width() * 0.24, track.height() * 0.10)

        self._draw_kart(painter, track)

    def _draw_kart(self, painter: QPainter, track: QRectF) -> None:
        painter.save()
        center = QPointF(track.center().x(), track.center().y() + 5)
        scale = min(track.width() / 220.0, track.height() / 270.0)
        painter.translate(center)
        painter.scale(scale, scale)

        chassis = QPainterPath()
        chassis.moveTo(-20, -96)
        chassis.lineTo(20, -96)
        chassis.quadTo(28, -85, 26, -72)
        chassis.lineTo(22, 20)
        chassis.quadTo(18, 68, 34, 92)
        chassis.lineTo(-34, 92)
        chassis.quadTo(-18, 68, -22, 20)
        chassis.lineTo(-26, -72)
        chassis.quadTo(-28, -85, -20, -96)
        chassis.closeSubpath()

        body_grad = QLinearGradient(0, -96, 0, 92)
        body_grad.setColorAt(0.0, QColor("#22364f"))
        body_grad.setColorAt(0.55, QColor("#1a2b42"))
        body_grad.setColorAt(1.0, QColor("#111f31"))
        painter.setPen(QPen(QColor("#607fa7"), 1.4))
        painter.setBrush(body_grad)
        painter.drawPath(chassis)

        painter.setPen(QPen(QColor("#84a7d4"), 1.1))
        painter.drawRoundedRect(QRectF(-15, -102, 30, 14), 4, 4)

        seat = QPainterPath()
        seat.addRoundedRect(QRectF(-18, -18, 36, 60), 14, 14)
        seat_grad = QLinearGradient(0, -18, 0, 42)
        seat_grad.setColorAt(0.0, QColor("#2a3e59"))
        seat_grad.setColorAt(1.0, QColor("#17273b"))
        painter.setPen(QPen(QColor("#6f8fb6"), 1.0))
        painter.setBrush(seat_grad)
        painter.drawPath(seat)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#9ab8df"), 1.2))
        painter.drawEllipse(QPointF(0, -42), 10, 10)
        painter.drawLine(QPointF(-6, -42), QPointF(6, -42))

        painter.setPen(QPen(QColor("#465f7f"), 1.3))
        painter.drawLine(QPointF(-42, 48), QPointF(42, 48))

        angle = self._display_angle_deg
        inner = angle * (1.0 + ACKERMANN_FACTOR)
        outer = angle * (1.0 - ACKERMANN_FACTOR)
        left_front = inner if angle > 0 else outer
        right_front = outer if angle > 0 else inner

        self._draw_wheel(painter, QPointF(-48, -36), left_front, True)
        self._draw_wheel(painter, QPointF(48, -36), right_front, False)
        self._draw_wheel(painter, QPointF(-52, 48), 0.0, True)
        self._draw_wheel(painter, QPointF(52, 48), 0.0, False)

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
        painter.setPen(QPen(QColor("#4d6685"), 1.1))
        wheel_grad = QLinearGradient(tire.topLeft(), tire.bottomLeft())
        wheel_grad.setColorAt(0.0, QColor("#111b29"))
        wheel_grad.setColorAt(1.0, QColor("#090f18"))
        painter.setBrush(wheel_grad)
        painter.drawRoundedRect(tire, 4, 4)

        painter.setPen(QPen(QColor(128, 164, 209, 70), 1.0))
        painter.drawLine(QPointF(-5, -9), QPointF(5, -9))
        painter.restore()
