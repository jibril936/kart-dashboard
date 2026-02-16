from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from qtpy.QtCore import Qt, Slot
from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.battery_icon import BatteryIcon

class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.v_temp = 0.0
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.setStyleSheet("background-color: black;")
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # --- GAUCHE : VITESSE (0-70 km/h, pas de 10) ---
        # scalaCount=7 donnera : 0, 10, 20, 30, 40, 50, 60, 70
        self.speed_gauge = AnalogGaugeWidget(minValue=0, maxValue=70, units="km/h", scalaCount=7, parent=self)
        self.main_layout.addWidget(self.speed_gauge, stretch=2)

        # --- CENTRE : BATTERIE & INFOS ---
        self.center_block = QVBoxLayout()
        self.center_block.setSpacing(5)
        self.center_block.addStretch()

        self.batt_icon = BatteryIcon(self)
        self.soc_label = QLabel("0%")
        self.soc_label.setStyleSheet("color: white; font-size: 40px; font-family: 'Orbitron'; font-weight: bold;")
        self.volt_label = QLabel("0.0V")
        self.volt_label.setStyleSheet("color: #888888; font-size: 22px; font-family: 'Orbitron';")

        self.center_block.addWidget(self.batt_icon, alignment=Qt.AlignCenter)
        self.center_block.addWidget(self.soc_label, alignment=Qt.AlignCenter)
        self.center_block.addWidget(self.volt_label, alignment=Qt.AlignCenter)
        self.center_block.addStretch()
        
        self.main_layout.addLayout(self.center_block, stretch=1)

        # --- DROITE : PUISSANCE (-2 à +10 kW, pas de 2) ---
        # scalaCount=6 donnera : -2, 0, 2, 4, 6, 8, 10
        self.power_gauge = AnalogGaugeWidget(minValue=-2, maxValue=10, units="kW", scalaCount=6, parent=self)
        self.main_layout.addWidget(self.power_gauge, stretch=2)

    def connect_signals(self):
        self.store.speed_changed.connect(self.speed_gauge.setValue)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)
        self.store.soc_changed.connect(self._on_soc)

    @Slot(float)
    def _on_current(self, amps):
        # Calcul kW
        kw = (self.v_temp * amps) / 1000.0
        self.power_gauge.setValue(kw)

    @Slot(float)
    def _on_voltage(self, volts):
        self.v_temp = volts
        self.volt_label.setText(f"{volts:.1f}V")

    @Slot(int)
    def _on_soc(self, val):
        self.soc_label.setText(f"{val}%")
        self.batt_icon.set_value(val)