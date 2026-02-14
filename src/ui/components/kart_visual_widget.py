from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class KartVisualWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._steering_angle_deg = 0.0
        self.setMinimumWidth(220)
        self.setContentsMargins(15, 15, 15, 15)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1a2634;
                border-radius: 12px;
                border: 1px solid #2c3e50;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            """
        )

    def set_steering_angle(self, angle_deg: float) -> None:
        self._steering_angle_deg = max(-45.0, min(45.0, float(angle_deg)))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        pad_x = 18
        pad_y = 18
        w = max(1, self.width() - (2 * pad_x))
        h = max(1, self.height() - (2 * pad_y))
        cx = pad_x + (w * 0.5)
        top_y = pad_y + (h * 0.16)
        bottom_y = pad_y + (h * 0.82)

        chassis_top_half = w * 0.16
        chassis_bottom_half = w * 0.30

        chassis_points = [
            QPointF(cx - chassis_top_half, top_y),
            QPointF(cx + chassis_top_half, top_y),
            QPointF(cx + chassis_bottom_half, bottom_y),
            QPointF(cx - chassis_bottom_half, bottom_y),
        ]

        chassis_pen = QPen(QColor("#00FFFF"), 3)
        painter.setPen(chassis_pen)
        painter.setBrush(QBrush(QColor(0, 255, 255, 40)))
        painter.drawPolygon(chassis_points)

        cockpit_w = w * 0.14
        cockpit_h = h * 0.1
        cockpit_rect = QRectF(cx - cockpit_w * 0.5, pad_y + (h * 0.44), cockpit_w, cockpit_h)
        painter.setPen(QPen(QColor("#8da7be"), 2))
        painter.setBrush(QColor(12, 20, 30, 190))
        painter.drawEllipse(cockpit_rect)

        rear_wheel_color = QColor("#707070")
        front_wheel_color = QColor("#00FFFF")

        rear_w = w * 0.09
        rear_h = h * 0.2
        rear_y = pad_y + (h * 0.58)
        rear_offset = w * 0.24

        rear_left_rect = QRectF(cx - rear_offset - rear_w * 0.5, rear_y, rear_w, rear_h)
        rear_right_rect = QRectF(cx + rear_offset - rear_w * 0.5, rear_y, rear_w, rear_h)

        painter.setPen(QPen(rear_wheel_color, 2))
        painter.setBrush(QColor(120, 120, 120, 80))
        painter.drawRect(rear_left_rect)
        painter.drawRect(rear_right_rect)

        front_w = w * 0.08
        front_h = h * 0.18
        front_center_y = pad_y + (h * 0.25)
        front_offset = w * 0.2

        painter.setPen(QPen(front_wheel_color, 2))
        painter.setBrush(QColor(0, 255, 255, 60))

        front_left_center = QPointF(cx - front_offset, front_center_y)
        front_right_center = QPointF(cx + front_offset, front_center_y)

        self._draw_rotated_wheel(painter, front_left_center, front_w, front_h, self._steering_angle_deg)
        self._draw_rotated_wheel(painter, front_right_center, front_w, front_h, self._steering_angle_deg)

        axle_pen = QPen(QColor("#77889a"), 2)
        painter.setPen(axle_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        rear_axle_y = rear_y + rear_h * 0.5
        painter.drawLine(QPointF(rear_left_rect.center().x(), rear_axle_y), QPointF(rear_right_rect.center().x(), rear_axle_y))
        painter.drawLine(QPointF(front_left_center.x(), front_center_y), QPointF(front_right_center.x(), front_center_y))

    def _draw_rotated_wheel(self, painter: QPainter, center: QPointF, width: float, height: float, angle: float) -> None:
        painter.save()
        painter.translate(center)
        painter.rotate(angle)
        painter.drawRect(QRectF(-width * 0.5, -height * 0.5, width, height))
        painter.restore()
