from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout, QWidget


class TemperatureStrip(QWidget):
    def __init__(self, maximum: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._max = maximum

        self.setStyleSheet("background: transparent; border: none;")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        self.value = QLabel("--°C")
        self.value.setStyleSheet(
            "color: #FFFFFF; font-family: 'Roboto Mono', 'Inter'; font-size: 14pt; font-weight: 600; background: transparent; border: none;"
        )

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setMinimumWidth(380)
        self.bar.setStyleSheet(
            """
            QProgressBar {
                border: none;
                border-radius: 0px;
                background-color: #1E252C;
            }
            QProgressBar::chunk {
                border-radius: 0px;
                background: #00FFFF;
            }
            """
        )

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(22)
        glow.setOffset(0, 0)
        glow.setColor(Qt.GlobalColor.cyan)
        self.bar.setGraphicsEffect(glow)

        root.addWidget(self.bar, 1)
        root.addWidget(self.value, 0, Qt.AlignmentFlag.AlignVCenter)

    def set_temp(self, value: float) -> None:
        clamped = max(0.0, min(self._max, float(value)))
        ratio = 0.0 if self._max <= 0 else clamped / self._max
        self.value.setText(f"{clamped:.0f}°C")
        self.bar.setValue(int(ratio * 100))


class NavButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self._active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(30)
        self.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #626E79;
                font-size: 15px;
                font-weight: 700;
                padding: 4px 0 8px 0;
            }
            QPushButton:hover {
                color: #b8d8f0;
            }
            """
        )

    def set_active(self, active: bool) -> None:
        self._active = active
        self.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                border-bottom: %s;
                color: %s;
                font-size: 15px;
                font-weight: 700;
                padding: 4px 0 8px 0;
            }
            """
            % ("3px solid #00FFFF" if active else "3px solid transparent", "#FFFFFF" if active else "#626E79")
        )


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        temp_row = QHBoxLayout()
        temp_row.setContentsMargins(0, 0, 0, 0)
        temp_row.setSpacing(0)

        self.motor_strip = TemperatureStrip(120.0)

        temp_row.addWidget(self.motor_strip, 1)

        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(100, 0, 100, 0)
        nav_row.setSpacing(26)

        self.cluster_button = NavButton("CLUSTER")
        self.tech_button = NavButton("TECH")
        self.graphs_button = NavButton("GRAPHS")
        self.cluster_button.set_active(True)

        nav_row.addWidget(self.cluster_button)
        nav_row.addWidget(self.tech_button)
        nav_row.addWidget(self.graphs_button)

        root.addLayout(temp_row)
        root.addLayout(nav_row)

    def update_temperatures(self, motor_temp: float, battery_temp: float) -> None:
        _ = battery_temp
        self.motor_strip.set_temp(float(motor_temp))

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        _ = (battery_voltage, battery_soc_percent)
        if motor_temp_c is not None:
            self.update_temperatures(motor_temp_c, 0.0)


BottomBarStrip = BottomBar
