from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout, QWidget


class TemperatureStrip(QWidget):
    def __init__(self, title: str, maximum: float, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._max = maximum

        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(8)

        self.label = QLabel(title)
        self.label.setStyleSheet(
            "color: #7E8B97; font-size: 12px; letter-spacing: 2px; font-weight: 600; background: transparent; border: none;"
        )

        self.value = QLabel("--°C")
        self.value.setStyleSheet(
            "color: #EAF7FF; font-size: 18px; font-weight: 700; background: transparent; border: none;"
        )

        head.addWidget(self.label)
        head.addStretch(1)
        head.addWidget(self.value)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setStyleSheet(
            """
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #1B1B1B;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #00ff00, stop:1 #ff0000);
            }
            """
        )

        root.addLayout(head)
        root.addWidget(self.bar)

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
                color: #555555;
                font-size: 15px;
                font-weight: 700;
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
                color: %s;
                font-size: 15px;
                font-weight: 700;
            }
            """
            % ("#FFFFFF" if active else "#555555")
        )


class BottomBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        temp_row = QHBoxLayout()
        temp_row.setContentsMargins(0, 0, 0, 0)
        temp_row.setSpacing(30)

        self.motor_strip = TemperatureStrip("MOTEUR", 120.0)
        self.battery_strip = TemperatureStrip("BATTERIE", 80.0)

        temp_row.addWidget(self.motor_strip, 1)
        temp_row.addWidget(self.battery_strip, 1)

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
        self.motor_strip.set_temp(float(motor_temp))
        self.battery_strip.set_temp(float(battery_temp))

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        _ = (battery_voltage, battery_soc_percent)
        if motor_temp_c is not None:
            self.update_temperatures(motor_temp_c, 0.0)


BottomBarStrip = BottomBar
