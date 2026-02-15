from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget


class LeafPowerGauge(QWidget):
    MIN_KW = -10.0
    MAX_KW = 10.0
    EMA_ALPHA = 0.2

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

        self.setMinimumSize(220, 250)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    def minimumSizeHint(self):  # noqa: N802
        return self.minimumSize()

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
        clamped_kw = max(self.MIN_KW, min(self.MAX_KW, power_kw))

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

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(8, 8, -8, -8)
        painter.setPen(QPen(QColor("#203646"), 1.0))
        painter.setBrush(QColor("#0c131c"))
        painter.drawRoundedRect(rect, 16, 16)

        center = QPointF(rect.center().x(), rect.center().y() + rect.height() * 0.17)
        radius = min(rect.width(), rect.height()) * 0.42
        arc_rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)

        track_width = max(8.0, radius * 0.12)
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

        painter.setPen(QColor("#8eb5cd"))
        label_font = QFont("Bahnschrift", max(8, int(rect.height() * 0.045)), QFont.Weight.DemiBold)
        painter.setFont(label_font)

        for text, angle, dist in (
            ("REGEN", 240, radius + 24),
            ("ECO", 330, radius + 24),
            ("POWER", 55, radius + 24),
        ):
            point = self._point_on_arc(center, dist, angle)
            label_rect = QRectF(point.x() - 28, point.y() - 10, 56, 20)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, text)

        if self._has_data and self._current is not None and self._power_kw_raw is not None:
            power_text = f"{self._power_kw_raw:+.1f} kW"
            current_text = f"{self._current:+.0f} A"
        else:
            power_text = "N/A"
            current_text = "N/A"

        power_font = QFont("Bahnschrift", max(13, int(rect.height() * 0.108)), QFont.Weight.Bold)
        small_font = QFont("Bahnschrift", max(9, int(rect.height() * 0.055)), QFont.Weight.DemiBold)

        painter.setFont(power_font)
        painter.setPen(QColor("#dff7ff"))
        power_rect = QRectF(rect.left(), center.y() - (radius * 0.10), rect.width(), radius * 0.42)
        painter.drawText(power_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, power_text)

        painter.setFont(small_font)
        painter.setPen(QColor("#97bfd7"))
        current_rect = QRectF(rect.left(), center.y() + (radius * 0.16), rect.width(), radius * 0.30)
        painter.drawText(current_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, current_text)

        needle_angle = self._kw_to_angle(self._power_kw_smooth if self._has_data else 0.0)
        needle_start = self._point_on_arc(center, radius * 0.14, needle_angle)
        needle_end = self._point_on_arc(center, radius * 0.98, needle_angle)
        painter.setPen(QPen(QColor("#eef7ff"), max(2.0, radius * 0.02), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(needle_start, needle_end)

        dot = self._point_on_arc(center, radius * 0.98, needle_angle)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#7ce8ff"))
        painter.drawEllipse(dot, max(3.0, radius * 0.05), max(3.0, radius * 0.05))

        painter.setBrush(QColor("#0a1018"))
        painter.setPen(QPen(QColor("#7fdfff"), 1.2))
        painter.drawEllipse(center, max(7.0, radius * 0.09), max(7.0, radius * 0.09))
