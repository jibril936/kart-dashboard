from __future__ import annotations

from collections import deque

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.models.telemetry import Telemetry


class DiagView(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, refresh_hz: float) -> None:
        super().__init__()
        self._seconds_per_sample = 1.0 / refresh_hz if refresh_hz > 0 else 0.1
        self._sample_index = 0
        self._speed_history = deque(maxlen=180)
        self._power_history = deque(maxlen=180)
        self._x_history = deque(maxlen=180)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        top = QHBoxLayout()
        back = QPushButton("⬅ Back")
        back.setMinimumHeight(52)
        back.setStyleSheet("font-size: 22px; padding: 8px 16px;")
        back.clicked.connect(self.back_requested.emit)
        top.addWidget(back)
        top.addStretch(1)

        self._raw_values = {
            "Voltage": QLabel("—"),
            "Current": QLabel("—"),
            "Power": QLabel("—"),
            "RPM": QLabel("—"),
            "Throttle": QLabel("—"),
            "Brake": QLabel("—"),
            "Source": QLabel("—"),
        }

        grid = QGridLayout()
        for idx, (name, label) in enumerate(self._raw_values.items()):
            title = QLabel(name)
            title.setStyleSheet("color:#9CA3AF; font-size:16px;")
            label.setStyleSheet("font-size:30px; font-weight:700;")
            grid.addWidget(title, idx, 0)
            grid.addWidget(label, idx, 1)

        self._plot = pg.PlotWidget(background="#0b0f1a")
        self._plot.setLabel("left", "Value")
        self._plot.setLabel("bottom", "Time", units="s")
        self._plot.showGrid(x=True, y=True, alpha=0.25)
        self._speed_curve = self._plot.plot(pen=pg.mkPen("#60A5FA", width=3), name="speed")
        self._power_curve = self._plot.plot(pen=pg.mkPen("#F97316", width=2), name="power")

        root.addLayout(top)
        root.addLayout(grid)
        root.addWidget(self._plot, stretch=1)

    def update_telemetry(self, telemetry: Telemetry) -> None:
        self._raw_values["Voltage"].setText(Telemetry.format_value(telemetry.pack_voltage_v, "V", 2))
        self._raw_values["Current"].setText(Telemetry.format_value(telemetry.pack_current_a, "A", 1))
        self._raw_values["Power"].setText(Telemetry.format_value(telemetry.pack_power_kw, "kW", 2))
        self._raw_values["RPM"].setText(Telemetry.format_value(telemetry.motor_rpm, "rpm", 0))
        self._raw_values["Throttle"].setText(Telemetry.format_value(telemetry.throttle_percent, "%", 0))
        self._raw_values["Brake"].setText(Telemetry.format_value(telemetry.brake_percent, "%", 0))
        self._raw_values["Source"].setText(telemetry.source_state.value)

        if telemetry.speed_kph is not None and telemetry.pack_power_kw is not None:
            self._sample_index += 1
            self._x_history.append(self._sample_index * self._seconds_per_sample)
            self._speed_history.append(telemetry.speed_kph)
            self._power_history.append(telemetry.pack_power_kw * 10)

        self._speed_curve.setData(list(self._x_history), list(self._speed_history))
        self._power_curve.setData(list(self._x_history), list(self._power_history))
