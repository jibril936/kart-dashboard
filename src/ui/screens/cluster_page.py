from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from qtpy.QtCore import Qt, Slot
from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.temperature_widget import TemperatureWidget
from src.ui.components.pack_battery_widget import PackBatteryWidget

class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.v_temp = 0.0
        # Force le fond noir et l'application du style
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        # Layout Principal (Vertical)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # 1. Pousse tout vers le bas pour libérer le haut (Zone Alertes)
        self.main_layout.addStretch(1)

        # 2. LA LIGNE DES COMPTEURS (Horizontale)
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(10)

        # --- COLONNE GAUCHE (Vitesse + Temp Moteur) ---
        self.left_col = QVBoxLayout()
        self.speed_gauge = AnalogGaugeWidget(minValue=0, maxValue=70, units="km/h", scalaCount=7)
        self.speed_gauge.setMinimumSize(350, 350)
        self.motor_temp = TemperatureWidget("MOTOR TEMP")
        
        self.left_col.addWidget(self.speed_gauge, alignment=Qt.AlignCenter)
        self.left_col.addWidget(self.motor_temp, alignment=Qt.AlignCenter)
        self.content_layout.addLayout(self.left_col)

        # --- COLONNE CENTRALE (Batterie %) ---
        self.center_col = QVBoxLayout()
        self.pack_status = PackBatteryWidget()
        # On ajoute un gros spacer pour que la batterie soit alignée sur les textes du bas
        self.center_col.addStretch(5) 
        self.center_col.addWidget(self.pack_status, alignment=Qt.AlignCenter)
        self.center_col.addStretch(1)
        self.content_layout.addLayout(self.center_col)

        # --- COLONNE DROITE (Puissance + Temp Batterie) ---
        self.right_col = QVBoxLayout()
        self.power_gauge = AnalogGaugeWidget(minValue=-2, maxValue=10, units="kW", scalaCount=6)
        self.power_gauge.setMinimumSize(350, 350)
        self.batt_temp = TemperatureWidget("BATT TEMP")
        
        self.right_col.addWidget(self.power_gauge, alignment=Qt.AlignCenter)
        self.right_col.addWidget(self.batt_temp, alignment=Qt.AlignCenter)
        self.content_layout.addLayout(self.right_col)

        self.main_layout.addLayout(self.content_layout)
        
        # 3. Petit espace en bas
        self.main_layout.addStretch(1)

    def connect_signals(self):
        self.store.speed_changed.connect(self.speed_gauge.setValue)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)
        self.store.soc_changed.connect(self._on_soc)
        
        if hasattr(self.store, 'motor_temp_changed'):
            self.store.motor_temp_changed.connect(self.motor_temp.set_value)
        if hasattr(self.store, 'batt_temp_changed'):
            self.store.batt_temp_changed.connect(self.batt_temp.set_value)

    @Slot(float)
    def _on_current(self, amps):
        kw = (self.v_temp * amps) / 1000.0
        self.power_gauge.setValue(kw)

    @Slot(float)
    def _on_voltage(self, volts):
        self.v_temp = volts
        self.pack_status.update_status(self.store.get_soc())

    @Slot(int)
    def _on_soc(self, val):
        self.pack_status.update_status(val)