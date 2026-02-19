from qtpy.QtCore import QObject, Signal

class StateStore(QObject):
    """Source unique de vérité pour tout le kart."""

    # --- SIGNAUX VÉHICULE ---
    speed_changed = Signal(float)
    motor_temp_changed = Signal(float)
    system_ready = Signal(bool)
    brake_active = Signal(bool)
    is_limiting = Signal(bool)

    # --- SIGNAUX BMS ---
    soc_changed = Signal(int)
    pack_voltage_changed = Signal(float)
    pack_current_changed = Signal(float)
    batt_temp_changed = Signal(float)
    
    # Signaux techniques (évitent les crashs HardwareService)
    capacity_remaining_ah = Signal(float)
    cycle_count = Signal(int)
    bms_status_bitmask = Signal(int)
    temp_mosfet = Signal(float)
    temp_sensor_1 = Signal(float)
    temp_sensor_2 = Signal(float)

    # Cellules
    cell_voltages_changed = Signal(list)
    cell_min_v = Signal(float)
    cell_max_v = Signal(float)
    cell_delta_v = Signal(float)
    bms_alarm = Signal(str)

    def __init__(self):
        super().__init__()
        # Stockage interne des données (Source of Truth)
        self.soc = 0
        self.voltage = 0.0
        self.current = 0.0
        self.delta = 0.0
        self.v_min = 0.0
        self.v_max = 0.0
        self.speed = 0.0

    # Getters / Setters pour garantir la mise à jour avant l'émission
    def set_soc(self, val: int):
        self.soc = val
        self.soc_changed.emit(val)

    def get_soc(self):
        return self.soc

    def set_voltage(self, val: float):
        self.voltage = val
        self.pack_voltage_changed.emit(val)

    def set_cell_data(self, voltages: list, v_min: float, v_max: float, delta: float):
        self.v_min = v_min
        self.v_max = v_max
        self.delta = delta
        self.cell_voltages_changed.emit(voltages)
        self.cell_min_v.emit(v_min)
        self.cell_max_v.emit(v_max)
        self.cell_delta_v.emit(delta)