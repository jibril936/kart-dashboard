from __future__ import annotations

from qtpy.QtCore import QObject, Signal


class StateStore(QObject):
    """
    Source unique de vérité pour tout le kart.
    Toutes les données doivent passer par des setters qui :
      1) stockent la valeur
      2) émettent le signal correspondant
    """

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

    def __init__(self) -> None:
        super().__init__()

        # --- Stockage interne (Source of Truth) ---
        # Véhicule
        self.speed: float = 0.0
        self.motor_temp: float = 0.0
        self._system_ready: bool = False
        self._brake_active: bool = False
        self._is_limiting: bool = False

        # BMS
        self.soc: int = 0
        self.pack_voltage: float = 0.0
        self.pack_current: float = 0.0
        self.batt_temp: float = 0.0

        # BMS techniques
        self.capacity_ah: float = 0.0
        self._cycle_count: int = 0
        self._bms_status_bitmask: int = 0

        self._temp_mosfet: float = 0.0
        self._temp_sensor_1: float = 0.0
        self._temp_sensor_2: float = 0.0

        # Cellules
        self.cell_voltages: list[float] = []
        self._cell_min_v: float = 0.0
        self._cell_max_v: float = 0.0
        self._cell_delta_v: float = 0.0

    # ---------------------------------------------------------------------
    # Getters (si l'UI en a besoin) + Setters (obligatoires côté services)
    # ---------------------------------------------------------------------

    # --- Véhicule ---
    def set_speed(self, val: float) -> None:
        v = float(val)
        if v == self.speed:
            return
        self.speed = v
        self.speed_changed.emit(v)

    def get_speed(self) -> float:
        return self.speed

    def set_motor_temp(self, val: float) -> None:
        v = float(val)
        if v == self.motor_temp:
            return
        self.motor_temp = v
        self.motor_temp_changed.emit(v)

    def get_motor_temp(self) -> float:
        return self.motor_temp

    def set_system_ready(self, val: bool) -> None:
        v = bool(val)
        if v == self._system_ready:
            return
        self._system_ready = v
        self.system_ready.emit(v)

    def get_system_ready(self) -> bool:
        return self._system_ready

    def set_brake_active(self, val: bool) -> None:
        v = bool(val)
        if v == self._brake_active:
            return
        self._brake_active = v
        self.brake_active.emit(v)

    def get_brake_active(self) -> bool:
        return self._brake_active

    def set_is_limiting(self, val: bool) -> None:
        v = bool(val)
        if v == self._is_limiting:
            return
        self._is_limiting = v
        self.is_limiting.emit(v)

    def get_is_limiting(self) -> bool:
        return self._is_limiting

    # --- BMS ---
    def set_soc(self, val: int) -> None:
        v = int(val)
        if v == self.soc:
            return
        self.soc = v
        self.soc_changed.emit(v)

    def get_soc(self) -> int:
        return self.soc

    def set_pack_voltage(self, val: float) -> None:
        v = float(val)
        if v == self.pack_voltage:
            return
        self.pack_voltage = v
        self.pack_voltage_changed.emit(v)

    # Alias pratique (si tu veux l’appeler set_voltage)
    def set_voltage(self, val: float) -> None:
        self.set_pack_voltage(val)

    def get_pack_voltage(self) -> float:
        return self.pack_voltage

    def set_pack_current(self, val: float) -> None:
        v = float(val)
        if v == self.pack_current:
            return
        self.pack_current = v
        self.pack_current_changed.emit(v)

    # Alias pratique (si tu veux l’appeler set_current)
    def set_current(self, val: float) -> None:
        self.set_pack_current(val)

    def get_pack_current(self) -> float:
        return self.pack_current

    def set_batt_temp(self, val: float) -> None:
        v = float(val)
        if v == self.batt_temp:
            return
        self.batt_temp = v
        self.batt_temp_changed.emit(v)

    def get_batt_temp(self) -> float:
        return self.batt_temp

    # --- BMS techniques ---
    def set_capacity_remaining_ah(self, val: float) -> None:
        v = float(val)
        if v == self.capacity_ah:
            return
        self.capacity_ah = v
        self.capacity_remaining_ah.emit(v)

    def get_capacity_remaining_ah(self) -> float:
        return self.capacity_ah

    def set_cycle_count(self, val: int) -> None:
        v = int(val)
        if v == self._cycle_count:
            return
        self._cycle_count = v
        self.cycle_count.emit(v)

    def get_cycle_count(self) -> int:
        return self._cycle_count

    def set_bms_status_bitmask(self, val: int) -> None:
        v = int(val)
        if v == self._bms_status_bitmask:
            return
        self._bms_status_bitmask = v
        self.bms_status_bitmask.emit(v)

    def get_bms_status_bitmask(self) -> int:
        return self._bms_status_bitmask

    def set_temp_mosfet(self, val: float) -> None:
        v = float(val)
        if v == self._temp_mosfet:
            return
        self._temp_mosfet = v
        self.temp_mosfet.emit(v)

    def set_temp_sensor_1(self, val: float) -> None:
        v = float(val)
        if v == self._temp_sensor_1:
            return
        self._temp_sensor_1 = v
        self.temp_sensor_1.emit(v)

    def set_temp_sensor_2(self, val: float) -> None:
        v = float(val)
        if v == self._temp_sensor_2:
            return
        self._temp_sensor_2 = v
        self.temp_sensor_2.emit(v)

    # --- Cellules ---
    def set_cell_data(self, voltages: list[float]) -> None:
        if not voltages:
            return

        # On copie pour éviter toute surprise si une liste est réutilisée ailleurs
        v_list = [float(v) for v in voltages]

        v_min = min(v_list)
        v_max = max(v_list)
        delta = v_max - v_min

        self.cell_voltages = v_list
        self._cell_min_v = v_min
        self._cell_max_v = v_max
        self._cell_delta_v = delta

        self.cell_voltages_changed.emit(v_list)
        self.cell_min_v.emit(v_min)
        self.cell_max_v.emit(v_max)
        self.cell_delta_v.emit(delta)

    def get_cell_voltages(self) -> list[float]:
        return list(self.cell_voltages)

    def emit_bms_alarm(self, message: str) -> None:
        self.bms_alarm.emit(str(message))
