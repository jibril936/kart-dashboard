from qtpy.QtCore import QObject, Signal

class StateStore(QObject):
    """Hub central pour toutes les données du véhicule et du BMS."""

    def __init__(self):
        super().__init__()
        # Valeurs par défaut pour éviter les erreurs de type 'None'
        self.soc = 0
        self.last_delta = 0.0
        self.last_min = 3.2
        self.last_max = 3.3
        self.is_ready = False

    def get_soc(self):
        return getattr(self, 'soc', 0)

    # --- ÉTAT DU VÉHICULE & SYSTÈME ---
    speed_changed = Signal(float)
    motor_temp_changed = Signal(float)
    batt_temp_changed = Signal(float)
    system_ready = Signal(bool)
    brake_active = Signal(bool)
    is_limiting = Signal(bool)

    # --- BMS GLOBAL ---
    soc_changed = Signal(int)
    pack_voltage_changed = Signal(float)
    pack_current_changed = Signal(float)
    
    # --- BMS CELLULES ---
    cell_voltages_changed = Signal(list)
    cell_min_v = Signal(float)
    cell_max_v = Signal(float)
    cell_delta_v = Signal(float)

    # --- ALERTES ---
    bms_alarm = Signal(str)