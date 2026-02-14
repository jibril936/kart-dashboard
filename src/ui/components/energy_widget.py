from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget


class EnergyWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._voltage = 0.0
        self._current = 0.0

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1a2634;
                border-radius: 12px;
                border: 1px solid #2c3e50;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        battery_title = QLabel("BATTERIE")
        battery_title.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 10px; font-weight: 700; color: #8da7be;"
        )

        self.voltage_label = QLabel("52.0 V")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltage_label.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 32px; font-weight: 800; color: #ffffff;"
        )

        self.voltage_bar = QProgressBar()
        self.voltage_bar.setRange(440, 540)
        self.voltage_bar.setTextVisible(False)
        self.voltage_bar.setMinimumHeight(14)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #2c3e50; border: none;")

        current_title = QLabel("COURANT")
        current_title.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 10px; font-weight: 700; color: #8da7be;"
        )

        self.current_label = QLabel("+0 A")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_label.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 36px; font-weight: 800; color: #ffffff;"
        )

        self.current_bar = QProgressBar()
        self.current_bar.setRange(0, 200)
        self.current_bar.setTextVisible(False)
        self.current_bar.setMinimumHeight(14)

        layout.addWidget(battery_title)
        layout.addWidget(self.voltage_label)
        layout.addWidget(self.voltage_bar)
        layout.addStretch(1)
        layout.addWidget(divider)
        layout.addStretch(1)
        layout.addWidget(current_title)
        layout.addWidget(self.current_label)
        layout.addWidget(self.current_bar)

        self._set_voltage_bar_color("#2ecc71")
        self._set_current_bar_color("#00e5ff")

    def _set_voltage_bar_color(self, color: str) -> None:
        self.voltage_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #244458;
                border-radius: 6px;
                background-color: #0d121a;
            }}
            QProgressBar::chunk {{
                border-radius: 5px;
                background-color: {color};
            }}
            """
        )

    def _set_current_bar_color(self, color: str) -> None:
        self.current_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #1f4152;
                border-radius: 6px;
                background-color: #0d121a;
            }}
            QProgressBar::chunk {{
                border-radius: 5px;
                background-color: {color};
            }}
            """
        )

    def update_values(self, voltage: float, current: float) -> None:
        self._voltage = float(voltage)
        self._current = float(current)
        _power_kw = (self._voltage * self._current) / 1000.0

        self.voltage_label.setText(f"{self._voltage:.1f} V")
        self.current_label.setText(f"{self._current:+.0f} A")

        self.voltage_bar.setValue(int(round(self._voltage * 10)))
        if self._voltage <= 46.0:
            voltage_color = "#ff7f50"
        elif self._voltage <= 48.0:
            voltage_color = "#ffb347"
        else:
            voltage_color = "#36d47c"

        self.voltage_label.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; "
            f"font-size: 32px; font-weight: 800; color: {voltage_color};"
        )
        self._set_voltage_bar_color(voltage_color)

        current_magnitude = min(200, int(abs(self._current)))
        self.current_bar.setValue(current_magnitude)
        if self._current < 0:
            current_color = "#00bfff"
        else:
            current_color = "#00e5ff"

        self.current_label.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; "
            f"font-size: 36px; font-weight: 800; color: {current_color};"
        )
        self._set_current_bar_color(current_color)
