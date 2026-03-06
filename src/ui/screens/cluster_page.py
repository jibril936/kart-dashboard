from qtpy.QtCore import QTimer, Qt, Slot
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.battery_elements import CircularBatteryWidget
from src.ui.components.indicator_elements import IconAlertBar, SegmentedTempBar


class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.variator = getattr(store, "variator_service", None)

        self.v_temp = 0.0
        self.i_temp = 0.0

        self._speed_target = 0.0
        self._speed_display = 0.0
        self._i2c_brake = False

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

        # Centre : SOC
        self.energy_circle = CircularBatteryWidget()
        self.content_layout.addWidget(self.energy_circle, alignment=Qt.AlignmentFlag.AlignCenter)

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
        # BMS
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)

        self.store.soc_changed.connect(self.energy_circle.update_status)
        self.store.motor_temp_changed.connect(self.motor_temp_bar.set_value)
        self.store.batt_temp_changed.connect(self.batt_temp_bar.set_value)

        self.store.system_ready.connect(lambda s: self.alert_bar.update_alert("READY", s))
        self.store.is_limiting.connect(lambda s: self.alert_bar.update_alert("LIMIT", s))

        self.store.motor_temp_changed.connect(lambda v: self.alert_bar.update_alert("MOT_TEMP", v > 85))
        self.store.batt_temp_changed.connect(lambda v: self.alert_bar.update_alert("BATT_TEMP", v > 55))
        self.store.soc_changed.connect(lambda v: self.alert_bar.update_alert("LOW_BATT", v < 15))

        # Variateur I2C
        if self.variator is not None:
            self.variator.telemetry_received.connect(self._on_i2c_telemetry)
            self.variator.connection_changed.connect(self._on_i2c_connection)
        else:
            if hasattr(self.store, "speed_changed"):
                self.store.speed_changed.connect(self._on_speed_fallback)
            if hasattr(self.store, "brake_active"):
                self.store.brake_active.connect(lambda s: self.alert_bar.update_alert("BRAKE", s))

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
        self._speed_target = max(0.0, float(vitesse_kmh))
        self._i2c_brake = bool(frein)
        self.alert_bar.update_alert("BRAKE", self._i2c_brake)

    @Slot(bool)
    def _on_i2c_connection(self, connected: bool):
        self.alert_bar.update_alert("READY", bool(connected))

    @Slot(float)
    def _on_speed_fallback(self, speed: float):
        self._speed_target = max(0.0, float(speed))