from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QConicalGradient, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class AnalogGaugeWidget(QWidget):
    """OLED-inspired analog gauge with arc progress and central numeric value."""

    def __init__(
        self,
        minValue: float = 0.0,
        maxValue: float = 100.0,
        units: str = "",
        gaugeColor: QColor | str = "#00FFFF",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.minValue = minValue
        self.maxValue = maxValue
        self.units = units
        self.gaugeColor = QColor(gaugeColor)
        self._value = minValue

        self.setMinimumSize(220, 220)
        self.setAutoFillBackground(False)

    @property
    def value(self) -> float:
        return self._value

    def setValue(self, value: float) -> None:
        clamped_value = max(self.minValue, min(self.maxValue, value))
        if clamped_value != self._value:
            self._value = clamped_value
            self.update()

    def paintEvent(self, event) -> None:  # noqa: ANN001
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.fillRect(self.rect(), QColor("#000000"))

        size = min(self.width(), self.height())
        margin = size * 0.14
        arc_rect = QRectF(
            (self.width() - size) / 2 + margin,
            (self.height() - size) / 2 + margin,
            size - 2 * margin,
            size - 2 * margin,
        )

        start_angle = 225 * 16
        total_span = 270 * 16
        arc_width = max(10, int(size * 0.07))

        background_pen = QPen(QColor("#1C1C1C"), arc_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(background_pen)
        painter.drawArc(arc_rect, start_angle, -total_span)

        gradient = QConicalGradient(arc_rect.center(), 90)
        gradient.setColorAt(0.00, QColor("#222222"))
        gradient.setColorAt(0.50, self.gaugeColor)
        gradient.setColorAt(1.00, QColor("#222222"))

        progress_pen = QPen(gradient, arc_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)

        range_span = self.maxValue - self.minValue
        progress_ratio = 0.0 if range_span == 0 else (self._value - self.minValue) / range_span
        progress_span = int(total_span * progress_ratio)
        painter.drawArc(arc_rect, start_angle, -progress_span)

        value_font = QFont("Arial", max(18, int(size * 0.18)), QFont.Weight.Bold)
        painter.setFont(value_font)
        painter.setPen(QColor("#F5F5F5"))
        value_text = f"{self._value:.0f}"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, value_text)

        if self.units:
            units_font = QFont("Arial", max(10, int(size * 0.06)), QFont.Weight.DemiBold)
            painter.setFont(units_font)
            painter.setPen(self.gaugeColor)
            units_rect = self.rect().adjusted(0, int(size * 0.20), 0, 0)
            painter.drawText(units_rect, Qt.AlignmentFlag.AlignCenter, self.units)
