from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


class EnergyWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._voltage = 0.0
        self._current = 0.0

        self.setStyleSheet("background-color: #1a2634; border-radius: 15px; border: 1px solid #2c3e50;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        battery_title = QLabel("BATTERIE")
        battery_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        battery_title.setStyleSheet(
            "font-family: Arial, sans-serif; font-size: 10px; font-weight: 600; color: #afc0d4; border: none; background: transparent;"
        )

        self.voltage_label = QLabel("52.0 V")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltage_label.setStyleSheet(
            "font-family: Arial, sans-serif; font-size: 44px; font-weight: 800; color: #ffffff; border: none; background: transparent;"
        )

        self.voltage_bar = QProgressBar()
        self.voltage_bar.setRange(440, 540)
        self.voltage_bar.setMinimumHeight(30)
        self.voltage_bar.setTextVisible(True)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #2c3e50; border: none;")

        power_title = QLabel("PUISSANCE")
        power_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        power_title.setStyleSheet(
            "font-family: Arial, sans-serif; font-size: 10px; font-weight: 600; color: #afc0d4; border: none; background: transparent;"
        )

        self.power_label = QLabel("0.00 kW")
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.power_label.setStyleSheet(
            "font-family: Arial, sans-serif; font-size: 30px; font-weight: 800; color: #ffffff; border: none; background: transparent;"
        )

        self.current_label = QLabel("+0 A")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.current_label.setStyleSheet(
            "font-family: Arial, sans-serif; font-size: 20px; font-weight: 600; color: #9daec0; border: none; background: transparent;"
        )

        power_row = QFrame()
        power_row.setStyleSheet("background: transparent; border: none;")
        power_row_layout = QHBoxLayout(power_row)
        power_row_layout.setContentsMargins(0, 0, 0, 0)
        power_row_layout.setSpacing(8)
        power_row_layout.addWidget(self.power_label, 2)
        power_row_layout.addWidget(self.current_label, 1)

        bidirectional = QFrame()
        bidirectional.setStyleSheet("background: transparent; border: none;")
        bidi_layout = QVBoxLayout(bidirectional)
        bidi_layout.setContentsMargins(0, 0, 0, 0)
        bidi_layout.setSpacing(3)

        self.consumption_bar = QProgressBar()
        self.consumption_bar.setRange(0, 200)
        self.consumption_bar.setTextVisible(False)
        self.consumption_bar.setMinimumHeight(18)

        self.center_line = QFrame()
        self.center_line.setFixedHeight(2)
        self.center_line.setStyleSheet("background-color: #3A3A3A;")

        self.regen_bar = QProgressBar()
        self.regen_bar.setRange(0, 200)
        self.regen_bar.setTextVisible(False)
        self.regen_bar.setInvertedAppearance(True)
        self.regen_bar.setMinimumHeight(18)

        bidi_layout.addWidget(self.consumption_bar)
        bidi_layout.addWidget(self.center_line)
        bidi_layout.addWidget(self.regen_bar)

        layout.addWidget(battery_title)
        layout.addWidget(self.voltage_label)
        layout.addWidget(self.voltage_bar)
        layout.addSpacing(4)
        layout.addWidget(divider)
        layout.addSpacing(4)
        layout.addWidget(power_title)
        layout.addWidget(power_row)
        layout.addWidget(bidirectional)

        self._set_voltage_bar_color("#00FFFF")
        self._set_power_bar_colors("#FFAA00", "#00FFFF")

    def _set_voltage_bar_color(self, color: str) -> None:
        self.voltage_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #1e4a4a;
                border-radius: 9px;
                background-color: #0C1111;
                text-align: center;
                font-family: Arial, sans-serif;
                font-size: 16px;
                font-weight: 700;
                color: #E8F7FF;
            }}
            QProgressBar::chunk {{
                border-radius: 8px;
                background-color: {color};
            }}
            """
        )

    def _set_power_bar_colors(self, consumption_color: str, regen_color: str) -> None:
        self.consumption_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #2A2A2A;
                border-radius: 6px;
                background-color: #0D0D0D;
            }}
            QProgressBar::chunk {{
                background-color: {consumption_color};
                border-radius: 6px;
            }}
            """
        )
        self.regen_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #2A2A2A;
                border-radius: 6px;
                background-color: #0D0D0D;
            }}
            QProgressBar::chunk {{
                background-color: {regen_color};
                border-radius: 6px;
            }}
            """
        )

    def update_values(self, voltage: float, current: float) -> None:
        self._voltage = float(voltage)
        self._current = float(current)
        power_kw = (self._voltage * self._current) / 1000.0

        self.voltage_label.setText(f"{self._voltage:.1f} V")
        self.current_label.setText(f"{self._current:+.0f} A")
        self.power_label.setText(f"{power_kw:+.2f} kW")

        self.voltage_bar.setValue(int(round(self._voltage * 10)))
        self.voltage_bar.setFormat(f"{self._voltage:.1f} V")

        if self._voltage <= 46.0:
            voltage_color = "#FF3333"
        elif self._voltage <= 48.0:
            voltage_color = "#FFAA00"
        else:
            voltage_color = "#00FFFF"
        self.voltage_label.setStyleSheet(
            f"font-family: Arial, sans-serif; font-size: 44px; font-weight: 800; color: {voltage_color}; border: none; background: transparent;"
        )
        self._set_voltage_bar_color(voltage_color)

        magnitude = min(200, int(abs(self._current)))
        if self._current >= 0:
            self.consumption_bar.setValue(magnitude)
            self.regen_bar.setValue(0)
            self.current_label.setStyleSheet(
                "font-family: Arial, sans-serif; font-size: 20px; font-weight: 600; color: #FFAA00; border: none; background: transparent;"
            )
            self._set_power_bar_colors("#FFAA00", "#1A2C2C")
        else:
            self.consumption_bar.setValue(0)
            self.regen_bar.setValue(magnitude)
            self.current_label.setStyleSheet(
                "font-family: Arial, sans-serif; font-size: 20px; font-weight: 600; color: #00FFFF; border: none; background: transparent;"
            )
            self._set_power_bar_colors("#2C1E10", "#00FFFF")
