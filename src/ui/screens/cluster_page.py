from qtpy.QtCore import Qt, Slot
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.battery_elements import CircularBatteryWidget
from src.ui.components.indicator_elements import IconAlertBar, SegmentedTempBar


class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        # Mémoire pour calcul des kW
        self.v_temp = 0.0
        self.i_temp = 0.0

        # --- CONFIGURATION VISUELLE ---
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Structure optimisée 800x480 avec Cercle Central et Alertes Icônes."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.main_layout.setSpacing(0)

        # 1) BARRE D'ALERTES
        self.alert_bar = IconAlertBar()
        self.main_layout.addWidget(self.alert_bar)

        # 2) ZONE PRINCIPALE
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(10, 0, 10, 0)
        self.content_layout.setSpacing(0)

        # --- COLONNE GAUCHE (Vitesse + Temp Moteur) ---
        self.left_col = QVBoxLayout()
        self.speed_gauge = AnalogGaugeWidget(minValue=0, maxValue=70, units="km/h", scalaCount=7)
        self.speed_gauge.setFixedSize(260, 260)
        self.motor_temp_bar = SegmentedTempBar("MOTOR")

        self.left_col.addWidget(self.speed_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self.left_col.addWidget(self.motor_temp_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.left_col)

        # --- COLONNE CENTRALE (SOC) ---
        self.energy_circle = CircularBatteryWidget()
        self.content_layout.addWidget(self.energy_circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- COLONNE DROITE (Puissance + Temp Batterie) ---
        self.right_col = QVBoxLayout()
        self.power_gauge = AnalogGaugeWidget(minValue=-2, maxValue=10, units="kW", scalaCount=6)
        self.power_gauge.setFixedSize(260, 260)
        self.batt_temp_bar = SegmentedTempBar("BATT")

        self.right_col.addWidget(self.power_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        self.right_col.addWidget(self.batt_temp_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addLayout(self.right_col)

        self.main_layout.addLayout(self.content_layout)

        # 3) ESPACE POUR LA NAVBAR
        self.main_layout.addStretch(1)

    def connect_signals(self):
        """Liaison entre le StateStore et les widgets."""
        # Conduite
        self.store.speed_changed.connect(self.speed_gauge.setValue)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)

        # Batterie
        self.store.soc_changed.connect(self.energy_circle.update_status)

        # Températures
        self.store.motor_temp_changed.connect(self.motor_temp_bar.set_value)
        self.store.batt_temp_changed.connect(self.batt_temp_bar.set_value)

        # Alertes (icônes)
        self.store.system_ready.connect(lambda s: self.alert_bar.update_alert("READY", s))
        self.store.brake_active.connect(lambda s: self.alert_bar.update_alert("BRAKE", s))
        self.store.is_limiting.connect(lambda s: self.alert_bar.update_alert("LIMIT", s))

        # Alertes Temp (auto)
        self.store.motor_temp_changed.connect(lambda v: self.alert_bar.update_alert("MOT_TEMP", v > 85))
        self.store.batt_temp_changed.connect(lambda v: self.alert_bar.update_alert("BATT_TEMP", v > 55))
        self.store.soc_changed.connect(lambda v: self.alert_bar.update_alert("LOW_BATT", v < 15))

    @Slot(float)
    def _on_current(self, amps: float):
        self.i_temp = amps
        kw = (self.v_temp * self.i_temp) / 1000.0
        self.power_gauge.setValue(kw)

    @Slot(float)
    def _on_voltage(self, volts: float):
        self.v_temp = volts
        # IMPORTANT : on ne force plus le refresh du SOC ici.
        # Le SOC est poussé uniquement par le signal soc_changed.
        kw = (self.v_temp * self.i_temp) / 1000.0
        self.power_gauge.setValue(kw)
