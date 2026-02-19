from __future__ import annotations

from dataclasses import dataclass
from typing import List

from qtpy.QtCore import QObject, Signal


@dataclass(frozen=True)
class CellStats:
    v_min: float
    v_max: float
    delta: float


class StateStore(QObject):
    """
    SOURCE DE VÉRITÉ
    - Stockage interne systématique
    - Setters: update valeur -> emit signal
    """

    # -----------------
    # VEHICULE / SIMU
    # -----------------
    speed_changed = Signal(float)
    motor_temp_changed = Signal(float)

    # Signaux attendus par ClusterPage / alert bar
    system_ready = Signal(bool)
    brake_active = Signal(bool)
    is_limiting = Signal(bool)

    # -----------------
    # BMS (JK)
    # -----------------
    soc_changed = Signal(int)
    pack_voltage_changed = Signal(float)
    pack_current_changed = Signal(float)

    # DEMANDÉS (tech JK)
    batt_temp_changed = Signal(float)
    capacity_remaining_ah = Signal(float)
    cycle_count = Signal(int)
    bms_status_bitmask = Signal(int)
    mosfet_status_changed = Signal(bool, bool)  # (charge_on, discharge_on)

    # Cellules (overlay)
    cell_voltages_changed = Signal(list)
    cell_min_v = Signal(float)
    cell_max_v = Signal(float)
    cell_delta_v = Signal(float)

    # Optionnel (UI)
    bms_alarm = Signal(str)

    def __init__(self) -> None:
        super().__init__()

        # ---------
        # VEHICULE
        # ---------
        self._speed: float = 0.0
        self._motor_temp: float = 0.0

        self._system_ready: bool = False
        self._brake_active: bool = False
        self._is_limiting: bool = False

        # ---
        # BMS
        # ---
        self._soc: int = 0
        self._pack_voltage: float = 0.0
        self._pack_current: float = 0.0

        self._batt_temp: float = 0.0
        self._capacity_remaining_ah: float = 0.0
        self._cycle_count: int = 0
        self._bms_status_bitmask: int = 0

        self._charge_mosfet_on: bool = False
        self._discharge_mosfet_on: bool = False

        self._cell_voltages: List[float] = []
        self._cell_stats: CellStats = CellStats(0.0, 0.0, 0.0)

    # -----------------
    # Helpers
    # -----------------
    @staticmethod
    def _same_float(a: float, b: float, eps: float = 1e-4) -> bool:
        return abs(a - b) <= eps

    # -----------------
    # VEHICULE setters
    # -----------------
    def set_speed(self, val: float) -> None:
        v = float(val)
        if self._same_float(v, self._speed, eps=1e-3):
            return
        self._speed = v
        self.speed_changed.emit(v)

    def get_speed(self) -> float:
        return self._speed

    def set_motor_temp(self, val: float) -> None:
        v = float(val)
        if self._same_float(v, self._motor_temp, eps=1e-2):
            return
        self._motor_temp = v
        self.motor_temp_changed.emit(v)

    def get_motor_temp(self) -> float:
        return self._motor_temp

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

    # -----------------
    # BMS setters
    # -----------------
    def set_soc(self, val: int) -> None:
        v = int(val)
        v = max(0, min(100, v))
        if v == self._soc:
            return
        self._soc = v
        self.soc_changed.emit(v)

    def get_soc(self) -> int:
        return self._soc

    def set_pack_voltage(self, val: float) -> None:
        v = float(val)
        if self._same_float(v, self._pack_voltage, eps=1e-3):
            return
        self._pack_voltage = v
        self.pack_voltage_changed.emit(v)

    def set_voltage(self, val: float) -> None:
        self.set_pack_voltage(val)

    def get_pack_voltage(self) -> float:
        return self._pack_voltage

    def set_pack_current(self, val: float) -> None:
        v = float(val)
        if self._same_float(v, self._pack_current, eps=1e-3):
            return
        self._pack_current = v
        self.pack_current_changed.emit(v)

    def set_current(self, val: float) -> None:
        self.set_pack_current(val)

    def get_pack_current(self) -> float:
        return self._pack_current

    def set_batt_temp(self, val: float) -> None:
        v = float(val)
        if self._same_float(v, self._batt_temp, eps=1e-2):
            return
        self._batt_temp = v
        self.batt_temp_changed.emit(v)

    def get_batt_temp(self) -> float:
        return self._batt_temp

    def set_capacity_remaining_ah(self, val: float) -> None:
        v = float(val)
        if self._same_float(v, self._capacity_remaining_ah, eps=1e-3):
            return
        self._capacity_remaining_ah = v
        self.capacity_remaining_ah.emit(v)

    def get_capacity_remaining_ah(self) -> float:
        return self._capacity_remaining_ah

    def set_cycle_count(self, val: int) -> None:
        v = int(val)
        if v == self._cycle_count:
            return
        self._cycle_count = v
        self.cycle_count.emit(v)

    def get_cycle_count(self) -> int:
        return self._cycle_count

    def set_bms_status_bitmask(self, val: int) -> None:
        v = int(val) & 0xFFFF
        if v == self._bms_status_bitmask:
            return
        self._bms_status_bitmask = v
        self.bms_status_bitmask.emit(v)

    def get_bms_status_bitmask(self) -> int:
        return self._bms_status_bitmask

    def set_mosfet_status(self, charge_on: bool, discharge_on: bool) -> None:
        c = bool(charge_on)
        d = bool(discharge_on)
        if c == self._charge_mosfet_on and d == self._discharge_mosfet_on:
            return
        self._charge_mosfet_on = c
        self._discharge_mosfet_on = d
        self.mosfet_status_changed.emit(c, d)

    def get_mosfet_status(self) -> tuple[bool, bool]:
        return self._charge_mosfet_on, self._discharge_mosfet_on

    # -----------------
    # Cellules setters
    # -----------------
    def set_cell_voltages(self, voltages: List[float]) -> None:
        if not voltages:
            return

        v_list = [float(v) for v in voltages]
        self._cell_voltages = v_list

        v_min = min(v_list)
        v_max = max(v_list)
        delta = v_max - v_min
        self._cell_stats = CellStats(v_min=v_min, v_max=v_max, delta=delta)

        self.cell_voltages_changed.emit(v_list)
        self.cell_min_v.emit(v_min)
        self.cell_max_v.emit(v_max)
        self.cell_delta_v.emit(delta)

    def set_cell_data(self, voltages: list, v_min: float = 0.0, v_max: float = 0.0, delta: float = 0.0) -> None:
        self.set_cell_voltages(list(voltages))

    def get_cell_voltages(self) -> List[float]:
        return list(self._cell_voltages)

    def get_cell_stats(self) -> CellStats:
        return self._cell_stats

    # -----------------
    # Diagnostics
    # -----------------
    def emit_bms_alarm(self, message: str) -> None:
        self.bms_alarm.emit(str(message))
