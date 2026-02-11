from __future__ import annotations

from src.core.types import Alert, AlertLevel, AppConfig, DashboardState
from src.qt_compat import (
    ALIGN_CENTER,
    ALIGN_LEFT,
    ALIGN_RIGHT,
    FONT_BOLD,
    QFont,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)
from src.ui.components import ClusterTile, DialContainer, GaugeNeedle


class DriveScreen(QWidget):
    details_requested = pyqtSignal()

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 18)
        root.setSpacing(16)

        self._top_bar = QFrame()
        self._top_bar.setProperty("topBar", True)
        top_layout = QHBoxLayout(self._top_bar)
        top_layout.setContentsMargins(12, 8, 12, 8)
        top_layout.setSpacing(12)

        icon_row = QHBoxLayout()
        icon_row.setSpacing(6)
        self._warning_icons: list[QLabel] = []
        for symbol in ["!", "⚡", "🛞", "🔋", "⚙", "🌡", "🛑", "ⓘ"]:
            icon = QLabel(symbol)
            icon.setAlignment(ALIGN_CENTER)
            icon.setProperty("warningIcon", True)
            self._warning_icons.append(icon)
            icon_row.addWidget(icon)
        top_layout.addLayout(icon_row, 3)

        center = QVBoxLayout()
        center.setSpacing(0)
        self._mode_title = QLabel("DRIVE · NORMAL")
        self._mode_title.setAlignment(ALIGN_CENTER)
        self._mode_title.setProperty("clusterTitle", True)
        self._scenario = QLabel(f"Scenario: {config.demo_scenario.upper()}")
        self._scenario.setAlignment(ALIGN_CENTER)
        self._scenario.setProperty("kpi", True)
        center.addWidget(self._mode_title)
        center.addWidget(self._scenario)
        top_layout.addLayout(center, 4)

        right = QHBoxLayout()
        right.setSpacing(10)
        self._clock_label = QLabel("--:--")
        self._clock_label.setAlignment(ALIGN_RIGHT | ALIGN_CENTER)
        self._clock_label.setProperty("clock", True)
        self._source_label = QLabel("DEMO" if config.source == "demo" else config.source.upper())
        self._source_label.setProperty("kpi", True)
        right.addWidget(self._clock_label)
        right.addWidget(self._source_label)
        top_layout.addLayout(right, 2)

        root.addWidget(self._top_bar, 1)

        main_cluster = QHBoxLayout()
        main_cluster.setSpacing(16)

        speed_dial = DialContainer("SPEED")
        speed_body = speed_dial.body_layout()
        speed_body.addStretch(1)
        self._speed = QLabel("0")
        self._speed.setFont(QFont("Inter", 96, FONT_BOLD))
        self._speed.setAlignment(ALIGN_CENTER)
        self._speed.setProperty("dialValue", True)
        self._unit = QLabel("km/h")
        self._unit.setAlignment(ALIGN_CENTER)
        self._unit.setProperty("kpi", True)
        speed_body.addWidget(self._speed)
        speed_body.addWidget(self._unit)
        speed_body.addStretch(1)

        rpm_dial = DialContainer("RPM")
        rpm_body = rpm_dial.body_layout()
        self._rpm_gauge = GaugeNeedle(0, config.rpm_max, config.rpm_redline)
        rpm_body.addWidget(self._rpm_gauge)

        center_panel = QFrame()
        center_panel.setProperty("centerPanel", True)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(16, 14, 16, 14)
        center_layout.setSpacing(8)
        panel_title = QLabel("EV STATUS")
        panel_title.setProperty("clusterTitle", True)
        panel_title.setAlignment(ALIGN_LEFT)
        center_layout.addWidget(panel_title)

        self._status_battery = QLabel("Battery: -- %")
        self._status_voltage = QLabel("Voltage: -- V")
        self._status_range = QLabel("Range: -- km")
        for row in [self._status_battery, self._status_voltage, self._status_range]:
            row.setProperty("statusRow", True)
            center_layout.addWidget(row)

        self._alert_line = QLabel("Status: All systems nominal")
        self._alert_line.setProperty("alertLine", "info")
        self._alert_line.setWordWrap(False)
        center_layout.addWidget(self._alert_line)
        center_layout.addStretch(1)

        main_cluster.addWidget(speed_dial, 3)
        main_cluster.addWidget(center_panel, 2)
        main_cluster.addWidget(rpm_dial, 3)
        root.addLayout(main_cluster, 6)

        bottom_wrap = QVBoxLayout()
        bottom_wrap.setSpacing(10)
        bottom_strip = QHBoxLayout()
        bottom_strip.setSpacing(12)

        self._battery_tile = ClusterTile("Battery", "%")
        self._motor_temp_tile = ClusterTile("Motor Temp", "°C")
        self._controller_temp_tile = ClusterTile("Controller Temp", "°C")
        self._battery_temp_tile = ClusterTile("Battery Temp", "°C")

        for tile in [self._battery_tile, self._motor_temp_tile, self._controller_temp_tile, self._battery_temp_tile]:
            bottom_strip.addWidget(tile)

        bottom_wrap.addLayout(bottom_strip)

        controls = QHBoxLayout()
        controls.addStretch(1)
        btn = QPushButton("TECH / Diagnostics")
        btn.setProperty("secondary", True)
        btn.setMinimumHeight(38)
        btn.clicked.connect(self.details_requested.emit)
        controls.addWidget(btn)
        bottom_wrap.addLayout(controls)

        root.addLayout(bottom_wrap, 2)

    def render(self, state: DashboardState) -> None:
        s = state.sample
        self._speed.setText(f"{s.speed_kph:.0f}")
        self._rpm_gauge.set_value(s.motor_rpm)

        self._status_battery.setText(f"Battery: {s.soc_percent:.0f}%")
        self._status_voltage.setText(f"Voltage: {s.pack_voltage_v:.1f} V")
        self._status_range.setText(f"Range: {s.estimated_range_km:.0f} km")

        self._battery_tile.set_value(f"{s.soc_percent:.0f}")
        self._motor_temp_tile.set_value(f"{s.motor_temp_c:.1f}")
        self._controller_temp_tile.set_value(f"{s.controller_temp_c:.1f}")
        self._battery_temp_tile.set_value(f"{s.battery_temp_c:.1f}")

        self._clock_label.setText(s.timestamp.strftime("%H:%M"))
        self._render_alerts(state.active_alerts)

    def _render_alerts(self, alerts: list[Alert]) -> None:
        for icon in self._warning_icons:
            icon.setProperty("warningActive", False)
            icon.style().unpolish(icon)
            icon.style().polish(icon)

        if not alerts:
            self._alert_line.setText("Status: All systems nominal")
            self._alert_line.setProperty("alertLine", "info")
            self._apply_alert_style()
            return

        top = sorted(alerts, key=lambda a: [AlertLevel.INFO, AlertLevel.WARNING, AlertLevel.CRITICAL].index(a.level))[-1]
        self._alert_line.setText(f"Alert: {top.message}")
        if top.level == AlertLevel.CRITICAL:
            self._alert_line.setProperty("alertLine", "critical")
            active_count = 3
        elif top.level == AlertLevel.WARNING:
            self._alert_line.setProperty("alertLine", "warning")
            active_count = 2
        else:
            self._alert_line.setProperty("alertLine", "info")
            active_count = 1
        self._apply_alert_style()

        for icon in self._warning_icons[:active_count]:
            icon.setProperty("warningActive", True)
            icon.style().unpolish(icon)
            icon.style().polish(icon)

    def _apply_alert_style(self) -> None:
        self._alert_line.style().unpolish(self._alert_line)
        self._alert_line.style().polish(self._alert_line)
