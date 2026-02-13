from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QWidget

from src.ui.visibility import set_visible_if, value_is_present

BATTERY_MIN_V = 44.0
BATTERY_MAX_V = 54.0
MOTOR_TEMP_MIN_C = 20.0
MOTOR_TEMP_MAX_C = 100.0


class _StripGauge(QWidget):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self.setMinimumHeight(58)

    def _draw_shell(self, painter: QPainter) -> tuple[QRectF, QRectF]:
        rect = QRectF(self.rect()).adjusted(4.0, 4.0, -4.0, -4.0)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#071224"))
        painter.drawRect(rect)

        gauge = QRectF(rect.left() + 8.0, rect.top() + 17.0, rect.width() - 16.0, 8.0)

        painter.setPen(QPen(QColor("#355c95"), 1.0))
        painter.drawLine(QPointF(gauge.left(), gauge.top()), QPointF(gauge.right(), gauge.top()))

        painter.setPen(QColor("#c5d9f2"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 8.0, rect.top() + 2.0, rect.width() - 16.0, 12.0), Qt.AlignmentFlag.AlignLeft, self._title)
        return rect, gauge


class BatteryBar(_StripGauge):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("BATTERY", parent)
        self._voltage: float | None = None

    def set_data(self, voltage: float | None, soc_percent: float | None) -> None:
        _ = soc_percent
        self._voltage = voltage
        self.update()

    def _fill_ratio(self) -> float:
        if self._voltage is None:
            return 0.0
        return max(0.0, min(1.0, (self._voltage - BATTERY_MIN_V) / (BATTERY_MAX_V - BATTERY_MIN_V)))

    @staticmethod
    def _fill_color() -> QColor:
        return QColor("#5bc0ff")

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect, gauge = self._draw_shell(painter)

        painter.setPen(QPen(QColor("#3e5370"), 1.0))
        for ratio in (0.0, 0.5, 1.0):
            x = gauge.left() + ratio * gauge.width()
            tick_h = 5.0 if ratio in (0.0, 1.0) else 4.0
            painter.drawLine(QPointF(x, gauge.top()), QPointF(x, gauge.top() - tick_h))

        fill = (gauge.width() - 2.0) * self._fill_ratio()
        if fill > 1.0:
            grad = QLinearGradient(gauge.topLeft(), gauge.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, self._fill_color())
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRect(QRectF(gauge.left() + 1.0, gauge.top() + 1.0, fill, gauge.height() - 2.0))

        painter.setPen(QColor("#8098b3"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
        painter.drawText(QRectF(gauge.left() - 2.0, gauge.bottom() + 2.0, 30.0, 12.0), Qt.AlignmentFlag.AlignLeft, f"{BATTERY_MIN_V:.0f}")
        painter.drawText(QRectF(gauge.right() - 26.0, gauge.bottom() + 2.0, 30.0, 12.0), Qt.AlignmentFlag.AlignRight, f"{BATTERY_MAX_V:.0f}")

        if self._voltage is not None:
            painter.setPen(self._fill_color())
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(QRectF(rect.left() + 100.0, gauge.bottom() + 1.0, rect.width() - 108.0, 14.0), Qt.AlignmentFlag.AlignLeft, f"{self._voltage:.1f} V")


class TempBar(_StripGauge):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("MOTOR TEMP", parent)
        self._temp_c: float = MOTOR_TEMP_MIN_C

    def set_data(self, temp_c: float) -> None:
        self._temp_c = temp_c
        self.update()

    def _ratio(self) -> float:
        return max(0.0, min(1.0, (self._temp_c - MOTOR_TEMP_MIN_C) / (MOTOR_TEMP_MAX_C - MOTOR_TEMP_MIN_C)))

    @staticmethod
    def _color() -> QColor:
        return QColor("#5bc0ff")

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect, gauge = self._draw_shell(painter)

        painter.setPen(QPen(QColor("#3e5370"), 1.0))
        for ratio in (0.0, 0.5, 1.0):
            x = gauge.left() + ratio * gauge.width()
            painter.drawLine(QPointF(x, gauge.top()), QPointF(x, gauge.top() - 5.0))

        fill = (gauge.width() - 2.0) * self._ratio()
        if fill > 1.0:
            grad = QLinearGradient(gauge.topLeft(), gauge.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, self._color())
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRect(QRectF(gauge.left() + 1.0, gauge.top() + 1.0, fill, gauge.height() - 2.0))

        painter.setPen(QColor("#8098b3"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
        painter.drawText(QRectF(gauge.left() - 2.0, gauge.bottom() + 2.0, 30.0, 12.0), Qt.AlignmentFlag.AlignLeft, f"{MOTOR_TEMP_MIN_C:.0f}")
        painter.drawText(QRectF(gauge.right() - 24.0, gauge.bottom() + 2.0, 30.0, 12.0), Qt.AlignmentFlag.AlignRight, f"{MOTOR_TEMP_MAX_C:.0f}")

        painter.setPen(self._color())
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 100.0, gauge.bottom() + 1.0, rect.width() - 108.0, 14.0), Qt.AlignmentFlag.AlignLeft, f"{self._temp_c:.0f}°C")


class BottomBarStrip(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomBarStrip")
        self.setMinimumHeight(66)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 4, 12, 4)
        self._layout.setSpacing(8)

        self.battery_bar = BatteryBar()
        self.temp_bar = TempBar()
        self.battery_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.temp_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._layout.addWidget(self.battery_bar, 1)
        self._layout.addWidget(self.temp_bar, 1)

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        show_battery = value_is_present(battery_voltage) or value_is_present(battery_soc_percent)
        if set_visible_if(self.battery_bar, show_battery):
            self.battery_bar.set_data(battery_voltage, battery_soc_percent)

        show_temp = value_is_present(motor_temp_c)
        if set_visible_if(self.temp_bar, show_temp):
            self.temp_bar.set_data(float(motor_temp_c))

        set_visible_if(self, show_battery or show_temp)

        if show_battery and show_temp:
            self._layout.setStretch(0, 1)
            self._layout.setStretch(1, 1)
        elif show_battery:
            self._layout.setStretch(0, 1)
            self._layout.setStretch(1, 0)
        elif show_temp:
            self._layout.setStretch(0, 0)
            self._layout.setStretch(1, 1)


BottomBar = BottomBarStrip
