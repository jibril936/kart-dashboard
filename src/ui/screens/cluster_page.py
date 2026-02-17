from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qtpy.QtCore import Qt, Slot
from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.temperature_widget import TemperatureWidget
from src.ui.components.battery_elements import PackBatteryWidget

class ClusterPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.v_temp = 0.0 # Stockage temporaire du voltage pour le calcul des kW
        
        # --- CONFIGURATION VISUELLE ---
        # Force le fond noir pour éviter l'héritage du thème de la Pi
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Structure l'écran en 3 colonnes : Vitesse | Batterie | Puissance"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # 1. Pousse l'ensemble vers le bas (pour dégager la vue du volant)
        self.main_layout.addStretch(1)

        # 2. CONTENEUR HORIZONTAL
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
        # On descend le widget batterie pour qu'il soit au niveau des textes de température
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
        
        # 3. Espace de sécurité en bas
        self.main_layout.addStretch(1)

    def connect_signals(self):
        """Relie les signaux du StateStore aux widgets de l'interface"""
        self.store.speed_changed.connect(self.speed_gauge.setValue)
        self.store.pack_current_changed.connect(self._on_current)
        self.store.pack_voltage_changed.connect(self._on_voltage)
        self.store.soc_changed.connect(self._on_soc)
        
        # Connexion des températures (vérifie que les noms correspondent dans ton store)
        if hasattr(self.store, 'motor_temp_changed'):
            self.store.motor_temp_changed.connect(self.motor_temp.set_value)
        if hasattr(self.store, 'batt_temp_changed'):
            self.store.batt_temp_changed.connect(self.batt_temp.set_value)

    @Slot(float)
    def _on_current(self, amps):
        """Calcule la puissance en kW dès que le courant change"""
        kw = (self.v_temp * amps) / 1000.0
        self.power_gauge.setValue(kw)

    @Slot(float)
    def _on_voltage(self, volts):
        """Met à jour le voltage et rafraîchit l'affichage batterie"""
        self.v_temp = volts
        # On utilise get_soc() pour s'assurer d'avoir une valeur propre
        self.pack_status.update_status(self.store.get_soc())

    @Slot(int)
    def _on_soc(self, val):
        """Met à jour le pourcentage de batterie"""
        self.pack_status.update_status(val)