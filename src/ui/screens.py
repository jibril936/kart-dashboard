from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from src.core.model import KartDataModel
from src.ui.components.speed_gauge_oem import SpeedGaugeOEM


class DrivingScreen(QWidget):
    def __init__(self, model: KartDataModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = model
        self.setStyleSheet("background-color: #121212; border: 2px solid #AA2222;")

        layout = QGridLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        battery_panel = self._make_placeholder_panel("BATTERY")
        power_panel = self._make_placeholder_panel("POWER")
        time_panel = self._make_placeholder_panel("TEMPS")

        self.speed_gauge = SpeedGaugeOEM(
            title="SPEED",
            unit="km/h",
            min_value=0,
            max_value=120,
            major_tick_step=10,
            minor_ticks_per_major=1,
        )

        layout.addWidget(battery_panel, 0, 0)
        layout.addWidget(self.speed_gauge, 0, 1)
        layout.addWidget(power_panel, 0, 2)
        layout.addWidget(time_panel, 1, 0, 1, 3)

        layout.setRowStretch(0, 4)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)

        speed_signal = getattr(self.model, "speedChanged", None)
        if speed_signal is None:
            speed_signal = self.model.speed_changed
        speed_signal.connect(self.update_gauge)
        self.update_gauge(self.model.speed)

    def _make_placeholder_panel(self, title: str) -> QFrame:
        panel = QFrame(self)
        panel.setStyleSheet(
            """
            QFrame {
                background-color: #1E1E1E;
                border: 1px solid #2D2D2D;
                border-radius: 16px;
            }
            QLabel {
                color: #EDEDED;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 1px;
            }
            """
        )

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(label)
        return panel

    def update_gauge(self, value: float) -> None:
        self.speed_gauge.set_value(value)


class TechScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #091530;")

        layout = QGridLayout(self)
        label = QLabel("TECH")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)


class GraphsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

        layout = QGridLayout(self)
        label = QLabel("GRAPHS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)
