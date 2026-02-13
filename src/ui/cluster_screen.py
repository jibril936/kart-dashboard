from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import BottomBarStrip, CenterPanel, CircularGauge

SPEED_MIN_KMH = 0
SPEED_MAX_KMH = 60
SPEED_MAJOR_TICK = 10
MIN_GAUGE_CENTER_SPACING = 24


class ClusterScreen(QWidget):
    tech_requested = pyqtSignal()

    def __init__(self, ui_scale: float = 1.0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_ui_scale = ui_scale
        self._effective_scale = ui_scale

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(18, 14, 18, 12)
        self.root.setSpacing(8)

        self.top_bar = QHBoxLayout()
        self.top_bar.setSpacing(8)

        self.tech_button = QPushButton("TECH")
        self.tech_button.setObjectName("NavButton")
        self.tech_button.clicked.connect(self.tech_requested.emit)

        self.top_bar.addStretch(1)
        self.top_bar.addWidget(self.tech_button)
        self.root.addLayout(self.top_bar)

        self.middle = QHBoxLayout()
        self.middle.setSpacing(16)

        self.speed_gauge = CircularGauge(
            "SPEED",
            "km/h",
            SPEED_MIN_KMH,
            SPEED_MAX_KMH,
            major_tick_step=SPEED_MAJOR_TICK,
            minor_ticks_per_major=1,
            label_formatter=lambda v: f"{int(v):d}",
            side="right",
        )
        self.center_panel = CenterPanel()

        self.middle.addWidget(self.speed_gauge, 1)
        self.middle.addWidget(self.center_panel, 2)
        self.root.addLayout(self.middle, 1)

        self.bottom_bar = BottomBarStrip()
        self.root.addWidget(self.bottom_bar)
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        compact = self.width() < 1100 or self.height() < 650
        auto_scale = 0.84 if compact else 1.0
        self._effective_scale = max(0.75, min(1.2, self._base_ui_scale * auto_scale))
        s = self._effective_scale

        horizontal_margin = (12 if compact else 18) * s
        self.root.setContentsMargins(int(horizontal_margin), int(14 * s), int(horizontal_margin), int(12 * s))
        self.root.setSpacing(int(8 * s))
        spacing = max(int(MIN_GAUGE_CENTER_SPACING * s), int((24 if compact else 30) * s))
        self.middle.setSpacing(spacing)
        self.top_bar.setSpacing(int((6 if compact else 8) * s))

        self.center_panel.set_compact_mode(compact, s)
        self.center_panel.kart_widget.set_compact_mode(compact, s)
        self.speed_gauge.set_compact_mode(compact, s)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_responsive_layout()

    def render(self, state: VehicleTechState) -> None:
        speed = state.speed_kmh
        steering_angle = state.steering_angle_deg
        charging = state.charging_state
        battery_v = state.battery_voltage_V
        brake = state.brake_state
        motor_temp = state.motor_temp_C

        self.speed_gauge.setVisible(speed is not None)
        if speed is not None:
            self.speed_gauge.set_value(float(speed))

        drive_mode = getattr(state, "drive_mode", None)
        control_mode = getattr(state, "control_mode", None)

        self.center_panel.set_state(
            float(steering_angle) if steering_angle is not None else None,
            drive_mode=drive_mode,
            control_mode=control_mode,
            charging_state=charging,
            gear=None,
        )

        _ = brake

        self.bottom_bar.set_values(
            battery_voltage=battery_v,
            battery_soc_percent=None,
            motor_temp_c=motor_temp,
        )
