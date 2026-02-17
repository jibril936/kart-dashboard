from qtpy.QtCore import QObject, Signal

class StateStore(QObject):
    """Central state and signal hub for ALL BMS and Vehicle data."""
# Dans src/core/state_store.py

    def get_soc(self):
        """Retourne le pourcentage de batterie (soc) ou 0 par défaut"""
        # getattr permet d'éviter le crash si 'soc' n'est pas encore créé
        return getattr(self, 'soc', 0)
    # --- VEHICLE ---
    speed_changed = Signal(float)
    steer_angle_changed = Signal(float)
    brake_status = Signal(bool)
    motor_temp_changed = Signal(float)

    # --- BMS GLOBAL ---
    soc_changed = Signal(int)
    pack_voltage_changed = Signal(float)
    pack_current_changed = Signal(float)
    power_changed = Signal(float)  # Watts
    capacity_remaining_ah = Signal(float)
    cycle_count = Signal(int)

    # --- BMS CELLS ---
    cell_voltages_changed = Signal(list) # Liste des 16-24 tensions
    cell_min_v = Signal(float)
    cell_max_v = Signal(float)
    cell_delta_v = Signal(float)

    # --- BMS TEMPERATURES ---
    batt_temp_changed = Signal(float)
    temp_mosfet = Signal(float)
    temp_sensor_1 = Signal(float)
    temp_sensor_2 = Signal(float)

    # --- BMS STATUS & ALARMS ---
    # On envoie des codes bruts ou des dictionnaires pour le tri ultérieur
    bms_status_bitmask = Signal(int)
    bms_alarms = Signal(list)

    # --- SAFETY & STATION ---
    ultrasonic_distances = Signal(list)
    evse_data = Signal(float, float)