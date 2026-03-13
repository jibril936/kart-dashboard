from qtpy.QtCore import QTimer, Qt, Slot
from qtpy.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.variator_i2c_service import VariatorI2CService
from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.battery_elements import CircularBatteryWidget
from src.ui.components.indicator_elements import IconAlertBar, SegmentedTempBar


class DriveModeSelector(QFrame):
    mode_selected = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode_selected = None
        self.setObjectName("Card")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(260)
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        self.buttons = {}
        for text, mode in (
            ("MANUAL", VariatorI2CService.MODE_MANUAL),
            ("N", VariatorI2CService.MODE_NEUTRAL),
            ("AUTO", VariatorI2CService.MODE_AUTO),
        ):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda checked, m=mode: self.set_mode(m))
            layout.addWidget(btn)
            self.buttons[mode] = btn

        self.set_mode(VariatorI2CService.MODE_NEUTRAL)

    def set_mode(self, mode: int):
        for m, btn in self.buttons.items():
            btn.setChecked(m == mode)
            if m == mode:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #101820;
                        color: #00f5ff;
                        border: 1px solid #00f5ff;
                        border-radius: 8px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                    """
                )
            else:
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #111111;
                        color: #8f8f8f;
                        border: 1px solid #303030;
                        border-radius: 8px;
                        font-weight: 600;
                        font-size: 11px;
                    }
                    """
                )
        self.mode_selected = mode

    def current_mode(self) -> int:
        return int(self.mode_selected)


