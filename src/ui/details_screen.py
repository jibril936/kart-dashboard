from __future__ import annotations

from src.core.store import StateStore
from src.core.types import DashboardState, TelemetrySample
from src.qt_compat import (
    ALIGN_LEFT,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)
from src.ui.components import AlertHistoryList

try:  # pragma: no cover - optional dependency
    import pyqtgraph as pg
except Exception:  # pragma: no cover
    pg = None


class DetailsScreen(QWidget):
    """TECH / Diagnostics view organized by subsystem clusters."""

    drive_requested = pyqtSignal()

    def __init__(self, store: StateStore) -> None:
        super().__init__()
        self._store = store
        self._nav_buttons: dict[str, QPushButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(12)

        header = QHBoxLayout()
        back_btn = QPushButton("Back to Drive")
        back_btn.setMinimumHeight(44)
        back_btn.clicked.connect(self.drive_requested.emit)

        title_wrap = QVBoxLayout()
        title = QLabel("TECH / DIAGNOSTICS")
        title.setProperty("clusterTitle", True)
        subtitle = QLabel("Vehicle telemetry, energy status, service & fault monitoring")
        subtitle.setProperty("kpi", True)
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)

        self._stats = QLabel("Stats pending")
        self._stats.setProperty("statusRow", True)

        header.addWidget(back_btn)
        header.addLayout(title_wrap, 1)
        header.addWidget(self._stats, 2)
        root.addLayout(header)

        nav = QHBoxLayout()
        for index, section in enumerate(("Vehicle", "Energy", "Service")):
            btn = QPushButton(section)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked, i=index: self._set_section(i))
            btn.setMinimumHeight(36)
            nav.addWidget(btn)
            self._nav_buttons[section] = btn
        nav.addStretch(1)
        root.addLayout(nav)

        body = QHBoxLayout()
        body.setSpacing(12)

        self._pages = QStackedWidget()
        self._pages.addWidget(self._build_vehicle_page())
        self._pages.addWidget(self._build_energy_page())
        self._pages.addWidget(self._build_service_page())
        body.addWidget(self._pages, 2)

        right = QVBoxLayout()
        self._plot = None
        self._curves = {}
        if pg is not None:
            self._plot = pg.PlotWidget(background="#070B14")
            self._plot.addLegend()
            self._plot.showGrid(x=True, y=True, alpha=0.3)
            self._curves = {
                "speed": self._plot.plot(pen=pg.mkPen("#52B9FF", width=2), name="speed"),
                "rpm": self._plot.plot(pen=pg.mkPen("#9D7DFF", width=2), name="rpm/100"),
                "voltage": self._plot.plot(pen=pg.mkPen("#64D38A", width=2), name="voltage"),
                "battery_temp": self._plot.plot(pen=pg.mkPen("#F6B64A", width=2), name="battery temp"),
            }
            right.addWidget(self._plot, 2)
        else:
            right.addWidget(QLabel("pyqtgraph unavailable"), 2)

        self._history = AlertHistoryList()
        right.addWidget(self._history, 1)
        body.addLayout(right, 1)

        root.addLayout(body, 1)
        self._set_section(0)

    def _build_vehicle_page(self) -> QWidget:
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self._veh_speed = self._make_card(layout, 0, 0, "Traction speed", "-- km/h")
        self._veh_rpm = self._make_card(layout, 0, 1, "Motor rpm", "-- rpm")
        self._veh_brake = self._make_card(layout, 0, 2, "Brake state", "--")
        self._veh_drive_mode = self._make_card(layout, 1, 0, "Drive mode", "classic")
        self._veh_control_mode = self._make_card(layout, 1, 1, "Control mode", "manual")
        self._veh_steer_angle = self._make_card(layout, 1, 2, "Steer angle", "-- deg")
        self._veh_pot = self._make_card(layout, 2, 0, "Potentiometer", "-- V")
        self._veh_steer_current = self._make_card(layout, 2, 1, "Steer current", "-- A")
        return panel

    def _build_energy_page(self) -> QWidget:
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self._ene_voltage = self._make_card(layout, 0, 0, "Battery voltage", "-- V")
        self._ene_current = self._make_card(layout, 0, 1, "Battery current", "-- A")
        self._ene_soc = self._make_card(layout, 0, 2, "SOC", "-- %")
        self._ene_power = self._make_card(layout, 1, 0, "Pack power", "-- kW")
        self._ene_charge_state = self._make_card(layout, 1, 1, "Charging", "off")
        self._ene_station_current = self._make_card(layout, 1, 2, "Station current", "-- A")
        self._ene_station_freq = self._make_card(layout, 2, 0, "Station frequency", "-- Hz")
        self._ene_batt_charge_current = self._make_card(layout, 2, 1, "Charge current", "-- A")
        return panel

    def _build_service_page(self) -> QWidget:
        panel = QWidget()
        layout = QGridLayout(panel)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        self._srv_motor_temp = self._make_card(layout, 0, 0, "Motor temp", "-- C")
        self._srv_controller_temp = self._make_card(layout, 0, 1, "Controller temp", "-- C")
        self._srv_battery_temp = self._make_card(layout, 0, 2, "Battery temp", "-- C")
        self._srv_source = self._make_card(layout, 1, 0, "Source state", "OK")
        self._srv_ultra_1 = self._make_card(layout, 1, 1, "Ultrasonic #1", "n/a")
        self._srv_ultra_2 = self._make_card(layout, 1, 2, "Ultrasonic #2", "n/a")
        self._srv_ultra_3 = self._make_card(layout, 2, 0, "Ultrasonic #3", "n/a")
        self._srv_stale = self._make_card(layout, 2, 1, "Data freshness", "-- ms")
        return panel

    def _make_card(self, layout: QGridLayout, row: int, col: int, title: str, initial_value: str) -> QLabel:
        frame = QFrame()
        frame.setProperty("tile", True)
        wrap = QVBoxLayout(frame)
        wrap.setContentsMargins(12, 10, 12, 10)
        wrap.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setProperty("kpi", True)
        title_lbl.setAlignment(ALIGN_LEFT)
        value_lbl = QLabel(initial_value)
        value_lbl.setProperty("statusRow", True)
        value_lbl.setAlignment(ALIGN_LEFT)

        wrap.addWidget(title_lbl)
        wrap.addWidget(value_lbl)
        layout.addWidget(frame, row, col)
        return value_lbl

    def _set_section(self, index: int) -> None:
        self._pages.setCurrentIndex(index)
        for i, section in enumerate(("Vehicle", "Energy", "Service")):
            self._nav_buttons[section].setChecked(i == index)

    def render(self, state: DashboardState) -> None:
        s = state.sample
        self._update_cluster_cards(s, state.stale_ms)

        speed_stats = self._store.stats_for("speed")
        volt_stats = self._store.stats_for("voltage")
        self._stats.setText(
            f"Speed avg {speed_stats.avg_value:.1f} km/h · min/max {speed_stats.min_value:.1f}/{speed_stats.max_value:.1f}"
            f"  |  Voltage avg {volt_stats.avg_value:.2f} V"
        )
        self._history.push_alerts(state.alert_history)

        if not self._curves:
            return
        series = self._store.latest_series()
        x = list(range(len(series["speed"])))
        self._curves["speed"].setData(x, series["speed"])
        self._curves["rpm"].setData(x, [v / 100 for v in series["rpm"]])
        self._curves["voltage"].setData(x, series["voltage"])
        self._curves["battery_temp"].setData(x, series["battery_temp"])

    def _update_cluster_cards(self, sample: TelemetrySample, stale_ms: int) -> None:
        # Vehicle / Traction
        self._veh_speed.setText(f"{sample.speed_kph:.1f} km/h")
        self._veh_rpm.setText(f"{sample.motor_rpm:.0f} rpm")
        self._veh_brake.setText("n/a")
        self._veh_drive_mode.setText("classic")
        self._veh_control_mode.setText("manual")
        self._veh_steer_angle.setText("n/a")
        self._veh_pot.setText("n/a")
        self._veh_steer_current.setText("n/a")

        # Energy / Charging
        self._ene_voltage.setText(f"{sample.pack_voltage_v:.2f} V")
        self._ene_current.setText(f"{sample.pack_current_a:.1f} A")
        self._ene_soc.setText(f"{sample.soc_percent:.1f} %")
        self._ene_power.setText(f"{sample.pack_power_kw:.2f} kW")
        self._ene_charge_state.setText("off")
        self._ene_station_current.setText("n/a")
        self._ene_station_freq.setText("n/a")
        self._ene_batt_charge_current.setText("n/a")

        # Service / Diagnostics
        self._srv_motor_temp.setText(f"{sample.motor_temp_c:.1f} C")
        self._srv_controller_temp.setText(f"{sample.controller_temp_c:.1f} C")
        self._srv_battery_temp.setText(f"{sample.battery_temp_c:.1f} C")
        self._srv_source.setText(sample.source_state.value)
        self._srv_ultra_1.setText("n/a")
        self._srv_ultra_2.setText("n/a")
        self._srv_ultra_3.setText("n/a")
        self._srv_stale.setText(f"{stale_ms} ms")
