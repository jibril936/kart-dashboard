from PyQt6.QtCore import QObject, pyqtSignal

class StateStore(QObject):
    """Central state and signal hub for ALL BMS and Vehicle data."""

    # --- VEHICLE ---
    speed_changed = pyqtSignal(float)
    steer_angle_changed = pyqtSignal(float)
    brake_status = pyqtSignal(bool)
    motor_temp_changed = pyqtSignal(float)

    # --- BMS GLOBAL ---
    soc_changed = pyqtSignal(int)
    pack_voltage_changed = pyqtSignal(float)
    pack_current_changed = pyqtSignal(float)
    power_changed = pyqtSignal(float)  # Watts
    capacity_remaining_ah = pyqtSignal(float)
    cycle_count = pyqtSignal(int)

    # --- BMS CELLS ---
    cell_voltages_changed = pyqtSignal(list) # Liste des 16-24 tensions
    cell_min_v = pyqtSignal(float)
    cell_max_v = pyqtSignal(float)
    cell_delta_v = pyqtSignal(float)

    # --- BMS TEMPERATURES ---
    temp_mosfet = pyqtSignal(float)
    temp_sensor_1 = pyqtSignal(float)
    temp_sensor_2 = pyqtSignal(float)

    # --- BMS STATUS & ALARMS ---
    # On envoie des codes bruts ou des dictionnaires pour le tri ultérieur
    bms_status_bitmask = pyqtSignal(int)
    bms_alarms = pyqtSignal(list)

    # --- SAFETY & STATION ---
    ultrasonic_distances = pyqtSignal(list)
    evse_data = pyqtSignal(float, float)