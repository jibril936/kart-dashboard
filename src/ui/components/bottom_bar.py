from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from src.ui.visibility import set_visible_if, value_is_present


class BatteryBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._voltage: float | None = None
        self._soc_percent: float | None = None
        self.setMinimumHeight(64)

    def set_data(self, voltage: float | None, soc_percent: float | None) -> None:
        self._voltage = voltage
        self._soc_percent = None if soc_percent is None else max(0.0, min(100.0, soc_percent))
        self.update()

    def _level_color(self) -> QColor:
        if self._soc_percent is None:
            return QColor("#7b8ea4")
        if self._soc_percent < 20.0:
            return QColor("#ff6d64")
        if self._soc_percent < 45.0:
            return QColor("#ffb347")
        return QColor("#63c6a8")

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(2.0, 2.0, -2.0, -2.0)
        painter.setPen(QPen(QColor("#23354a"), 1.0))
        painter.setBrush(QColor("#0d1522"))
        painter.drawRoundedRect(rect, 10.0, 10.0)

        painter.setPen(QColor("#9ab1c8"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 8.0, rect.width() - 20.0, 14.0), Qt.AlignmentFlag.AlignLeft, "BATTERY")

        gauge = QRectF(rect.left() + 10.0, rect.top() + 25.0, rect.width() - 20.0, 14.0)
        painter.setPen(QPen(QColor("#2e3f54"), 1.0))
        painter.setBrush(QColor("#0f1724"))
        painter.drawRoundedRect(gauge, 4.0, 4.0)

        marker_pen = QPen(QColor("#53657a"), 1.0)
        painter.setPen(marker_pen)
        for ratio in (0.0, 0.5, 1.0):
            x = gauge.left() + ratio * gauge.width()
            painter.drawLine(QPointF(x, gauge.top()), QPointF(x, gauge.bottom()))

        fill = 0.0 if self._soc_percent is None else (gauge.width() - 4.0) * (self._soc_percent / 100.0)
        if fill > 1.0:
            grad = QLinearGradient(gauge.topLeft(), gauge.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, self._level_color())
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(QRectF(gauge.left() + 2.0, gauge.top() + 2.0, fill, gauge.height() - 4.0), 3.0, 3.0)

        painter.setPen(QColor("#8ba2ba"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 42.0, 60.0, 14.0), Qt.AlignmentFlag.AlignLeft, "0")
        painter.drawText(QRectF(rect.center().x() - 12.0, rect.top() + 42.0, 24.0, 14.0), Qt.AlignmentFlag.AlignCenter, "1/2")
        painter.drawText(QRectF(rect.right() - 30.0, rect.top() + 42.0, 20.0, 14.0), Qt.AlignmentFlag.AlignRight, "1")

        secondary = ""
        if self._soc_percent is not None:
            secondary = f"{self._soc_percent:.0f}%"
        if self._voltage is not None:
            secondary = f"{secondary}  ·  {self._voltage:.1f} V" if secondary else f"{self._voltage:.1f} V"
        painter.setPen(self._level_color())
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 74.0, rect.top() + 42.0, rect.width() - 84.0, 14.0), Qt.AlignmentFlag.AlignLeft, secondary)


class TempBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._temp_c = 0.0
        self.setMinimumHeight(64)

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

        rect = QRectF(self.rect()).adjusted(2.0, 2.0, -2.0, -2.0)
        painter.setPen(QPen(QColor("#23354a"), 1.0))
        painter.setBrush(QColor("#0d1522"))
        painter.drawRoundedRect(rect, 10.0, 10.0)

        painter.setPen(QColor("#9ab1c8"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 8.0, rect.width() - 20.0, 14.0), Qt.AlignmentFlag.AlignLeft, "MOTOR TEMP")

        gauge = QRectF(rect.left() + 10.0, rect.top() + 25.0, rect.width() - 20.0, 14.0)
        painter.setPen(QPen(QColor("#2e3f54"), 1.0))
        painter.setBrush(QColor("#0f1724"))
        painter.drawRoundedRect(gauge, 4.0, 4.0)

        marker_pen = QPen(QColor("#53657a"), 1.0)
        painter.setPen(marker_pen)
        for ratio in (0.0, 0.5, 1.0):
            x = gauge.left() + ratio * gauge.width()
            painter.drawLine(QPointF(x, gauge.top()), QPointF(x, gauge.bottom()))

        fill = (gauge.width() - 4.0) * self._ratio()
        if fill > 1.0:
            grad = QLinearGradient(gauge.topLeft(), gauge.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, self._color())
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(QRectF(gauge.left() + 2.0, gauge.top() + 2.0, fill, gauge.height() - 4.0), 3.0, 3.0)

        painter.setPen(QColor("#8ba2ba"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 42.0, 36.0, 14.0), Qt.AlignmentFlag.AlignLeft, "50")
        painter.drawText(QRectF(rect.center().x() - 12.0, rect.top() + 42.0, 24.0, 14.0), Qt.AlignmentFlag.AlignCenter, "75")
        painter.drawText(QRectF(rect.right() - 36.0, rect.top() + 42.0, 26.0, 14.0), Qt.AlignmentFlag.AlignRight, "100")

        painter.setPen(self._color())
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 74.0, rect.top() + 42.0, rect.width() - 84.0, 14.0), Qt.AlignmentFlag.AlignLeft, f"{self._temp_c:.0f}°C")


class BottomBarStrip(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(78)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 6, 8, 6)
        self._layout.setSpacing(10)

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
