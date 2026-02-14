"""AnalogGaugeWidget (vendorized).

This module is intended as the local vendor location for the
AnalogGaugeWidgetPyQt project (Apache-2.0).

NOTE: In this environment GitHub access was blocked (HTTP 403), so this file
contains a PyQt6-compatible gauge implementation used by the project wrapper
until the upstream file can be dropped in directly.
"""

from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QConicalGradient, QFont, QPainter, QPen, QPolygonF, QRadialGradient
from PyQt6.QtWidgets import QWidget


class AnalogGaugeWidget(QWidget):
    """PyQt6 analog gauge widget with a compact API for project integration."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.value_min = 0.0
        self.value_max = 100.0
        self.value = 0.0

        self.scala_main_count = 10
        self.scala_subdiv_count = 1

        self.scale_angle_start_value = 225.0
        self.scale_angle_size = 270.0
        self._clockwise = True

        self.gauge_color_outer = QColor("#5f6d77")
        self.gauge_color_inner = QColor("#1e2d3f")
        self.gauge_color_active_start = QColor("#00d7ff")
        self.gauge_color_active_end = QColor("#52f0ff")

        self.tick_major_color = QColor("#dbf4ff")
        self.tick_minor_color = QColor("#4f7394")
        self.label_color = QColor("#b3ebff")
        self.value_color = QColor("#efffff")
        self.unit_color = QColor("#9ed9ea")

        self.needle_color = QColor("#f6feff")
        self.needle_glow_color = QColor("#62f0ff")

        self.display_units = "km/h"
        self.title = "SPEED"

        self._ui_scale = 1.0
        self._compact = False
        self._base_min_size = 280
        self.setMinimumSize(self._base_min_size, self._base_min_size)

    @staticmethod
    def _arc16(degrees: float) -> int:
        return int(round(degrees * 16))

    def setMinValue(self, value: float) -> None:  # noqa: N802
        self.value_min = float(value)
        self.value = max(self.value_min, self.value)
        self.update()

    def setMaxValue(self, value: float) -> None:  # noqa: N802
        self.value_max = float(value)
        self.value = min(self.value_max, self.value)
        self.update()

    def setScaleStartAngle(self, degrees: float) -> None:  # noqa: N802
        self.scale_angle_start_value = float(degrees)
        self.update()

    def setTotalScaleAngleSize(self, degrees: float) -> None:  # noqa: N802
        self.scale_angle_size = float(degrees)
        self.update()

    def setScalaMainCount(self, count: int) -> None:  # noqa: N802
        self.scala_main_count = max(1, int(count))
        self.update()

    def setScalaSubDivCount(self, count: int) -> None:  # noqa: N802
        self.scala_subdiv_count = max(0, int(count))
        self.update()

    def setGaugeTheme(self, *_args, **_kwargs) -> None:  # noqa: N802
        self.update()

    def setDisplayUnits(self, unit: str) -> None:  # noqa: N802
        self.display_units = unit
        self.update()

    def setTitle(self, title: str) -> None:  # noqa: N802
        self.title = title
        self.update()

    def updateValue(self, value: float) -> None:  # noqa: N802
        self.value = max(self.value_min, min(self.value_max, float(value)))
        self.update()

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        min_size = int((228 if compact else self._base_min_size) * ui_scale)
        self.setMinimumSize(min_size, min_size)
        self.update()

    def _value_ratio(self) -> float:
        span = max(1e-6, self.value_max - self.value_min)
        return max(0.0, min(1.0, (self.value - self.value_min) / span))

    def _ratio_to_angle(self, ratio: float) -> float:
        clamped_ratio = max(0.0, min(1.0, ratio))
        direction = -1.0 if self._clockwise else 1.0
        return self.scale_angle_start_value + direction * clamped_ratio * self.scale_angle_size

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pad = int(12 * self._ui_scale)
        rect = self.rect().adjusted(pad, pad, -pad, -pad)
        center_f = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2

        start_deg = self.scale_angle_start_value
        span_sign = -self.scale_angle_size if self._clockwise else self.scale_angle_size

        outer_rect = QRectF(center_f.x() - radius * 0.84, center_f.y() - radius * 0.84, radius * 1.68, radius * 1.68)
        inner_ring_rect = QRectF(center_f.x() - radius * 0.60, center_f.y() - radius * 0.60, radius * 1.2, radius * 1.2)

        dial_bg = QRadialGradient(center_f, radius * 1.05)
        dial_bg.setColorAt(0.0, QColor("#101d2f"))
        dial_bg.setColorAt(0.72, QColor("#090f19"))
        dial_bg.setColorAt(1.0, QColor("#05080d"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dial_bg)
        painter.drawEllipse(QRectF(center_f.x() - radius * 0.90, center_f.y() - radius * 0.90, radius * 1.8, radius * 1.8))

        painter.setPen(QPen(self.gauge_color_outer, 6.5))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(span_sign))

        painter.setPen(QPen(self.gauge_color_inner, 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(span_sign))

        ratio = self._value_ratio()
        active_span = span_sign * ratio
        active_grad = QConicalGradient(center_f, start_deg)
        active_grad.setColorAt(0.0, self.gauge_color_active_start)
        active_grad.setColorAt(0.45, self.gauge_color_active_end)
        active_grad.setColorAt(1.0, QColor("#0f1f2c"))
        painter.setPen(QPen(active_grad, 11, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(active_span))

        painter.setPen(QPen(QColor("#36506f"), 2))
        painter.setBrush(QColor("#0d1522"))
        painter.drawEllipse(inner_ring_rect)

        minor_total = self.scala_main_count * (self.scala_subdiv_count + 1)
        for i in range(minor_total + 1):
            ratio_tick = i / max(1, minor_total)
            ang = math.radians(self._ratio_to_angle(ratio_tick))
            is_major = i % (self.scala_subdiv_count + 1) == 0
            r1 = radius * (0.72 if is_major else 0.75)
            r2 = radius * (0.82 if is_major else 0.80)
            p1 = QPointF(center_f.x() + math.cos(ang) * r1, center_f.y() - math.sin(ang) * r1)
            p2 = QPointF(center_f.x() + math.cos(ang) * r2, center_f.y() - math.sin(ang) * r2)
            painter.setPen(QPen(self.tick_major_color if is_major else self.tick_minor_color, 1.8 if is_major else 1.1))
            painter.drawLine(p1, p2)

        painter.setPen(self.label_color)
        painter.setFont(QFont("Bahnschrift", max(7, int((8 if self._compact else 10) * self._ui_scale)), QFont.Weight.Bold))
        for i in range(self.scala_main_count + 1):
            value = self.value_min + (self.value_max - self.value_min) * i / max(1, self.scala_main_count)
            ratio_tick = i / max(1, self.scala_main_count)
            ang = math.radians(self._ratio_to_angle(ratio_tick))
            rl = radius * 0.64
            label_point = QPointF(center_f.x() + math.cos(ang) * rl, center_f.y() - math.sin(ang) * rl)
            painter.drawText(QRectF(label_point.x() - 15, label_point.y() - 9, 30, 18), int(Qt.AlignmentFlag.AlignCenter), f"{int(value):d}")

        painter.setPen(QColor("#95edff"))
        painter.setFont(QFont("Bahnschrift", max(7, int((8 if self._compact else 10) * self._ui_scale)), QFont.Weight.DemiBold))
        painter.drawText(rect.adjusted(0, int(8 * self._ui_scale), 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, f"◉ {self.title}")

        value_text = f"{self.value:.0f}"
        painter.setPen(self.value_color)
        painter.setFont(QFont("Bahnschrift", max(20, int((30 if self._compact else 34) * self._ui_scale)), QFont.Weight.Bold))
        painter.drawText(rect.adjusted(0, int(-9 * self._ui_scale), 0, 0), Qt.AlignmentFlag.AlignCenter, value_text)

        painter.setPen(self.unit_color)
        painter.setFont(QFont("Bahnschrift", max(7, int((8 if self._compact else 10) * self._ui_scale)), QFont.Weight.Medium))
        painter.drawText(rect.adjusted(0, int((26 if self._compact else 30) * self._ui_scale), 0, 0), Qt.AlignmentFlag.AlignHCenter, self.display_units)

        pointer_deg = self._ratio_to_angle(ratio)
        pointer_rad = math.radians(pointer_deg)
        pointer_radius = radius * 0.80
        counter_radius = radius * 0.08
        axis_vec = QPointF(math.cos(pointer_rad), -math.sin(pointer_rad))
        normal_vec = QPointF(-axis_vec.y(), axis_vec.x())

        needle_tip = QPointF(center_f.x() + axis_vec.x() * pointer_radius, center_f.y() + axis_vec.y() * pointer_radius)
        needle_tail = QPointF(center_f.x() - axis_vec.x() * counter_radius, center_f.y() - axis_vec.y() * counter_radius)

        needle_glow = QColor(self.needle_glow_color)
        needle_glow.setAlpha(82)
        painter.setPen(QPen(needle_glow, 7.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(needle_tail, needle_tip)
        painter.setPen(QPen(self.needle_color, 3.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(needle_tail, needle_tip)

        tip_base = QPointF(center_f.x() + axis_vec.x() * (pointer_radius - radius * 0.06), center_f.y() + axis_vec.y() * (pointer_radius - radius * 0.06))
        tip_w = radius * 0.016
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#bfffff"))
        painter.drawPolygon(
            QPolygonF(
                [
                    needle_tip,
                    QPointF(tip_base.x() + normal_vec.x() * tip_w, tip_base.y() + normal_vec.y() * tip_w),
                    QPointF(tip_base.x() - normal_vec.x() * tip_w, tip_base.y() - normal_vec.y() * tip_w),
                ]
            )
        )

        painter.setBrush(QColor("#dbe8f6"))
        painter.drawEllipse(center_f, 5, 5)
