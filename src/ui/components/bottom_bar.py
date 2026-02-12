from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._battery_v = 0.0
        self._battery_pct = 0.0
        self._power_ratio = 0.0
        self._regen_ratio = 0.0
        self._temp_c = 0.0
        self.setMinimumHeight(88)

    def set_values(
        self,
        battery_voltage: float,
        battery_percent: float,
        power_ratio: float,
        regen_ratio: float,
        motor_temp_c: float,
    ) -> None:
        self._battery_v = battery_voltage
        self._battery_pct = max(0.0, min(100.0, battery_percent))
        self._power_ratio = max(0.0, min(1.0, power_ratio))
        self._regen_ratio = max(0.0, min(1.0, regen_ratio))
        self._temp_c = motor_temp_c
        self.update()

    def _draw_horizontal_meter(self, painter: QPainter, x: int, y: int, w: int, h: int, ratio: float, label: str, color: QColor) -> None:
        painter.setPen(QPen(QColor("#2e3f54"), 1))
        painter.setBrush(QColor("#0f1724"))
        painter.drawRoundedRect(x, y, w, h, 3, 3)
        fill = int((w - 4) * ratio)
        if fill > 2:
            grad = QLinearGradient(x + 2, y, x + w - 2, y)
            grad.setColorAt(0, QColor("#2f4674"))
            grad.setColorAt(1, color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(x + 2, y + 2, fill, h - 4, 2, 2)

        painter.setPen(QColor("#8498af"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(x, y - 2, label)

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(8, 6, -8, -6)
        painter.setPen(QPen(QColor("#223145"), 1))
        painter.setBrush(QColor("#0b1320"))
        painter.drawRoundedRect(rect, 10, 10)

        left_w = int(rect.width() * 0.3)
        right_w = int(rect.width() * 0.18)
        center_w = rect.width() - left_w - right_w

        left = rect.adjusted(12, 8, -(rect.width() - left_w), -8)
        center = rect.adjusted(left_w + 6, 8, -(right_w + 8), -8)
        right = rect.adjusted(rect.width() - right_w + 6, 8, -12, -8)

        # Left: battery mini gauge
        painter.setPen(QPen(QColor("#8ea4bc"), 1.2))
        bx, by = left.left() + 4, left.top() + 12
        painter.drawRoundedRect(bx, by, 24, 14, 2, 2)
        painter.drawRect(bx + 24, by + 4, 3, 6)
        fill = int(20 * (self._battery_pct / 100.0))
        painter.fillRect(bx + 2, by + 2, fill, 10, QColor("#6a84ff"))
        painter.setPen(QColor("#dce8f5"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.drawText(left.adjusted(36, 4, 0, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, f"{self._battery_v:.1f}V")
        painter.setPen(QColor("#90a7bf"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(left.adjusted(36, 26, 0, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, f"{self._battery_pct:.0f}%")

        # Center: two thin horizontal bars
        meter_w = int(center_w * 0.42)
        meter_h = 10
        cx = center.left() + 18
        self._draw_horizontal_meter(painter, cx, center.top() + 20, meter_w, meter_h, self._power_ratio, "POWER", QColor("#6a89ff"))
        self._draw_horizontal_meter(painter, cx + meter_w + 22, center.top() + 20, meter_w, meter_h, self._regen_ratio, "REGEN", QColor("#5dbba9"))

        self._draw_horizontal_meter(
            painter,
            cx,
            center.top() + 44,
            meter_w * 2 + 22,
            meter_h,
            min(1.0, self._temp_c / 120.0),
            "TEMP",
            QColor("#ff8b5a"),
        )

        # Right: motor temperature
        painter.setPen(QColor("#dfeaf7"))
        painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        painter.drawText(right.adjusted(0, 10, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, f"{self._temp_c:.0f}°C")
        painter.setPen(QColor("#889db3"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(right.adjusted(0, 34, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, "MOTOR")
