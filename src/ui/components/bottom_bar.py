from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QWidget

from src.ui.visibility import set_visible_if, value_is_present

BATTERY_MIN_V = 44.0
BATTERY_MAX_V = 54.0
MOTOR_TEMP_MIN_C = 20.0
MOTOR_TEMP_MAX_C = 100.0


class _StripGauge(QWidget):
    def __init__(self, title: str, icon: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._icon = icon
        self.setMinimumHeight(74)

    def _draw_shell(self, painter: QPainter) -> tuple[QRectF, QRectF]:
        rect = QRectF(self.rect()).adjusted(3.0, 4.0, -3.0, -4.0)
        shell = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        shell.setColorAt(0.0, QColor("#152130"))
        shell.setColorAt(1.0, QColor("#070d15"))
        painter.setPen(QPen(QColor("#3d4f63"), 1.2))
        painter.setBrush(shell)
        painter.drawRoundedRect(rect, 9, 9)

        gauge = QRectF(rect.left() + 14.0, rect.top() + 28.0, rect.width() - 28.0, 17.0)
        painter.setPen(QPen(QColor("#263646"), 1.0))
        painter.setBrush(QColor("#03070e"))
        painter.drawRoundedRect(gauge, 5, 5)

        painter.setPen(QColor("#a7f5ff"))
        painter.setFont(QFont("Bahnschrift", 9, QFont.Weight.DemiBold))
        painter.drawText(QRectF(rect.left() + 12, rect.top() + 5, rect.width() - 24, 16), Qt.AlignmentFlag.AlignLeft, f"{self._icon} {self._title}")
        return rect, gauge

    def _segment_fill(self, painter: QPainter, gauge: QRectF, ratio: float, cold: QColor, hot: QColor) -> None:
        segments = 16
        gap = 2.0
        segment_w = (gauge.width() - gap * (segments - 1)) / segments
        active = int(round(segments * ratio))
        for i in range(segments):
            x = gauge.left() + i * (segment_w + gap)
            seg = QRectF(x, gauge.top() + 2.0, segment_w, gauge.height() - 4.0)
            t = i / max(1, segments - 1)
            color = QColor(
                int(cold.red() + (hot.red() - cold.red()) * t),
                int(cold.green() + (hot.green() - cold.green()) * t),
                int(cold.blue() + (hot.blue() - cold.blue()) * t),
            )
            if i < active:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(color)
                painter.drawRoundedRect(seg, 2, 2)
            else:
                muted = QColor(color)
                muted.setAlpha(38)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(muted)
                painter.drawRoundedRect(seg, 2, 2)


class BatteryBar(_StripGauge):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("BATTERY", "⚡", parent)
        self._voltage: float | None = None

    def set_data(self, voltage: float | None, soc_percent: float | None) -> None:
        _ = soc_percent
        self._voltage = voltage
        self.update()

    def _fill_ratio(self) -> float:
        if self._voltage is None:
            return 0.0
        return max(0.0, min(1.0, (self._voltage - BATTERY_MIN_V) / (BATTERY_MAX_V - BATTERY_MIN_V)))

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect, gauge = self._draw_shell(painter)

        ratio = self._fill_ratio()
        self._segment_fill(painter, gauge, ratio, QColor("#ff3b3b"), QColor("#4cff7e"))

        painter.setPen(QColor("#89a9be"))
        painter.setFont(QFont("Bahnschrift", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(gauge.left(), gauge.bottom() + 4.0, 28.0, 14.0), Qt.AlignmentFlag.AlignLeft, f"{BATTERY_MIN_V:.0f}")
        painter.drawText(QRectF(gauge.right() - 30.0, gauge.bottom() + 4.0, 30.0, 14.0), Qt.AlignmentFlag.AlignRight, f"{BATTERY_MAX_V:.0f}")

        if self._voltage is not None:
            painter.setPen(QColor("#b6ffca"))
            painter.setFont(QFont("Bahnschrift", 11, QFont.Weight.Bold))
            painter.drawText(QRectF(rect.left() + 115.0, rect.top() + 4.0, rect.width() - 120.0, 16.0), Qt.AlignmentFlag.AlignLeft, f"{self._voltage:.1f} V")


class TempBar(_StripGauge):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("MOTOR TEMP", "🌡", parent)
        self._temp_c: float = MOTOR_TEMP_MIN_C

    def set_data(self, temp_c: float) -> None:
        self._temp_c = temp_c
        self.update()

    def _ratio(self) -> float:
        return max(0.0, min(1.0, (self._temp_c - MOTOR_TEMP_MIN_C) / (MOTOR_TEMP_MAX_C - MOTOR_TEMP_MIN_C)))

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect, gauge = self._draw_shell(painter)

        ratio = self._ratio()
        self._segment_fill(painter, gauge, ratio, QColor("#2ca3ff"), QColor("#ff4135"))

        painter.setPen(QColor("#89a9be"))
        painter.setFont(QFont("Bahnschrift", 8, QFont.Weight.DemiBold))
        painter.drawText(QRectF(gauge.left(), gauge.bottom() + 4.0, 30.0, 14.0), Qt.AlignmentFlag.AlignLeft, f"{MOTOR_TEMP_MIN_C:.0f}")
        painter.drawText(QRectF(gauge.right() - 30.0, gauge.bottom() + 4.0, 30.0, 14.0), Qt.AlignmentFlag.AlignRight, f"{MOTOR_TEMP_MAX_C:.0f}")

        painter.setPen(QColor("#ffd0ca"))
        painter.setFont(QFont("Bahnschrift", 11, QFont.Weight.Bold))
        painter.drawText(QRectF(rect.left() + 132.0, rect.top() + 4.0, rect.width() - 140.0, 16.0), Qt.AlignmentFlag.AlignLeft, f"{self._temp_c:.0f}°C")


class BottomBarStrip(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomBarStrip")
        self.setMinimumHeight(82)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 4, 10, 4)
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
