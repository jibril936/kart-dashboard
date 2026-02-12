from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.ui.visibility import set_visible_if


@dataclass(slots=True)
class IndicatorSpec:
    key: str
    icon: str
    label: str
    active_color: str = "#ffb347"


class IndicatorGlyph(QWidget):
    def __init__(self, spec: IndicatorSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.spec = spec
        self.active = False
        self.setFixedSize(38, 28)

    def set_status(self, active: bool) -> None:
        self.active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor(self.spec.active_color if self.active else "#5f6670")
        painter.setPen(QPen(color, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        cx = self.width() / 2
        cy = self.height() / 2
        kind = self.spec.icon
        # PyQt6 overload resolution is strict: float geometry must use QRectF (or explicit int args).

        if kind == "battery":
            painter.drawRoundedRect(QRectF(cx - 9, cy - 5, 16, 10), 2, 2)
            painter.drawRect(int(cx + 7), int(cy - 2), 3, 4)
        elif kind == "temp":
            painter.drawLine(QPointF(cx - 6, cy + 6), QPointF(cx - 6, cy - 2))
            painter.drawEllipse(QPointF(cx - 6, cy + 7), 3, 3)
            painter.drawArc(int(cx - 3), int(cy - 5), 11, 11, 80 * 16, 220 * 16)
        elif kind == "charging":
            bolt = QPainterPath()
            bolt.moveTo(cx - 3, cy - 7)
            bolt.lineTo(cx + 1, cy - 7)
            bolt.lineTo(cx - 1, cy)
            bolt.lineTo(cx + 4, cy)
            bolt.lineTo(cx - 2, cy + 8)
            bolt.lineTo(cx, cy + 2)
            bolt.lineTo(cx - 4, cy + 2)
            bolt.closeSubpath()
            painter.setBrush(color)
            painter.drawPath(bolt)
        elif kind == "brake":
            painter.drawEllipse(QPointF(cx, cy), 7, 7)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "!")
        elif kind == "steer":
            painter.drawEllipse(QPointF(cx, cy), 7, 7)
            painter.drawLine(QPointF(cx - 6, cy), QPointF(cx + 6, cy))
            painter.drawLine(QPointF(cx, cy), QPointF(cx, cy + 5))
        elif kind == "station":
            painter.drawRoundedRect(QRectF(cx - 7, cy - 6, 14, 13), 2, 2)
            painter.drawLine(QPointF(cx - 3, cy - 2), QPointF(cx - 1, cy - 5))
            painter.drawLine(QPointF(cx + 1, cy - 2), QPointF(cx + 3, cy - 5))
        elif kind == "rpm":
            painter.drawArc(int(cx - 8), int(cy - 8), 16, 16, 25 * 16, 240 * 16)
            painter.drawLine(QPointF(cx, cy), QPointF(cx + 5, cy - 4))
        elif kind == "speed":
            painter.drawArc(int(cx - 8), int(cy - 8), 16, 16, 30 * 16, 220 * 16)
            painter.drawLine(QPointF(cx, cy), QPointF(cx + 6, cy - 1))
        elif kind == "sensor":
            painter.drawArc(int(cx - 7), int(cy - 7), 14, 14, 35 * 16, 110 * 16)
            painter.drawArc(int(cx - 10), int(cy - 10), 20, 20, 35 * 16, 110 * 16)
            painter.drawEllipse(QPointF(cx - 2, cy + 5), 1.8, 1.8)
        elif kind == "ready":
            painter.drawLine(QPointF(cx - 6, cy + 1), QPointF(cx - 2, cy + 6))
            painter.drawLine(QPointF(cx - 2, cy + 6), QPointF(cx + 7, cy - 5))
        elif kind == "abs":
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            painter.drawRoundedRect(QRectF(cx - 10, cy - 6, 20, 12), 3, 3)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "ABS")
        else:
            painter.setPen(QPen(color, 1.0))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.spec.label[:2])


class IndicatorRow(QWidget):
    def __init__(self, indicators: list[IndicatorSpec], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)
        layout.addStretch(1)

        self._chips: dict[str, IndicatorGlyph] = {}
        for spec in indicators:
            glyph = IndicatorGlyph(spec)
            layout.addWidget(glyph)
            self._chips[spec.key] = glyph

        layout.addStretch(1)

    def update_status(self, statuses: dict[str, bool | None]) -> None:
        for key, chip in self._chips.items():
            value = statuses.get(key)
            set_visible_if(chip, value is not None)
            chip.set_status(bool(value))
