from __future__ import annotations

import math
from collections.abc import Callable

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QConicalGradient, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class CircularGauge(QWidget):
    def __init__(
        self,
        title: str,
        unit: str,
        min_value: float,
        max_value: float,
        warning_value: float | None = None,
        critical_value: float | None = None,
        red_zone_start: float | None = None,
        major_tick_step: float | None = None,
        minor_ticks_per_major: int = 3,
        label_formatter: Callable[[float], str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.warning_value = warning_value
        self.critical_value = critical_value
        self.red_zone_start = red_zone_start
        self.major_tick_step = major_tick_step
        self.minor_ticks_per_major = max(0, minor_ticks_per_major)
        self.label_formatter = label_formatter or self._default_label_formatter
        self._value = min_value
        self._compact = False
        self._ui_scale = 1.0
        self.setMinimumSize(280, 280)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        self.update()

    def _default_label_formatter(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.1f}"

    def set_value(self, value: float) -> None:
        self._value = max(self.min_value, min(self.max_value, value))
        self.update()

    def _status_color(self) -> QColor:
        if self.critical_value is not None and self._value >= self.critical_value:
            return QColor("#ff5f56")
        if self.warning_value is not None and self._value >= self.warning_value:
            return QColor("#ffba49")
        return QColor("#6d88ff")

    def _value_ratio(self, value: float) -> float:
        return max(0.0, min(1.0, (value - self.min_value) / max(1e-5, (self.max_value - self.min_value))))

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pad = int(12 * self._ui_scale)
        rect = self.rect().adjusted(pad, pad, -pad, -pad)
        center_f = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2

        start_deg = 135
        span_deg = 270

        outer_rect = QRectF(center_f.x() - radius * 0.82, center_f.y() - radius * 0.82, radius * 1.64, radius * 1.64)
        inner_ring_rect = QRectF(center_f.x() - radius * 0.56, center_f.y() - radius * 0.56, radius * 1.12, radius * 1.12)

        halo_color = self._status_color()
        halo_color.setAlpha(26)
        painter.setPen(QPen(halo_color, 30, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, start_deg * 16, int(-span_deg * 16))

        painter.setPen(QPen(QColor("#1f2a3a"), 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, start_deg * 16, int(-span_deg * 16))

        if self.red_zone_start is not None:
            red_ratio = self._value_ratio(self.red_zone_start)
            red_start_deg = start_deg - span_deg * red_ratio
            red_span_deg = span_deg * (1 - red_ratio)
            painter.setPen(QPen(QColor("#ca3b4f"), 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(outer_rect, int(red_start_deg * 16), int(-red_span_deg * 16))

        ratio = self._value_ratio(self._value)
        value_span = span_deg * ratio
        active_grad = QConicalGradient(center_f, start_deg)
        active_grad.setColorAt(0.0, QColor("#8b9cff"))
        active_grad.setColorAt(0.5, QColor("#6488ff"))
        active_grad.setColorAt(0.82, QColor("#8c5bff"))
        active_grad.setColorAt(1.0, QColor("#ff6d64"))
        painter.setPen(QPen(QBrush(active_grad), 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, start_deg * 16, int(-value_span * 16))

        painter.setPen(QPen(QColor("#273649"), 2))
        painter.setBrush(QColor("#0f1623"))
        painter.drawEllipse(inner_ring_rect)

        painter.setPen(QPen(QColor("#304863"), 1))
        painter.setBrush(QColor("#111b2b"))
        painter.drawEllipse(QRectF(center_f.x() - radius * 0.49, center_f.y() - radius * 0.49, radius * 0.98, radius * 0.98))

        if self.major_tick_step is not None and self.major_tick_step > 0:
            total_major = int((self.max_value - self.min_value) / self.major_tick_step)
            major_count = max(1, total_major)
            minor_count = major_count * (self.minor_ticks_per_major + 1)

            for i in range(minor_count + 1):
                ratio_tick = i / minor_count
                ang = math.radians(start_deg - (span_deg * ratio_tick))
                is_major = i % (self.minor_ticks_per_major + 1) == 0
                r1 = radius * (0.72 if is_major else 0.75)
                r2 = radius * (0.82 if is_major else 0.80)
                p1 = QPointF(center_f.x() + math.cos(ang) * r1, center_f.y() - math.sin(ang) * r1)
                p2 = QPointF(center_f.x() + math.cos(ang) * r2, center_f.y() - math.sin(ang) * r2)
                tick_color = QColor("#bdcad8") if is_major else QColor("#4a5d73")
                painter.setPen(QPen(tick_color, 1.8 if is_major else 1.1))
                painter.drawLine(p1, p2)

            painter.setPen(QColor("#dbe8f5"))
            painter.setFont(QFont("Segoe UI", max(7, int((8 if self._compact else 9) * self._ui_scale)), QFont.Weight.DemiBold))
            for i in range(major_count + 1):
                value = self.min_value + self.major_tick_step * i
                ratio_tick = i / major_count
                ang = math.radians(start_deg - (span_deg * ratio_tick))
                rl = radius * 0.64
                label_point = QPointF(center_f.x() + math.cos(ang) * rl, center_f.y() - math.sin(ang) * rl)
                label_rect = QRectF(label_point.x() - 15, label_point.y() - 9, 30, 18)
                painter.drawText(label_rect, int(Qt.AlignmentFlag.AlignCenter), self.label_formatter(value))

        pointer_deg = start_deg - value_span
        pointer_rad = math.radians(pointer_deg)
        pointer_end = QPointF(
            center_f.x() + math.cos(pointer_rad) * radius * 0.62,
            center_f.y() - math.sin(pointer_rad) * radius * 0.62,
        )
        painter.setPen(QPen(QColor("#f4f9ff"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(center_f, pointer_end)

        hub_glow = QColor("#7b95ff")
        hub_glow.setAlpha(80)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(hub_glow)
        painter.drawEllipse(center_f, 12, 12)
        painter.setBrush(QColor("#dce7f5"))
        painter.drawEllipse(center_f, 7, 7)
        painter.setBrush(QColor("#2e3f57"))
        painter.drawEllipse(center_f, 3, 3)

        painter.setPen(QColor("#8ea5be"))
        painter.setFont(QFont("Segoe UI", max(7, int((8 if self._compact else 9) * self._ui_scale)), QFont.Weight.DemiBold))
        painter.drawText(rect.adjusted(0, int(8 * self._ui_scale), 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)

        value_text = f"{self._value:.0f}" if self.max_value >= 100 else f"{self._value:.1f}"
        painter.setPen(QColor("#f4f8ff"))
        painter.setFont(QFont("Segoe UI", max(20, int((28 if self._compact else 31) * self._ui_scale)), QFont.Weight.Bold))
        painter.drawText(rect.adjusted(0, int(-4 * self._ui_scale), 0, 0), Qt.AlignmentFlag.AlignCenter, value_text)

        painter.setPen(QColor("#90a4bd"))
        painter.setFont(QFont("Segoe UI", max(7, int((8 if self._compact else 9) * self._ui_scale)), QFont.Weight.Medium))
        unit_y_offset = int((34 if self._compact else 40) * self._ui_scale)
        painter.drawText(rect.adjusted(0, unit_y_offset, 0, 0), Qt.AlignmentFlag.AlignHCenter, self.unit)
