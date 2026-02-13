from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from src.core.state import VehicleTechState
from src.ui.components import BottomBarStrip, CenterPanel, CircularGauge, DriveTopIndicators

MAX_SPEED_KMH = 60
MAX_RPM = 60
SPEED_MAJOR_TICK = 10
RPM_MAJOR_TICK = 10


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
        self.top_indicators = DriveTopIndicators()
        self.tech_button = QPushButton("TECH")
        self.tech_button.setObjectName("NavButton")
        self.tech_button.clicked.connect(self.tech_requested.emit)
        self.top_bar.addWidget(self.top_indicators)
        self.top_bar.addWidget(self.tech_button)
        self.root.addLayout(self.top_bar)

        self.middle = QHBoxLayout()
        self.middle.setSpacing(16)

        self.speed_gauge = CircularGauge(
            "SPEED",
            "km/h",
            0,
            MAX_SPEED_KMH,
            major_tick_step=SPEED_MAJOR_TICK,
            minor_ticks_per_major=1,
            label_formatter=lambda v: f"{int(v):d}",
            side="right",
        )
        self.center_panel = CenterPanel()
        self.rpm_gauge = CircularGauge(
            "RPM",
            "rpm",
            0,
            MAX_RPM,
            major_tick_step=RPM_MAJOR_TICK,
            minor_ticks_per_major=1,
            label_formatter=lambda v: f"{int(v):d}",
            side="left",
        )

        self.middle.addWidget(self.speed_gauge, 1)
        self.middle.addWidget(self.center_panel, 1)
        self.middle.addWidget(self.rpm_gauge, 1)
        self.root.addLayout(self.middle, 1)

        self.bottom_bar = BottomBarStrip()
        self.root.addWidget(self.bottom_bar)
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        compact = self.width() < 1100 or self.height() < 650
        auto_scale = 0.84 if compact else 1.0
        self._effective_scale = max(0.75, min(1.2, self._base_ui_scale * auto_scale))
        s = self._effective_scale

        self.root.setContentsMargins(int(18 * s), int(14 * s), int(18 * s), int(12 * s))
        self.root.setSpacing(int(8 * s))
        self.middle.setSpacing(int((10 if compact else 16) * s))
        self.top_bar.setSpacing(int((6 if compact else 8) * s))

        self.center_panel.set_compact_mode(compact, s)
        self.center_panel.kart_widget.set_compact_mode(compact, s)
        self.speed_gauge.set_compact_mode(compact, s)
        self.rpm_gauge.set_compact_mode(compact, s)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_responsive_layout()

    def render(self, state: VehicleTechState) -> None:
        speed = state.speed_kmh
        rpm = state.rpm
        steering_angle = state.steering_angle_deg
        charging = state.charging_state
        battery_v = state.battery_voltage_V
        brake = state.brake_state
        motor_temp = state.motor_temp_C

        self.speed_gauge.setVisible(speed is not None)
        if speed is not None:
            self.speed_gauge.set_value(float(speed))

        self.rpm_gauge.setVisible(rpm is not None)
        if rpm is not None:
            self.rpm_gauge.set_value(float(rpm))

        drive_mode = getattr(state, "drive_mode", None)
        control_mode = getattr(state, "control_mode", None)

        self.center_panel.set_state(
            float(steering_angle) if steering_angle is not None else None,
            drive_mode=drive_mode,
            control_mode=control_mode,
            charging_state=charging,
            gear=None,
        )

        brake_active = None if brake is None else brake >= 0.5
        self.top_indicators.set_state(
            battery_voltage_v=battery_v,
            motor_temp_c=motor_temp,
            is_charging=charging,
            brake_active=brake_active,
        )

        self.bottom_bar.set_values(
            battery_voltage=battery_v,
            battery_soc_percent=None,
            motor_temp_c=motor_temp,
        )
