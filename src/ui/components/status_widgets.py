from __future__ import annotations

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class AbsBadgeWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._active = False
        self.setFixedSize(68, 26)

    def set_active(self, active: bool) -> None:
        self._active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor("#ff8f66") if self._active else QColor("#647487")
        glow = QColor(255, 143, 102, 72) if self._active else QColor(100, 116, 135, 24)
        rect = QRectF(self.rect()).adjusted(1.0, 2.0, -1.0, -2.0)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow)
        painter.drawRoundedRect(rect.adjusted(-1.0, -1.0, 1.0, 1.0), 9.0, 9.0)

        painter.setPen(QPen(color, 1.2))
        painter.setBrush(QColor("#121c2a"))
        painter.drawRoundedRect(rect, 8.0, 8.0)

        painter.setPen(color)
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(rect.adjusted(8.0, 0.0, 0.0, -8.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "ABS")
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.DemiBold))
        painter.drawText(rect.adjusted(0.0, 8.0, -8.0, 0.0), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "ON" if self._active else "OFF")


class BatteryStatusWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._percent = 0.0
        self._voltage = 0.0
        self.setMinimumSize(170, 72)

    def setValue(self, percent: float, volts: float) -> None:  # noqa: N802
        self._percent = max(0.0, min(100.0, percent))
        self._voltage = volts
        self.update()

    def _color(self) -> QColor:
        if self._percent < 20:
            return QColor("#ff6d64")
        if self._percent < 45:
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

        level_color = self._color()
        battery_rect = QRectF(rect.left() + 10.0, rect.top() + 23.0, 42.0, 22.0)
        painter.setPen(QPen(QColor("#95abc2"), 1.1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(battery_rect, 3.0, 3.0)
        painter.drawRect(QRectF(battery_rect.right(), battery_rect.top() + 7.0, 4.0, 8.0))

        fill_width = (battery_rect.width() - 4.0) * (self._percent / 100.0)
        if fill_width > 1.0:
            grad = QLinearGradient(battery_rect.topLeft(), battery_rect.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, level_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(QRectF(battery_rect.left() + 2.0, battery_rect.top() + 2.0, fill_width, battery_rect.height() - 4.0), 2.0, 2.0)

        painter.setPen(QColor("#9ab1c8"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 60.0, rect.top() + 10.0, rect.width() - 68.0, 14.0), Qt.AlignmentFlag.AlignLeft, "BATTERY")

        painter.setPen(level_color)
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 60.0, rect.top() + 22.0, rect.width() - 68.0, 28.0), Qt.AlignmentFlag.AlignLeft, f"{self._percent:.0f}%")

        painter.setPen(QColor("#8ba2ba"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 60.0, rect.top() + 49.0, rect.width() - 68.0, 14.0), Qt.AlignmentFlag.AlignLeft, f"{self._voltage:.1f} V")


class TemperatureStatusWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._value = 0.0
        self._label = "MOTOR"
        self.setMinimumSize(180, 72)

    def setTemperature(self, value: float, label: str) -> None:  # noqa: N802
        self._value = value
        self._label = label
        self.update()

    def _ratio(self) -> float:
        return max(0.0, min(1.0, self._value / 120.0))

    def _color(self) -> QColor:
        if self._value >= 95.0:
            return QColor("#ff6d64")
        if self._value >= 80.0:
            return QColor("#ffb347")
        return QColor("#63c6a8")

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(2.0, 2.0, -2.0, -2.0)
        color = self._color()

        painter.setPen(QPen(QColor("#23354a"), 1.0))
        painter.setBrush(QColor("#0d1522"))
        painter.drawRoundedRect(rect, 10.0, 10.0)

        painter.setPen(QPen(QColor("#94abc2"), 1.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(QLineF(rect.left() + 16.0, rect.top() + 18.0, rect.left() + 16.0, rect.bottom() - 16.0))
        painter.drawEllipse(QRectF(rect.left() + 9.0, rect.bottom() - 21.0, 14.0, 14.0))

        gauge = QRectF(rect.left() + 30.0, rect.top() + 30.0, rect.width() - 40.0, 12.0)
        painter.setPen(QPen(QColor("#2e3f54"), 1.0))
        painter.setBrush(QColor("#0f1724"))
        painter.drawRoundedRect(gauge, 4.0, 4.0)

        fill = (gauge.width() - 4.0) * self._ratio()
        if fill > 1.0:
            grad = QLinearGradient(gauge.topLeft(), gauge.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(QRectF(gauge.left() + 2.0, gauge.top() + 2.0, fill, gauge.height() - 4.0), 3.0, 3.0)

        painter.setPen(QColor("#9ab1c8"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 30.0, rect.top() + 10.0, rect.width() - 36.0, 14.0), Qt.AlignmentFlag.AlignLeft, self._label)

        painter.setPen(color)
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 30.0, rect.top() + 42.0, rect.width() - 36.0, 18.0), Qt.AlignmentFlag.AlignLeft, f"{self._value:.0f}°C")


class ValueStatusWidget(QWidget):
    def __init__(self, title: str, unit: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._unit = unit
        self._value = 0.0
        self.setMinimumSize(150, 72)

    def setValue(self, value: float) -> None:  # noqa: N802
        self._value = value
        self.update()

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
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 10.0, rect.width() - 20.0, 14.0), Qt.AlignmentFlag.AlignLeft, self._title)

        painter.setPen(QColor("#63c6a8"))
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 24.0, rect.width() - 20.0, 24.0), Qt.AlignmentFlag.AlignLeft, f"{self._value:.0f}")

        painter.setPen(QColor("#8ba2ba"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 10.0, rect.top() + 50.0, rect.width() - 20.0, 14.0), Qt.AlignmentFlag.AlignLeft, self._unit)


class MeterBarWidget(QWidget):
    def __init__(self, label: str, color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = label
        self._color = QColor(color)
        self._ratio = 0.0
        self.setMinimumSize(130, 28)

    def setRatio(self, ratio: float) -> None:  # noqa: N802
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(1.0, 1.0, -1.0, -1.0)
        painter.setPen(QColor("#8399b0"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.drawText(rect.adjusted(0.0, 0.0, 0.0, -14.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom, self._label)

        bar = rect.adjusted(0.0, 13.0, 0.0, 0.0)
        painter.setPen(QPen(QColor("#2e3f54"), 1.0))
        painter.setBrush(QColor("#0f1724"))
        painter.drawRoundedRect(bar, 4.0, 4.0)

        fill = (bar.width() - 4.0) * self._ratio
        if fill > 1.0:
            grad = QLinearGradient(bar.topLeft(), bar.topRight())
            grad.setColorAt(0.0, QColor("#2f4674"))
            grad.setColorAt(1.0, self._color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(QRectF(bar.left() + 2.0, bar.top() + 2.0, fill, bar.height() - 4.0), 3.0, 3.0)
