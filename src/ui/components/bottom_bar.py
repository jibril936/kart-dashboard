from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QWidget

from src.ui.visibility import set_visible_if, value_is_present


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

        painter.setPen(QColor("#9bb5d2"))
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 8.0, rect.top() + 2.0, rect.width() - 16.0, 12.0), Qt.AlignmentFlag.AlignLeft, self._title)
        return rect, gauge


class BatteryBar(_StripGauge):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("BATTERY", parent)
        self._voltage: float | None = None
        self._soc_percent: float | None = None

    def set_data(self, voltage: float | None, soc_percent: float | None) -> None:
        self._voltage = voltage
        self._soc_percent = None if soc_percent is None else max(0.0, min(100.0, soc_percent))
        self.update()

    def _fill_ratio(self) -> float:
        if self._soc_percent is None:
            return 0.0
        return self._soc_percent / 100.0

    def _fill_color(self) -> QColor:
        if self._soc_percent is None:
            return QColor("#5a6780")
        if self._soc_percent < 20.0:
            return QColor("#ff6d64")
        if self._soc_percent < 45.0:
            return QColor("#ffb347")
        return QColor("#63c6a8")

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect, gauge = self._draw_shell(painter)

        painter.setPen(QPen(QColor("#3e5370"), 1.0))
        for ratio in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = gauge.left() + ratio * gauge.width()
            tick_h = 5.0 if ratio in (0.0, 0.5, 1.0) else 3.0
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
        painter.drawText(QRectF(gauge.left() - 2.0, gauge.bottom() + 2.0, 20.0, 12.0), Qt.AlignmentFlag.AlignLeft, "0")
        painter.drawText(QRectF(gauge.center().x() - 14.0, gauge.bottom() + 2.0, 28.0, 12.0), Qt.AlignmentFlag.AlignCenter, "1/2")
        painter.drawText(QRectF(gauge.right() - 14.0, gauge.bottom() + 2.0, 18.0, 12.0), Qt.AlignmentFlag.AlignRight, "1")

        if self._voltage is not None:
            value_text = f"{self._voltage:.1f} V"
            if self._soc_percent is not None:
                value_text = f"{self._soc_percent:.0f}%  {value_text}"
            painter.setPen(self._fill_color())
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            painter.drawText(QRectF(rect.left() + 100.0, gauge.bottom() + 1.0, rect.width() - 108.0, 14.0), Qt.AlignmentFlag.AlignLeft, value_text)


class TempBar(_StripGauge):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("MOTOR TEMP", parent)
        self._temp_c: float = 0.0

    def set_data(self, temp_c: float) -> None:
        self._temp_c = temp_c
        self.update()

    def _ratio(self) -> float:
        return max(0.0, min(1.0, (self._temp_c - 50.0) / 50.0))

    def _color(self) -> QColor:
        if self._temp_c >= 95.0:
            return QColor("#ff6d64")
        if self._temp_c >= 80.0:
            return QColor("#ffb347")
        return QColor("#63c6a8")

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
        painter.drawText(QRectF(gauge.left() - 2.0, gauge.bottom() + 2.0, 24.0, 12.0), Qt.AlignmentFlag.AlignLeft, "50")
        painter.drawText(QRectF(gauge.center().x() - 10.0, gauge.bottom() + 2.0, 20.0, 12.0), Qt.AlignmentFlag.AlignCenter, "")
        painter.drawText(QRectF(gauge.right() - 22.0, gauge.bottom() + 2.0, 26.0, 12.0), Qt.AlignmentFlag.AlignRight, "100")

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
