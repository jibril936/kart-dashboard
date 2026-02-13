from __future__ import annotations

import math
from collections.abc import Callable
from typing import Literal

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QConicalGradient, QFont, QLinearGradient, QPainter, QPen, QPolygonF, QRadialGradient
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
        self._start_angle_deg = 225.0
        self._sweep_angle_deg = 270.0
        # In this widget coordinate system, a negative delta rotates clockwise.
        self._direction = -1.0
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
        self._value = self._clamp_value(value)
        self.update()

    def _clamp_value(self, value: float) -> float:
        return max(self.min_value, min(self.max_value, value))

    def _status_color(self) -> QColor:
        return QColor("#4ee8ff")

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

    def _value_to_ratio(self, value: float) -> float:
        return self._value_ratio(self._clamp_value(value))

    def _ratio_to_angle(self, ratio: float) -> float:
        clamped_ratio = max(0.0, min(1.0, ratio))
        return self._start_angle_deg + self._direction * clamped_ratio * self._sweep_angle_deg

    def _value_to_angle(self, value: float) -> float:
        return self._ratio_to_angle(self._value_to_ratio(value))

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pad = int(12 * self._ui_scale)
        rect = self.rect().adjusted(pad, pad, -pad, -pad)
        side_sign = 1 if self.side == "left" else -1
        center_f = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2

        start_deg = self._start_angle_deg
        span_deg = self._sweep_angle_deg
        span_sign = self._direction * span_deg
        inward_shift = radius * 0.08 * side_sign
        hub_center = QPointF(center_f)

        outer_rect = QRectF(center_f.x() - radius * 0.84, center_f.y() - radius * 0.84, radius * 1.68, radius * 1.68)
        inner_ring_rect = QRectF(center_f.x() - radius * 0.60, center_f.y() - radius * 0.60, radius * 1.2, radius * 1.2)

        dial_bg = QRadialGradient(center_f, radius * 1.05)
        dial_bg.setColorAt(0.0, QColor("#101d2f"))
        dial_bg.setColorAt(0.72, QColor("#090f19"))
        dial_bg.setColorAt(1.0, QColor("#05080d"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dial_bg)
        painter.drawEllipse(QRectF(center_f.x() - radius * 0.90, center_f.y() - radius * 0.90, radius * 1.8, radius * 1.8))

        painter.setPen(QPen(QColor("#5f6d77"), 6.5))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(span_sign))

        for ratio_bolt in (0.08, 0.24, 0.42, 0.58, 0.76, 0.92):
            ang = math.radians(self._ratio_to_angle(ratio_bolt))
            bx = center_f.x() + math.cos(ang) * radius * 0.87
            by = center_f.y() - math.sin(ang) * radius * 0.87
            painter.setPen(QPen(QColor("#8e99a3"), 1.0))
            painter.setBrush(QColor("#272d33"))
            painter.drawEllipse(QPointF(bx, by), radius * 0.018, radius * 0.018)

        halo_color = self._status_color()
        halo_color.setAlpha(26)
        painter.setPen(QPen(halo_color, 36, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(span_sign))

        painter.setPen(QPen(QColor("#1e2d3f"), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(span_sign))

        clamped_value = self._clamp_value(self._value)
        ratio = self._value_to_ratio(clamped_value)
        value_span = span_sign * ratio
        active_grad = QConicalGradient(center_f, start_deg)
        active_grad.setColorAt(0.0, QColor("#2f74ff"))
        active_grad.setColorAt(0.55, QColor("#00d4ff"))
        active_grad.setColorAt(1.0, QColor("#f2fdff"))
        painter.setPen(QPen(QBrush(active_grad), 15, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(value_span))

        painter.setPen(QPen(QColor(164, 248, 255, 90), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(outer_rect, self._arc16(start_deg), self._arc16(value_span))

        glass = QLinearGradient(inner_ring_rect.topLeft(), inner_ring_rect.bottomLeft())
        glass.setColorAt(0.0, QColor("#18283d"))
        glass.setColorAt(1.0, QColor("#0d1522"))
        painter.setPen(QPen(QColor("#36506f"), 2))
        painter.setBrush(glass)
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
                ang = math.radians(self._ratio_to_angle(ratio_tick))
                is_major = i % (self.minor_ticks_per_major + 1) == 0
                r1 = radius * (0.72 if is_major else 0.75)
                r2 = radius * (0.82 if is_major else 0.80)
                p1 = QPointF(center_f.x() + math.cos(ang) * r1, center_f.y() - math.sin(ang) * r1)
                p2 = QPointF(center_f.x() + math.cos(ang) * r2, center_f.y() - math.sin(ang) * r2)
                tick_color = QColor("#dbf4ff") if is_major else QColor("#4f7394")
                painter.setPen(QPen(tick_color, 1.8 if is_major else 1.1))
                painter.drawLine(p1, p2)

            painter.setPen(QColor("#b3ebff"))
            painter.setFont(QFont("Bahnschrift", max(7, int((8 if self._compact else 10) * self._ui_scale)), QFont.Weight.Bold))
            for i in range(major_count + 1):
                value = self.min_value + self.major_tick_step * i
                ratio_tick = i / major_count
                ang = math.radians(self._ratio_to_angle(ratio_tick))
                rl = radius * 0.64
                label_point = QPointF(center_f.x() + math.cos(ang) * rl, center_f.y() - math.sin(ang) * rl)
                label_rect = QRectF(label_point.x() - 15, label_point.y() - 9, 30, 18)
                painter.drawText(label_rect, int(Qt.AlignmentFlag.AlignCenter), self.label_formatter(value))

        painter.setPen(QColor("#95edff"))
        painter.setFont(QFont("Bahnschrift", max(7, int((8 if self._compact else 10) * self._ui_scale)), QFont.Weight.DemiBold))
        title_rect = rect.adjusted(0, int(8 * self._ui_scale), 0, 0)
        title_rect.translate(self._i(inward_shift), 0)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, f"◉ {self.title}")

        value_text = f"{self._value:.0f}"
        painter.setPen(QColor(135, 236, 255, 90))
        painter.setFont(QFont("Bahnschrift", max(20, int((30 if self._compact else 34) * self._ui_scale)), QFont.Weight.Bold))
        glow_rect = rect.adjusted(2, int(-7 * self._ui_scale), 2, 0)
        glow_rect.translate(self._i(inward_shift), 0)
        painter.drawText(glow_rect, Qt.AlignmentFlag.AlignCenter, value_text)
        painter.setPen(QColor("#efffff"))
        value_rect = rect.adjusted(0, int(-9 * self._ui_scale), 0, 0)
        value_rect.translate(self._i(inward_shift), 0)
        painter.drawText(value_rect, Qt.AlignmentFlag.AlignCenter, value_text)

        painter.setPen(QColor("#9ed9ea"))
        painter.setFont(QFont("Bahnschrift", max(7, int((8 if self._compact else 10) * self._ui_scale)), QFont.Weight.Medium))
        unit_y_offset = int((26 if self._compact else 30) * self._ui_scale)
        unit_rect = rect.adjusted(0, unit_y_offset, 0, 0)
        unit_rect.translate(self._i(inward_shift), 0)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignHCenter, self.unit)

        # Needle is intentionally painted above center text to mimic automotive clusters.
        pointer_deg = self._value_to_angle(clamped_value)
        pointer_rad = math.radians(pointer_deg)
        pointer_radius = radius * 0.80
        counter_radius = radius * 0.08
        axis_vec = QPointF(math.cos(pointer_rad), -math.sin(pointer_rad))
        normal_vec = QPointF(-axis_vec.y(), axis_vec.x())
        needle_tip = QPointF(hub_center.x() + axis_vec.x() * pointer_radius, hub_center.y() + axis_vec.y() * pointer_radius)
        needle_tail = QPointF(hub_center.x() - axis_vec.x() * counter_radius, hub_center.y() - axis_vec.y() * counter_radius)

        needle_glow = QColor("#62f0ff")
        needle_glow.setAlpha(82)
        painter.setPen(QPen(needle_glow, 7.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(needle_tail, needle_tip)

        needle_color = QColor("#f6feff")
        painter.setPen(QPen(needle_color, 3.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(needle_tail, needle_tip)

        tip_base = QPointF(
            hub_center.x() + axis_vec.x() * (pointer_radius - radius * 0.06),
            hub_center.y() + axis_vec.y() * (pointer_radius - radius * 0.06),
        )
        tip_w = radius * 0.016
        tip_polygon = QPolygonF(
            [
                needle_tip,
                QPointF(tip_base.x() + normal_vec.x() * tip_w, tip_base.y() + normal_vec.y() * tip_w),
                QPointF(tip_base.x() - normal_vec.x() * tip_w, tip_base.y() - normal_vec.y() * tip_w),
            ]
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#bfffff"))
        painter.drawPolygon(tip_polygon)

        if counter_radius > 0:
            painter.setBrush(QColor("#bdefff"))
            painter.drawEllipse(needle_tail, radius * 0.016, radius * 0.016)

        hub_glow = QColor("#9db0c5")
        hub_glow.setAlpha(62)
        painter.setBrush(hub_glow)
        painter.drawEllipse(hub_center, 13, 13)
        painter.setBrush(QColor("#2b3748"))
        painter.drawEllipse(hub_center, 8, 8)
        painter.setBrush(QColor("#dbe8f6"))
        painter.drawEllipse(hub_center, 5, 5)
        painter.setBrush(QColor("#152232"))
        painter.drawEllipse(hub_center, 2.2, 2.2)