class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.variator = getattr(store, "variator_service", None)
        self.charger_service = getattr(store, "charger_service", None)
        self.borne_service = getattr(store, "borne_service", None)

        self.v_temp = 0.0
        self.i_temp = 0.0

        self._speed_target = 0.0
        self._speed_display = 0.0
        self._i2c_brake = False
        self._reported_mode = VariatorI2CService.MODE_NEUTRAL
        self._fault_active = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self.setup_ui()
        self.connect_signals()

        self.speed_anim_timer = QTimer(self)
        self.speed_anim_timer.setInterval(30)
        self.speed_anim_timer.timeout.connect(self._animate_speed)
        self.speed_anim_timer.start()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.main_layout.setSpacing(0)

        self.alert_bar = IconAlertBar()
        self.main_layout.addWidget(self.alert_bar)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(10, 0, 10, 0)
        self.content_layout.setSpacing(0)

        # Gauche : vitesse
        self.left_col = QVBoxLayout()
        self.speed_gauge = AnalogGaugeWidget(
            minValue=0,
            maxValue=70,
            units="km/h",
            scalaCount=7,
        )
        self.speed_gauge.setFixedSize(260, 260)
        self.motor_temp_bar = SegmentedTempBar("MOTOR")

        self.left_col.addWidget(self.speed_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self.left_col.addWidget(self.motor_temp_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.left_col)

        # Centre : mode + SOC
        self.center_col = QVBoxLayout()
        self.center_col.setSpacing(8)

        self.mode_selector = DriveModeSelector()
        self.center_col.addWidget(self.mode_selector, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.energy_circle = CircularBatteryWidget()
        self.center_col.addWidget(self.energy_circle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.mode_status = QLabel("NEUTRAL")
        self.mode_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_status.setStyleSheet("color: #8f8f8f; font-size: 11px; font-weight: 700;")
        self.center_col.addWidget(self.mode_status)

        self.content_layout.addLayout(self.center_col)

        # Droite : puissance
        self.right_col = QVBoxLayout()
        self.power_gauge = AnalogGaugeWidget(
            minValue=-1000,
            maxValue=1000,
            units="W",
            scalaCount=4,
        )
        self.power_gauge.setFixedSize(260, 260)
        self.batt_temp_bar = SegmentedTempBar("BATT")

        self.right_col.addWidget(self.power_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self.right_col.addWidget(self.batt_temp_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.right_col)

        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addStretch(1)

    def connect_signals(self):
        self.mode_selector.set_mode(VariatorI2CService.MODE_NEUTRAL)
        if self.variator is not None:
            self.mode_selector.set_mode(self.variator.current_mode)
            self.mode_selector.mode_selected = self.variator.current_mode
            self._update_mode_text(self.variator.current_mode)
            self.mode_selector.buttons[VariatorI2CService.MODE_MANUAL].clicked.connect(
                lambda: self._send_mode(VariatorI2CService.MODE_MANUAL)
            )
            self.mode_selector.buttons[VariatorI2CService.MODE_NEUTRAL].clicked.connect(
                lambda: self._send_mode(VariatorI2CService.MODE_NEUTRAL)
            )
            self.mode_selector.buttons[VariatorI2CService.MODE_AUTO].clicked.connect(
                lambda: self._send_mode(VariatorI2CService.MODE_AUTO)
            )
        else:
            self._update_mode_text(VariatorI2CService.MODE_NEUTRAL)

        # BMS
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)
        self.store.soc_changed.connect(self.energy_circle.update_status)
        self.store.motor_temp_changed.connect(self.motor_temp_bar.set_value)
        self.store.batt_temp_changed.connect(self.batt_temp_bar.set_value)

        self.store.system_ready.connect(lambda s: self.alert_bar.update_alert("READY", s))
        self.store.is_limiting.connect(lambda s: self.alert_bar.update_alert("LIMIT", s))
        self.store.motor_temp_changed.connect(lambda v: self.alert_bar.update_alert("MOTT", v > 85))
        self.store.batt_temp_changed.connect(lambda v: self.alert_bar.update_alert("BATT", v > 55))
        self.store.soc_changed.connect(lambda v: self.alert_bar.update_alert("LOW-B", v < 15))

        if hasattr(self.store, "bms_status_bitmask"):
            self.store.bms_status_bitmask.connect(self._on_bitmask)

        # Variateur
        if self.variator is not None:
            self.variator.telemetry_received.connect(self._on_i2c_telemetry)
            self.variator.connection_changed.connect(self._on_i2c_connection)
            self.variator.command_changed.connect(self._on_command_changed)
        else:
            if hasattr(self.store, "speed_changed"):
                self.store.speed_changed.connect(self._on_speed_fallback)
            if hasattr(self.store, "brake_active"):
                self.store.brake_active.connect(lambda s: self.alert_bar.update_alert("BRAKE", s))

        # services préparés
        if self.charger_service is not None:
            self.charger_service.connection_changed.connect(
                lambda connected: self.alert_bar.update_alert("CHG", bool(connected))
            )
        if self.borne_service is not None:
            self.borne_service.connection_changed.connect(
                lambda connected: self.alert_bar.update_alert("BORN", bool(connected))
            )

    def _send_mode(self, mode: int):
        self.mode_selector.set_mode(mode)
        self._update_mode_text(mode)
        if self.variator is not None:
            self.variator.set_command(mode, self.variator.current_target)

    def _update_mode_text(self, mode: int):
        if mode == VariatorI2CService.MODE_MANUAL:
            text = "MANUAL"
        elif mode == VariatorI2CService.MODE_AUTO:
            text = "AUTO"
        else:
            text = "NEUTRAL"
        self.mode_status.setText(text)

    def _animate_speed(self):
        delta = self._speed_target - self._speed_display

        if abs(delta) < 0.2:
            self._speed_display = self._speed_target
        else:
            step = max(0.5, abs(delta) * 0.18)
            if delta > 0:
                self._speed_display += step
                if self._speed_display > self._speed_target:
                    self._speed_display = self._speed_target
            else:
                self._speed_display -= step
                if self._speed_display < self._speed_target:
                    self._speed_display = self._speed_target

        self.speed_gauge.setValue(self._speed_display)

    def _update_power_gauge(self):
        raw_w = self.v_temp * self.i_temp

        # accélération => positif
        # charge / regen => négatif
        display_w = -raw_w

        if display_w > 1000:
            display_w = 1000
        elif display_w < -1000:
            display_w = -1000

        self.power_gauge.setValue(display_w)
        self.alert_bar.update_alert("CHG", display_w < -50)

    @Slot(int, int)
    def _on_command_changed(self, mode: int, target: int):
        self.mode_selector.set_mode(mode)
        self._update_mode_text(mode)

    @Slot(float)
    def _on_current(self, amps: float):
        self.i_temp = float(amps)
        self._update_power_gauge()

    @Slot(float)
    def _on_voltage(self, volts: float):
        self.v_temp = float(volts)
        self._update_power_gauge()

    @Slot(float, int, bool)
    def _on_i2c_telemetry(self, vitesse_kmh: float, mode: int, frein: bool):
        print(f"[I2C TELEMETRY] vitesse={vitesse_kmh:.2f} mode={mode} frein={frein}")
        self._speed_target = max(0.0, float(vitesse_kmh))
        self._i2c_brake = bool(frein)
        self._reported_mode = int(mode)
        self.alert_bar.update_alert("BRAKE", self._i2c_brake)

    @Slot(bool)
    def _on_i2c_connection(self, connected: bool):
        self.alert_bar.update_alert("READY", bool(connected))

    @Slot(float)
    def _on_speed_fallback(self, speed: float):
        self._speed_target = max(0.0, float(speed))

    @Slot(int)
    def _on_bitmask(self, mask: int):
        fault = bool(int(mask) & 0xFFFF)
        self._fault_active = fault
        self.alert_bar.update_alert("FAULT", fault)