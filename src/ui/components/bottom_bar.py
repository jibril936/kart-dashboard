from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class TemperatureStrip(QWidget):
    def __init__(self, title: str, max_temp: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._max_temp = max_temp
        self._target_temp = 0.0
        self._display_temp = 0.0
        self.setMinimumHeight(52)
        self.setStyleSheet("background: transparent; border: none;")

        self.label = QLabel(f"{title} --°C")
        self.label.setStyleSheet("color: #dce7f7; font-size: 14px; font-weight: 600; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)
        root.addWidget(self.label)

        self._anim = QPropertyAnimation(self, b"displayTemp", self)
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_temp(self, value: float) -> None:
        self._target_temp = max(0.0, min(self._max_temp, float(value)))
        self._anim.stop()
        self._anim.setStartValue(self._display_temp)
        self._anim.setEndValue(self._target_temp)
        self._anim.start()

    @pyqtProperty(float)
    def displayTemp(self) -> float:  # noqa: N802
        return self._display_temp

    @displayTemp.setter
    def displayTemp(self, value: float) -> None:  # noqa: N802
        self._display_temp = float(value)
        self.label.setText(f"{self._title} {self._display_temp:.0f}°C")
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bar = self.rect().adjusted(0, self.height() - 12, 0, -2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#242424"))
        painter.drawRoundedRect(bar, 4, 4)

        ratio = max(0.0, min(1.0, self._display_temp / self._max_temp))
        fill = bar.adjusted(0, 0, int(-(bar.width() * (1.0 - ratio))), 0)
        grad = QLinearGradient(fill.topLeft(), fill.topRight())
        grad.setColorAt(0.0, QColor("#19c463"))
        grad.setColorAt(0.7, QColor("#c9b421"))
        grad.setColorAt(1.0, QColor("#f13f3f"))
        painter.setBrush(grad)
        painter.drawRoundedRect(fill, 4, 4)


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: #151515; border: none; border-radius: 12px;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(16)

        self.motor_strip = TemperatureStrip("MOTEUR", 120.0)
        self.battery_strip = TemperatureStrip("BATTERIE", 80.0)

        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.warning_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #8c9aad; border: none;")

        layout.addWidget(self.motor_strip, 1)
        layout.addWidget(self.battery_strip, 1)
        layout.addWidget(self.warning_label, 2)

    def update_temperatures(self, motor_temp: float, battery_temp: float) -> None:
        self.motor_strip.set_temp(float(motor_temp))
        self.battery_strip.set_temp(float(battery_temp))

    def update_warning(self, warnings: list[str]) -> None:
        if warnings:
            self.warning_label.setText(" | ".join(warnings).upper())
            self.warning_label.setStyleSheet("font-size: 14px; font-weight: 800; color: #ff5252; border: none;")
        else:
            self.warning_label.setText("")
            self.warning_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #8c9aad; border: none;")

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        _ = (battery_voltage, battery_soc_percent)
        if motor_temp_c is not None:
            self.update_temperatures(motor_temp_c, 0.0)


BottomBarStrip = BottomBar
