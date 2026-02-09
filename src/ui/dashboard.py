from __future__ import annotations

from collections import deque
from typing import Deque

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QGridLayout,
)
import pyqtgraph as pg

from src.models.telemetry import Telemetry


class DashboardWindow(QMainWindow):
    def __init__(self, refresh_hz: float) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard")
        self.setStyleSheet("background-color: #0b0f1a; color: #f5f5f5;")
        self._seconds_per_sample = 1.0 / refresh_hz if refresh_hz > 0 else 0.1

        self._speed_label = QLabel("—")
        self._rpm_label = QLabel("—")
        self._temp_label = QLabel("—")
        self._battery_label = QLabel("—")
        self._status_label = QLabel("—")

        for label in [self._speed_label, self._rpm_label, self._temp_label, self._battery_label]:
            label.setFont(QFont("Arial", 32, QFont.Weight.Bold))

        self._status_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._rpm_bar = QProgressBar()
        self._rpm_bar.setRange(0, 8000)
        self._rpm_bar.setFormat("%v RPM")
        self._rpm_bar.setTextVisible(True)
        self._rpm_bar.setStyleSheet("QProgressBar { height: 24px; } QProgressBar::chunk { background-color: #3c8dbc; }")

        self._battery_bar = QProgressBar()
        self._battery_bar.setRange(0, 14)
        self._battery_bar.setFormat("%v V")
        self._battery_bar.setTextVisible(True)
        self._battery_bar.setStyleSheet("QProgressBar { height: 24px; } QProgressBar::chunk { background-color: #00c851; }")

        self._rpm_history: Deque[float] = deque(maxlen=120)
        self._time_history: Deque[float] = deque(maxlen=120)
        self._sample_index = 0

        self._plot = pg.PlotWidget(background="#111827")
        self._plot.setYRange(0, 8000)
        self._plot.setLabel("left", "RPM")
        self._plot.setLabel("bottom", "Temps", units="s")
        self._plot.showGrid(x=True, y=True, alpha=0.2)
        self._plot_curve = self._plot.plot(pen=pg.mkPen("#f97316", width=3))

        main = QWidget()
        layout = QVBoxLayout(main)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        metrics_layout = QGridLayout()
        metrics_layout.setHorizontalSpacing(32)
        metrics_layout.setVerticalSpacing(18)
        metrics_layout.addWidget(self._metric_block("Vitesse", self._speed_label), 0, 0)
        metrics_layout.addWidget(self._metric_block("RPM", self._rpm_label), 0, 1)
        metrics_layout.addWidget(self._metric_block("Température", self._temp_label), 1, 0)
        metrics_layout.addWidget(self._metric_block("Batterie", self._battery_label), 1, 1)

        layout.addLayout(metrics_layout)
        layout.addWidget(self._rpm_bar)
        layout.addWidget(self._battery_bar)
        layout.addWidget(self._status_label)
        layout.addWidget(self._plot, stretch=1)

        self.setCentralWidget(main)

    def _metric_block(self, title: str, value_label: QLabel) -> QWidget:
        wrapper = QWidget()
        block_layout = QVBoxLayout(wrapper)
        block_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Medium))
        title_label.setStyleSheet("color: #9ca3af;")

        block_layout.addWidget(title_label)
        block_layout.addWidget(value_label)
        return wrapper

    def update_telemetry(self, telemetry: Telemetry) -> None:
        self._speed_label.setText(telemetry.formatted(telemetry.speed_kph, "km/h"))
        self._rpm_label.setText(telemetry.formatted(telemetry.rpm, "rpm", precision=0))
        self._temp_label.setText(telemetry.formatted(telemetry.temp_c, "°C"))
        self._battery_label.setText(telemetry.formatted(telemetry.battery_v, "V"))

        if telemetry.rpm is not None:
            self._rpm_bar.setValue(int(telemetry.rpm))
        else:
            self._rpm_bar.reset()

        if telemetry.battery_v is not None:
            self._battery_bar.setValue(int(telemetry.battery_v))
        else:
            self._battery_bar.reset()

        status_text = telemetry.status
        status_color = "#00c851" if telemetry.status == "OK" else "#ff4444"
        self._status_label.setText(f"État: {status_text}")
        self._status_label.setStyleSheet(f"color: {status_color};")

        if telemetry.rpm is not None:
            self._sample_index += 1
            self._time_history.append(self._sample_index * self._seconds_per_sample)
            self._rpm_history.append(telemetry.rpm)
            self._plot_curve.setData(list(self._time_history), list(self._rpm_history))
        else:
            self._plot_curve.setData([], [])
