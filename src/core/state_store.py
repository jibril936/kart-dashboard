from qtpy.QtCore import QObject, Signal

class StateStore(QObject):
    def __init__(self):
        super().__init__()
        self.soc = 0
        self.last_delta = 0.0
        self.last_min = 0.0
        self.last_max = 0.0

    def get_soc(self):
        return getattr(self, 'soc', 0)

    # --- SIGNAUX VÉHICULE (MockService) ---
    speed_changed = Signal(float)
    motor_temp_changed = Signal(float)
    system_ready = Signal(bool)
    brake_active = Signal(bool)
    is_limiting = Signal(bool)

    # --- SIGNAUX BMS (HardwareService UNIQUEMENT) ---
    soc_changed = Signal(int)
    pack_voltage_changed = Signal(float)
    pack_current_changed = Signal(float)
    capacity_remaining_ah = Signal(float)
    cycle_count = Signal(int)
    
    batt_temp_changed = Signal(float) 
    temp_mosfet = Signal(float)
    temp_sensor_1 = Signal(float)
    temp_sensor_2 = Signal(float)

    cell_voltages_changed = Signal(list)
    cell_min_v = Signal(float)
    cell_max_v = Signal(float)
    cell_delta_v = Signal(float)

    bms_alarm = Signal(str)
    bms_status_bitmask = Signal(int)