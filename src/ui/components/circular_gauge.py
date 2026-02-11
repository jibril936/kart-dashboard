from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
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
        self._value = min_value
        self.setMinimumSize(260, 260)

    def set_value(self, value: float) -> None:
        self._value = max(self.min_value, min(self.max_value, value))
        self.update()

    def _status_color(self) -> QColor:
        if self.critical_value is not None and self._value >= self.critical_value:
            return QColor("#ff5f56")
        if self.warning_value is not None and self._value >= self.warning_value:
            return QColor("#f7b731")
        return QColor("#5ad37a")

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(18, 18, -18, -18)
        center = rect.center()
        center_f = QPointF(center)
        radius = min(rect.width(), rect.height()) / 2
        arc_rect = rect.adjusted(16, 16, -16, -16)

        start_deg = 135
        span_deg = 270
        span_qt = int(-span_deg * 16)

        painter.setPen(QPen(QColor("#253141"), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(arc_rect, start_deg * 16, span_qt)

        if self.red_zone_start is not None:
            red_ratio = (self.red_zone_start - self.min_value) / max(1e-5, (self.max_value - self.min_value))
            red_ratio = max(0.0, min(1.0, red_ratio))
            red_start_deg = start_deg - span_deg * red_ratio
            red_span_deg = span_deg * (1 - red_ratio)
            painter.setPen(QPen(QColor("#ff5f56"), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(arc_rect, int(red_start_deg * 16), int(-red_span_deg * 16))

        ratio = (self._value - self.min_value) / max(1e-5, (self.max_value - self.min_value))
        ratio = max(0.0, min(1.0, ratio))
        value_span = span_deg * ratio

        painter.setPen(QPen(self._status_color(), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(arc_rect, start_deg * 16, int(-value_span * 16))

        tick_pen = QPen(QColor("#3a4a5f"), 2)
        painter.setPen(tick_pen)
        for i in range(0, 11):
            ang = math.radians(start_deg - (span_deg * i / 10))
            r1 = radius * 0.75
            r2 = radius * 0.84
            p1 = QPointF(center_f.x() + math.cos(ang) * r1, center_f.y() - math.sin(ang) * r1)
            p2 = QPointF(center_f.x() + math.cos(ang) * r2, center_f.y() - math.sin(ang) * r2)
            painter.drawLine(p1, p2)

        pointer_deg = start_deg - value_span
        pointer_rad = math.radians(pointer_deg)
        pointer_end = QPointF(
            center_f.x() + math.cos(pointer_rad) * radius * 0.67,
            center_f.y() - math.sin(pointer_rad) * radius * 0.67,
        )
        painter.setPen(QPen(QColor("#dbe7f4"), 3))
        painter.drawLine(center_f, pointer_end)
        painter.setBrush(QColor("#dbe7f4"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 6, 6)

        painter.setPen(QColor("#90a4bd"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        painter.drawText(rect.adjusted(0, 8, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)

        value_text = f"{self._value:.0f}" if self.max_value >= 100 else f"{self._value:.1f}"
        painter.setPen(QColor("#f2f7ff"))
        painter.setFont(QFont("Segoe UI", 30, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, value_text)

        painter.setPen(QColor("#8ea3ba"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        painter.drawText(rect.adjusted(0, 68, 0, 0), Qt.AlignmentFlag.AlignHCenter, self.unit)
