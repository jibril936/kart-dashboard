from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget


class PowerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._voltage = 0.0
        self._current = 0.0

        self.setStyleSheet(
            """
            QWidget {
                background-color: #1A1A1A;
                border: 1px solid #303030;
                border-radius: 14px;
            }
            QLabel {
                color: #F1F1F1;
                border: none;
                background: transparent;
            }
            QFrame {
                border: none;
                background: transparent;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.current_label = QLabel("+0.0 A")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_label.setStyleSheet("font-size: 38px; font-weight: 800; color: #D8D8D8;")

        self.power_label = QLabel("0 W")
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.power_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #AFAFAF;")

        bar_box = QFrame()
        bar_layout = QVBoxLayout(bar_box)
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(2)

        self.discharge_bar = QProgressBar()
        self.discharge_bar.setRange(0, 200)
        self.discharge_bar.setTextVisible(False)
        self.discharge_bar.setMinimumHeight(26)

        self.center_line = QFrame()
        self.center_line.setFixedHeight(2)
        self.center_line.setStyleSheet("background-color: #808080;")

        self.regen_bar = QProgressBar()
        self.regen_bar.setRange(0, 200)
        self.regen_bar.setTextVisible(False)
        self.regen_bar.setInvertedAppearance(True)
        self.regen_bar.setMinimumHeight(26)

        bar_layout.addWidget(self.discharge_bar)
        bar_layout.addWidget(self.center_line)
        bar_layout.addWidget(self.regen_bar)

        layout.addWidget(self.current_label)
        layout.addWidget(self.power_label)
        layout.addWidget(bar_box)

        self._set_bar_styles("#3A3A3A", "#3A3A3A")

    def _set_bar_styles(self, discharge_color: str, regen_color: str) -> None:
        self.discharge_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                background-color: #101010;
            }}
            QProgressBar::chunk {{
                background-color: {discharge_color};
                border-radius: 7px;
            }}
            """
        )
        self.regen_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                background-color: #101010;
            }}
            QProgressBar::chunk {{
                background-color: {regen_color};
                border-radius: 7px;
            }}
            """
        )

    def update_values(self, voltage: float, current: float) -> None:
        self._voltage = float(voltage)
        self._current = float(current)
        power = self._voltage * self._current

        self.current_label.setText(f"{self._current:+.0f} A")
        self.power_label.setText(f"{abs(power):.0f} W")

        if self._current >= 0.0:
            self.discharge_bar.setValue(min(200, int(abs(self._current))))
            self.regen_bar.setValue(0)
            self.current_label.setStyleSheet("font-size: 38px; font-weight: 800; color: #FFB347;")
            self._set_bar_styles("#FF8A00", "#2A2A2A")
        else:
            self.discharge_bar.setValue(0)
            self.regen_bar.setValue(min(200, int(abs(self._current))))
            self.current_label.setStyleSheet("font-size: 38px; font-weight: 800; color: #60D7FF;")
            self._set_bar_styles("#2A2A2A", "#00B8FF")
