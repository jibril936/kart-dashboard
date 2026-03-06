from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.battery_elements import CircularBatteryWidget
from src.ui.components.indicator_elements import IconAlertBar, SegmentedTempBar


class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self.v_temp = 0.0
        self.i_temp = 0.0

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Structure optimisée 800x480 avec puissance traction positive à l'accélération."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.main_layout.setSpacing(0)

        self.alert_bar = IconAlertBar()
        self.main_layout.addWidget(self.alert_bar)

        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(10, 0, 10, 0)
        self.content_layout.setSpacing(0)

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

        self.energy_circle = CircularBatteryWidget()
        self.content_layout.addWidget(self.energy_circle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.right_col = QVBoxLayout()
        self.power_gauge = AnalogGaugeWidget(
            minValue=0,
            maxValue=2,
            units="kW",
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

    def _update_power_gauge(self):
        raw_kw = (self.v_temp * self.i_temp) / 1000.0

        # Convention UI :
        # - traction / accélération => positif
        # - charge / régénération => ramené à 0 sur ce compteur
        traction_kw = max(0.0, -raw_kw)

        self.power_gauge.setValue(min(2.0, traction_kw))

    @Slot(float)
    def _on_current(self, amps: float):
        self.i_temp = float(amps)
        self._update_power_gauge()

    @Slot(float)
    def _on_voltage(self, volts: float):
        self.v_temp = float(volts)
        self._update_power_gauge()