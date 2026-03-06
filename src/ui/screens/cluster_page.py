from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from src.core.variator_i2c_service import VariatorI2CService
from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.battery_elements import CircularBatteryWidget
from src.ui.components.indicator_elements import IconAlertBar, SegmentedTempBar


class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self.v_temp = 0.0
        self.i_temp = 0.0

        self.i2c_speed = 0.0
        self.i2c_mode = 0
        self.i2c_brake = False
        self.i2c_connected = False

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self.variator = VariatorI2CService(parent=self)

        self.setup_ui()
        self.connect_signals()

        self.variator.start()
        self._push_slider_command()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 6, 0, 0)
        self.main_layout.setSpacing(4)

        self._build_top_command_bar()

        self.alert_bar = IconAlertBar()
        self.main_layout.addWidget(self.alert_bar)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(6, 0, 6, 0)
        self.content_layout.setSpacing(4)

        # gauche
        self.left_col = QVBoxLayout()
        self.left_col.setSpacing(4)

        self.speed_gauge = AnalogGaugeWidget(
            minValue=0,
            maxValue=70,
            units="km/h",
            scalaCount=7,
        )
        self.speed_gauge.setFixedSize(235, 235)

        self.motor_temp_bar = SegmentedTempBar("MOTOR")

        self.left_col.addWidget(self.speed_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self.left_col.addWidget(self.motor_temp_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.left_col, 1)

        # centre
        self.energy_circle = CircularBatteryWidget()
        self.content_layout.addWidget(self.energy_circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # droite
        self.right_col = QVBoxLayout()
        self.right_col.setSpacing(4)

        self.power_gauge = AnalogGaugeWidget(
            minValue=-1000,
            maxValue=1000,
            units="W",
            scalaCount=4,
        )
        self.power_gauge.setFixedSize(235, 235)

        self.batt_temp_bar = SegmentedTempBar("BATT")

        self.right_col.addWidget(self.power_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self.right_col.addWidget(self.batt_temp_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.right_col, 1)

        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addStretch(1)

    def _build_top_command_bar(self):
        card = QFrame(self)
        card.setObjectName("Card")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title = QLabel("VARIATEUR I2C")
        title.setObjectName("CardTitle")
        title_row.addWidget(title)

        title_row.addStretch(1)

        self.lbl_i2c_link = QLabel("OFFLINE")
        self.lbl_i2c_link.setObjectName("Value")
        title_row.addWidget(self.lbl_i2c_link)

        layout.addLayout(title_row)

        slider_row = QHBoxLayout()
        slider_row.setSpacing(10)

        self.lbl_target = QLabel("Target 0 km/h")
        self.lbl_target.setObjectName("Value")
        self.lbl_target.setMinimumWidth(130)
        slider_row.addWidget(self.lbl_target)

        self.slider_target = QSlider(Qt.Orientation.Horizontal)
        self.slider_target.setRange(0, 60)
        self.slider_target.setValue(0)
        self.slider_target.setTracking(True)
        self.slider_target.valueChanged.connect(self._on_slider_changed)
        slider_row.addWidget(self.slider_target, 1)

        self.lbl_mode = QLabel("MANUAL")
        self.lbl_mode.setObjectName("Value")
        self.lbl_mode.setMinimumWidth(80)
        self.lbl_mode.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        slider_row.addWidget(self.lbl_mode)

        layout.addLayout(slider_row)

        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        self.lbl_i2c_speed = QLabel("Speed: 0.0 km/h")
        self.lbl_i2c_speed.setObjectName("Muted")
        info_row.addWidget(self.lbl_i2c_speed)

        self.lbl_i2c_brake = QLabel("Brake: OFF")
        self.lbl_i2c_brake.setObjectName("Muted")
        info_row.addWidget(self.lbl_i2c_brake)

        info_row.addStretch(1)

        layout.addLayout(info_row)

        self.main_layout.addWidget(card)

    def connect_signals(self):
        # Store / BMS
        self.store.speed_changed.connect(self.speed_gauge.setValue)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)

        self.store.soc_changed.connect(self.energy_circle.update_status)

        self.store.motor_temp_changed.connect(self.motor_temp_bar.set_value)
        self.store.batt_temp_changed.connect(self.batt_temp_bar.set_value)

        self.store.system_ready.connect(lambda s: self.alert_bar.update_alert("READY", s))
        self.store.brake_active.connect(lambda s: self.alert_bar.update_alert("BRAKE", s))
        self.store.is_limiting.connect(lambda s: self.alert_bar.update_alert("LIMIT", s))

        self.store.motor_temp_changed.connect(lambda v: self.alert_bar.update_alert("MOT_TEMP", v > 85))
        self.store.batt_temp_changed.connect(lambda v: self.alert_bar.update_alert("BATT_TEMP", v > 55))
        self.store.soc_changed.connect(lambda v: self.alert_bar.update_alert("LOW_BATT", v < 15))

        # Variateur I2C
        self.variator.telemetry_received.connect(self._on_i2c_telemetry)
        self.variator.connection_changed.connect(self._on_i2c_connection)

    def _push_slider_command(self):
        target = int(self.slider_target.value())
        mode = 1 if target > 0 else 0
        self.variator.set_command(mode, target)

        self.lbl_target.setText(f"Target {target} km/h")
        self.lbl_mode.setText("AUTO" if mode == 1 else "MANUAL")

    @Slot(int)
    def _on_slider_changed(self, _value: int):
        self._push_slider_command()

    def _update_power_gauge(self):
        raw_w = self.v_temp * self.i_temp

        # Convention UI voulue :
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
        self.i2c_speed = float(vitesse_kmh)
        self.i2c_mode = int(mode)
        self.i2c_brake = bool(frein)

        self.lbl_i2c_speed.setText(f"Speed: {self.i2c_speed:.1f} km/h")
        self.lbl_i2c_brake.setText(f"Brake: {'ON' if self.i2c_brake else 'OFF'}")
        self.lbl_mode.setText("AUTO" if self.i2c_mode == 1 else "MANUAL")

        # cohérence visuelle sur la barre d'alertes
        self.alert_bar.update_alert("BRAKE", self.i2c_brake)

    @Slot(bool)
    def _on_i2c_connection(self, connected: bool):
        self.i2c_connected = bool(connected)
        self.lbl_i2c_link.setText("ONLINE" if connected else "OFFLINE")

    def closeEvent(self, event):
        try:
            self.variator.stop()
        except Exception:
            pass
        super().closeEvent(event)