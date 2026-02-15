from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget


class LeafPowerGauge(QWidget):
    MIN_KW = -10.0
    MAX_KW = 10.0
    EMA_ALPHA = 0.25

    START_ANGLE_DEG = 210.0
    SPAN_ANGLE_DEG = 240.0

    REGEN_MAX_KW = -2.0
    ECO_MAX_KW = 2.0

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._voltage: float | None = None
        self._current: float | None = None
        self._power_kw_raw: float | None = None
        self._power_kw_smooth = 0.0
        self._has_data = False

        self.setMinimumSize(220, 220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def minimumSizeHint(self):  # noqa: N802
        return QSize(220, 220)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))

    def set_values(self, v_pack: float | None, i_pack: float | None) -> None:
        if v_pack is None or i_pack is None:
            self._voltage = v_pack
            self._current = i_pack
            self._power_kw_raw = None
            self._has_data = False
            self.update()
            return

        self._voltage = float(v_pack)
        self._current = float(i_pack)
        power_kw = (self._voltage * self._current) / 1000.0
        clamped_kw = self._clamp(power_kw, self.MIN_KW, self.MAX_KW)

        if not self._has_data:
            self._power_kw_smooth = clamped_kw
        else:
            self._power_kw_smooth = (self.EMA_ALPHA * clamped_kw) + ((1.0 - self.EMA_ALPHA) * self._power_kw_smooth)

        self._power_kw_raw = clamped_kw
        self._has_data = True
        self.update()

    def _kw_to_angle(self, power_kw: float) -> float:
        normalized = (power_kw - self.MIN_KW) / max(1e-6, self.MAX_KW - self.MIN_KW)
        return self.START_ANGLE_DEG + normalized * self.SPAN_ANGLE_DEG

    @staticmethod
    def _point_on_arc(center: QPointF, radius: float, angle_deg: float) -> QPointF:
        angle_rad = math.radians(angle_deg)
        return QPointF(
            center.x() + (radius * math.cos(angle_rad)),
            center.y() - (radius * math.sin(angle_rad)),
        )

    def _draw_zone(self, painter: QPainter, arc_rect: QRectF, min_kw: float, max_kw: float, color: QColor, width: float) -> None:
        start_deg = self._kw_to_angle(min_kw)
        end_deg = self._kw_to_angle(max_kw)
        span_deg = end_deg - start_deg
        painter.setPen(QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(arc_rect, int(-start_deg * 16), int(-span_deg * 16))

    def _fit_label_font(self, text: str, max_width: float, max_height: float, start_px: int) -> QFont:
        px = max(8, start_px)
        while px >= 8:
            font = QFont("Bahnschrift", px, QFont.Weight.DemiBold)
            fm = QFontMetrics(font)
            if fm.horizontalAdvance(text) <= max_width and fm.height() <= max_height:
                return font
            px -= 1
        return QFont("Bahnschrift", 8, QFont.Weight.DemiBold)

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        base_rect = QRectF(self.rect()).adjusted(4, 4, -4, -4)
        w = base_rect.width()
        h = base_rect.height()
        pad = max(10, int(min(w, h) * 0.06))
        content = base_rect.adjusted(pad, pad, -pad, -pad)

        gauge_h = content.height() * 0.68
        text_h = content.height() * 0.22
        labels_h = content.height() - gauge_h - text_h

        zone_gauge = QRectF(content.left(), content.top(), content.width(), gauge_h)
        zone_text = QRectF(content.left(), zone_gauge.bottom(), content.width(), text_h)
        zone_labels = QRectF(content.left(), zone_text.bottom(), content.width(), labels_h)

        painter.setPen(QPen(QColor("#203646"), 1.0))
        painter.setBrush(QColor("#0c131c"))
        painter.drawRoundedRect(base_rect, 16, 16)

        center = zone_gauge.center()
        radius = 0.45 * min(zone_gauge.width(), zone_gauge.height())
        arc_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)

        track_width = max(6.0, radius * 0.10)
        painter.setPen(QPen(QColor("#2a3f53"), track_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(arc_rect, int(-self.START_ANGLE_DEG * 16), int(-self.SPAN_ANGLE_DEG * 16))

        self._draw_zone(painter, arc_rect, self.MIN_KW, self.REGEN_MAX_KW, QColor("#39b8ff"), track_width)
        self._draw_zone(painter, arc_rect, self.REGEN_MAX_KW, self.ECO_MAX_KW, QColor("#63d597"), track_width)
        self._draw_zone(painter, arc_rect, self.ECO_MAX_KW, self.MAX_KW, QColor("#f4ad4f"), track_width)

        tick_pen = QPen(QColor("#85a4bd"), 1.2)
        painter.setPen(tick_pen)
        for tick_kw in (-10, -5, 0, 5, 10):
            tick_angle = self._kw_to_angle(float(tick_kw))
            outer = self._point_on_arc(center, radius + 6, tick_angle)
            inner = self._point_on_arc(center, radius - 11, tick_angle)
            painter.drawLine(outer, inner)

        if self._has_data and self._current is not None and self._power_kw_raw is not None:
            power_text = f"{self._power_kw_raw:+.1f} kW"
            current_text = f"{self._current:+.0f} A"
        else:
            power_text = "N/A"
            current_text = "N/A"

        scale_ref = min(content.width(), content.height())
        big_font_px = int(self._clamp(int(scale_ref * 0.14), 22, 42))
        small_font_px = int(self._clamp(int(scale_ref * 0.07), 14, 22))

        power_font = QFont("Bahnschrift", big_font_px, QFont.Weight.Bold)
        small_font = QFont("Bahnschrift", small_font_px, QFont.Weight.DemiBold)

        painter.setFont(power_font)
        painter.setPen(QColor("#dff7ff"))
        power_rect = QRectF(zone_text.left(), zone_text.top(), zone_text.width(), zone_text.height() * 0.62)
        painter.drawText(power_rect, Qt.AlignmentFlag.AlignCenter, power_text)

        painter.setFont(small_font)
        painter.setPen(QColor("#97bfd7"))
        current_rect = QRectF(zone_text.left(), power_rect.bottom(), zone_text.width(), zone_text.bottom() - power_rect.bottom())
        painter.drawText(current_rect, Qt.AlignmentFlag.AlignCenter, current_text)

        labels = [("REGEN", "REG"), ("ECO", "ECO"), ("POWER", "PWR")]
        col_w = zone_labels.width() / 3.0
        max_label_h = max(10.0, zone_labels.height() * 0.9)
        painter.setPen(QColor("#8eb5cd"))
        for idx, (full_text, short_text) in enumerate(labels):
            cell = QRectF(zone_labels.left() + (idx * col_w), zone_labels.top(), col_w, zone_labels.height())
            preferred_font = self._fit_label_font(full_text, cell.width() * 0.9, max_label_h, int(scale_ref * 0.055))
            fm = QFontMetrics(preferred_font)
            label_text = full_text
            if fm.horizontalAdvance(full_text) > cell.width() * 0.9:
                label_text = short_text
                preferred_font = self._fit_label_font(short_text, cell.width() * 0.9, max_label_h, preferred_font.pixelSize())
            painter.setFont(preferred_font)
            painter.drawText(cell, Qt.AlignmentFlag.AlignCenter, label_text)

        needle_angle = self._kw_to_angle(self._power_kw_smooth if self._has_data else 0.0)
        needle_start = self._point_on_arc(center, radius * 0.10, needle_angle)
        needle_end = self._point_on_arc(center, radius * 0.85, needle_angle)
        painter.setPen(
            QPen(QColor("#d7fbff"), max(2.0, radius * 0.03), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        )
        painter.drawLine(needle_start, needle_end)

        painter.setBrush(QColor("#071018"))
        painter.setPen(QPen(QColor("#87f2ff"), max(1.4, radius * 0.015)))
        painter.drawEllipse(center, max(7.0, radius * 0.09), max(7.0, radius * 0.09))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#bcf7ff"))
        painter.drawEllipse(center, max(3.0, radius * 0.045), max(3.0, radius * 0.045))
