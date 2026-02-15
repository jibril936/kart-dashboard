from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class TemperatureStrip(QWidget):
    def __init__(self, title: str, maximum: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._max = maximum
        self._display = 0.0

        self._anim = QPropertyAnimation(self, b"displayTemp", self)
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setStyleSheet("background: transparent; border: none;")
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.label = QLabel(title)
        self.label.setStyleSheet("color: #7E8B97; font-size: 12px; letter-spacing: 2px; background: transparent; border: none;")
        self.value = QLabel("--°C")
        self.value.setStyleSheet("color: #EAF7FF; font-size: 20px; font-weight: 600; background: transparent; border: none;")

        root.addWidget(self.label, 0, Qt.AlignmentFlag.AlignVCenter)
        root.addStretch(1)
        root.addWidget(self.value, 0, Qt.AlignmentFlag.AlignVCenter)

        self.setMinimumHeight(34)

    def set_temp(self, value: float) -> None:
        clamped = max(0.0, min(self._max, float(value)))
        self._anim.stop()
        self._anim.setStartValue(self._display)
        self._anim.setEndValue(clamped)
        self._anim.start()

    @pyqtProperty(float)
    def displayTemp(self) -> float:  # noqa: N802
        return self._display

    @displayTemp.setter
    def displayTemp(self, value: float) -> None:  # noqa: N802
        self._display = float(value)
        self.value.setText(f"{self._display:.0f}°C")
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bar_rect = self.rect().adjusted(0, self.height() - 8, 0, -2)
        bar_rect.setHeight(6)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1B1B1B"))
        painter.drawRoundedRect(bar_rect, 3, 3)

        ratio = 0.0 if self._max <= 0 else max(0.0, min(1.0, self._display / self._max))
        fill_width = int(bar_rect.width() * ratio)
        if fill_width <= 0:
            return

        fill_rect = bar_rect.adjusted(0, 0, -(bar_rect.width() - fill_width), 0)
        painter.setBrush(QColor("#18BAFF"))
        painter.drawRoundedRect(fill_rect, 3, 3)


class NavButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def set_active(self, active: bool) -> None:
        self._active = active
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor("#FFFFFF") if self._active else QColor("#555555")
        painter.setPen(color)
        painter.setFont(self.font())
        painter.drawText(self.rect().adjusted(0, 0, 0, -8), Qt.AlignmentFlag.AlignCenter, self.text())
        if self._active:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#179BFF"))
            bar = self.rect().adjusted(self.width() // 3, self.height() - 5, -(self.width() // 3), -1)
            painter.drawRoundedRect(bar, 2, 2)


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        temp_row = QHBoxLayout()
        temp_row.setContentsMargins(0, 0, 0, 0)
        temp_row.setSpacing(40)

        self.motor_strip = TemperatureStrip("MOTEUR", 120.0)
        self.battery_strip = TemperatureStrip("BATTERIE", 80.0)

        temp_row.addWidget(self.motor_strip, 1)
        temp_row.addWidget(self.battery_strip, 1)

        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(120, 0, 120, 0)
        nav_row.setSpacing(26)

        self.cluster_button = NavButton("CLUSTER")
        self.tech_button = NavButton("TECH")
        self.graphs_button = NavButton("GRAPHS")
        self.cluster_button.set_active(True)

        for btn in (self.cluster_button, self.tech_button, self.graphs_button):
            btn.setMinimumHeight(30)
            nav_row.addWidget(btn)

        root.addLayout(temp_row)
        root.addLayout(nav_row)

    def update_temperatures(self, motor_temp: float, battery_temp: float) -> None:
        self.motor_strip.set_temp(float(motor_temp))
        self.battery_strip.set_temp(float(battery_temp))

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        _ = (battery_voltage, battery_soc_percent)
        if motor_temp_c is not None:
            self.update_temperatures(motor_temp_c, 0.0)


BottomBarStrip = BottomBar
