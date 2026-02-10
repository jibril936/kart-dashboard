from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.models.telemetry import SourceState, Telemetry


class DriveView(QWidget):
    diagnostics_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        top = QHBoxLayout()
        self._state = QLabel("SOURCE: —")
        self._state.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        diag_button = QPushButton("⚙️ Diagnostic")
        diag_button.setMinimumHeight(56)
        diag_button.setStyleSheet("font-size: 22px; padding: 8px 16px;")
        diag_button.clicked.connect(self.diagnostics_requested.emit)

        top.addWidget(self._state)
        top.addStretch(1)
        top.addWidget(diag_button)

        self._speed = QLabel("—")
        self._speed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._speed.setFont(QFont("Arial", 120, QFont.Weight.Bold))

        self._soc = QLabel("SOC —")
        self._soc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._soc.setFont(QFont("Arial", 54, QFont.Weight.Bold))

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)
        self._power = self._metric("Power")
        self._current = self._metric("Current")
        self._temps = self._metric("Temps")
        self._alerts = self._metric("Alertes")
        grid.addWidget(self._power[0], 0, 0)
        grid.addWidget(self._current[0], 0, 1)
        grid.addWidget(self._temps[0], 1, 0)
        grid.addWidget(self._alerts[0], 1, 1)

        root.addLayout(top)
        root.addWidget(self._speed)
        root.addWidget(self._soc)
        root.addLayout(grid)

    def _metric(self, title: str) -> tuple[QFrame, QLabel]:
        box = QFrame()
        box.setStyleSheet("QFrame { background:#111827; border-radius: 12px; padding: 10px; }")
        layout = QVBoxLayout(box)
        t = QLabel(title)
        t.setStyleSheet("color:#9CA3AF; font-size:18px;")
        v = QLabel("—")
        v.setWordWrap(True)
        v.setStyleSheet("font-size:34px; font-weight:700;")
        layout.addWidget(t)
        layout.addWidget(v)
        return box, v

    def update_telemetry(self, telemetry: Telemetry) -> None:
        self._speed.setText(Telemetry.format_value(telemetry.speed_kph, "km/h", 0))
        self._soc.setText(f"SOC {Telemetry.format_value(telemetry.soc_percent, '%', 0)}")
        self._power[1].setText(Telemetry.format_value(telemetry.pack_power_kw, "kW", 1))
        self._current[1].setText(Telemetry.format_value(telemetry.pack_current_a, "A", 1))
        self._temps[1].setText(
            "M "
            + Telemetry.format_value(telemetry.motor_temp_c, "°C", 1)
            + "  | I "
            + Telemetry.format_value(telemetry.inverter_temp_c, "°C", 1)
            + "  | B "
            + Telemetry.format_value(telemetry.battery_temp_c, "°C", 1)
        )
        self._alerts[1].setText("\n".join(telemetry.alerts) if telemetry.alerts else "Aucune")

        color = {SourceState.OK: "#10B981", SourceState.TIMEOUT: "#F59E0B", SourceState.ERROR: "#EF4444"}[telemetry.source_state]
        self._state.setText(f"SOURCE: {telemetry.source_state.value}")
        self._state.setStyleSheet(f"color:{color};")
