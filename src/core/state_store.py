from qtpy.QtCore import QObject, Signal

class StateStore(QObject):
    """Hub central pour toutes les données du véhicule et du BMS."""

    def __init__(self):
        super().__init__()
        # Valeurs par défaut pour éviter les erreurs au démarrage
        self.soc = 0
        self.last_delta = 0.0
        self.last_min = 0.0
        self.last_max = 0.0

    def get_soc(self):
        """Récupération sécurisée du pourcentage de batterie."""
        return getattr(self, 'soc', 0)

    # --- VÉHICULE ---
    speed_changed = Signal(float)
    motor_temp_changed = Signal(float)
    system_ready = Signal(bool)
    brake_active = Signal(bool)
    is_limiting = Signal(bool)        # <--- AJOUTÉ : Pour corriger ton erreur

    # --- BMS GLOBAL ---
    soc_changed = Signal(int)
    pack_voltage_changed = Signal(float)
    pack_current_changed = Signal(float)
    
    # --- BMS TEMPÉRATURES ---
    batt_temp_changed = Signal(float) # Signal principal pour l'UI
    temp_mosfet = Signal(float)
    temp_sensor_1 = Signal(float)
    temp_sensor_2 = Signal(float)

    # --- BMS CELLULES ---
    cell_voltages_changed = Signal(list)
    cell_min_v = Signal(float)
    cell_max_v = Signal(float)
    cell_delta_v = Signal(float)

    # --- ALERTES ---
    bms_alarm = Signal(str)