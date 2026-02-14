from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget


class BatteryWidget(QWidget):
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
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.voltage_label = QLabel("0.0 V")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltage_label.setStyleSheet("font-size: 40px; font-weight: 800; color: #55FF7A;")

        self.current_label = QLabel("+0.0 A")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #CFCFCF;")

        self.level_bar = QProgressBar()
        self.level_bar.setRange(440, 540)
        self.level_bar.setTextVisible(True)
        self.level_bar.setMinimumHeight(36)
        self.level_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                background-color: #111111;
                text-align: center;
                color: #F7F7F7;
                font-size: 20px;
                font-weight: 700;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background-color: #35D46C;
            }
            """
        )

        layout.addWidget(self.voltage_label)
        layout.addWidget(self.current_label)
        layout.addWidget(self.level_bar)

    def update_values(self, voltage: float, current: float) -> None:
        self._voltage = float(voltage)
        self._current = float(current)

        self.voltage_label.setText(f"{self._voltage:.1f} V")
        self.current_label.setText(f"{self._current:+.1f} A")
        self.level_bar.setValue(int(round(self._voltage * 10)))
        self.level_bar.setFormat(f"{self._voltage:.1f} V")

        if self._voltage <= 46.0:
            color = "#FF3B30"
        elif self._voltage <= 48.0:
            color = "#FF9F0A"
        else:
            color = "#32D74B"

        self.voltage_label.setStyleSheet(f"font-size: 40px; font-weight: 800; color: {color};")
        self.level_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 2px solid #3A3A3A;
                border-radius: 10px;
                background-color: #111111;
                text-align: center;
                color: #F7F7F7;
                font-size: 20px;
                font-weight: 700;
            }}
            QProgressBar::chunk {{
                border-radius: 8px;
                background-color: {color};
            }}
            """
        )
