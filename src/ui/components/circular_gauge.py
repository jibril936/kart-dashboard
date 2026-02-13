from __future__ import annotations

import math
from collections.abc import Callable
from typing import Literal

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
        side: Literal["left", "right"] = "left",
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
        self.side: Literal["left", "right"] = side
        self._value = min_value
        self._compact = False
        self._ui_scale = 1.0
        self._base_min_size = 280
        self._gap_angle_deg = 82
        self.setMinimumSize(280, 280)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        min_size = int((228 if compact else self._base_min_size) * ui_scale)
        self.setMinimumSize(min_size, min_size)
        self.update()

    def _default_label_formatter(self, value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.1f}"

    def set_value(self, value: float) -> None:
        self._value = max(self.min_value, min(self.max_value, value))
        self.update()

    def _status_color(self) -> QColor:
        return QColor("#6d88ff")

    def _value_ratio(self, value: float) -> float:
        return max(0.0, min(1.0, (value - self.min_value) / max(1e-5, (self.max_value - self.min_value))))

    @staticmethod
    def _i(value: float | None) -> int:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return 0
        return int(round(value))

    @staticmethod
    def _arc16(degrees: float) -> int:
        return int(round(degrees * 16))

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pad = int(12 * self._ui_scale)
        rect = self.rect().adjusted(pad, pad, -pad, -pad)
        side_sign = 1 if self.side == "left" else -1
        center_f = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2

        gap_center_deg = 0 if self.side == "right" else 180
        gap_half = self._gap_angle_deg / 2.0
        start_deg = gap_center_deg + gap_half
        span_deg = 360 - self._gap_angle_deg
        inward_shift = radius * 0.08 * side_sign
        hub_center = QPointF(center_f.x() + inward_shift, center_f.y())

        outer_rect = QRectF(center_f.x() - radius * 0.82, center_f.y() - radius * 0.82, radius * 1.64, radius * 1.64)
        inner_ring_rect = QRectF(center_f.x() - radius * 0.56, center_f.y() - radius * 0.56, radius * 1.12, radius * 1.12)

        halo_color = self._status_color()
        halo_color.setAlpha(26)
        painter.setPen(QPen(halo_color, 30, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(-span_deg))

        painter.setPen(QPen(QColor("#1f2a3a"), 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(-span_deg))

        ratio = self._value_ratio(self._value)
        value_span = span_deg * ratio
        active_grad = QConicalGradient(center_f, start_deg)
        active_grad.setColorAt(0.0, QColor("#8b9cff"))
        active_grad.setColorAt(0.5, QColor("#6488ff"))
        active_grad.setColorAt(0.82, QColor("#5cb6ff"))
        active_grad.setColorAt(1.0, QColor("#46d3ff"))
        painter.setPen(QPen(QBrush(active_grad), 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(-value_span))

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
            hub_center.x() + math.cos(pointer_rad) * radius * 0.62,
            hub_center.y() - math.sin(pointer_rad) * radius * 0.62,
        )
        painter.setPen(QPen(QColor("#f4f9ff"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(hub_center, pointer_end)

        hub_glow = QColor("#7b95ff")
        hub_glow.setAlpha(80)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(hub_glow)
        painter.drawEllipse(hub_center, 12, 12)
        painter.setBrush(QColor("#dce7f5"))
        painter.drawEllipse(hub_center, 7, 7)
        painter.setBrush(QColor("#2e3f57"))
        painter.drawEllipse(hub_center, 3, 3)

        painter.setPen(QColor("#8ea5be"))
        painter.setFont(QFont("Segoe UI", max(7, int((8 if self._compact else 9) * self._ui_scale)), QFont.Weight.DemiBold))
        title_rect = rect.adjusted(0, int(8 * self._ui_scale), 0, 0)
        title_rect.translate(self._i(inward_shift), 0)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)

        value_text = f"{self._value:.0f}"
        painter.setPen(QColor("#f4f8ff"))
        painter.setFont(QFont("Segoe UI", max(20, int((28 if self._compact else 31) * self._ui_scale)), QFont.Weight.Bold))
        value_rect = rect.adjusted(0, int(-9 * self._ui_scale), 0, 0)
        value_rect.translate(self._i(inward_shift), 0)
        painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value_text)

        painter.setPen(QColor("#90a4bd"))
        painter.setFont(QFont("Segoe UI", max(7, int((8 if self._compact else 9) * self._ui_scale)), QFont.Weight.Medium))
        unit_y_offset = int((26 if self._compact else 30) * self._ui_scale)
        unit_rect = rect.adjusted(0, unit_y_offset, 0, 0)
        unit_rect.translate(self._i(inward_shift), 0)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignHCenter, self.unit)
