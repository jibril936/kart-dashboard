from __future__ import annotations

import math
import random
import time

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class KartDataModel(QObject):
    speed_changed = pyqtSignal(float)
    battery_pack_voltage_changed = pyqtSignal(float)
    battery_pack_current_changed = pyqtSignal(float)
    instant_power_changed = pyqtSignal(float)
    motor_temperature_changed = pyqtSignal(float)
    battery_temperature_changed = pyqtSignal(float)
    brake_state_changed = pyqtSignal(bool)
    steering_angle_changed = pyqtSignal(float)
    ultrasonic_rear_1_distance_changed = pyqtSignal(float)
    ultrasonic_rear_2_distance_changed = pyqtSignal(float)
    ultrasonic_rear_3_distance_changed = pyqtSignal(float)
    warnings_changed = pyqtSignal(list)
    soc_changed = pyqtSignal(float)
    bms_temp_t1_changed = pyqtSignal(float)
    bms_temp_t2_changed = pyqtSignal(float)
    bms_temp_mos_changed = pyqtSignal(float)
    bms_temp_max_changed = pyqtSignal(float)
    cell_voltages_changed = pyqtSignal(list)
    cell_min_changed = pyqtSignal(float)
    cell_max_changed = pyqtSignal(float)
    cell_delta_changed = pyqtSignal(float)
    charging_state_changed = pyqtSignal(bool)
    evse_current_changed = pyqtSignal(float)
    evse_frequency_changed = pyqtSignal(float)
    steering_pot_voltage_changed = pyqtSignal(float)
    steering_current_changed = pyqtSignal(float)
    rpm_changed = pyqtSignal(float)
    ultrasonic_states_changed = pyqtSignal(list)
    ultrasonic_distances_changed = pyqtSignal(list)
    energy_wh_changed = pyqtSignal(float)
    battery_sag_changed = pyqtSignal(float)
    mode_changed = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._start_time = time.monotonic()
        self._last_update = self._start_time

        self._speed = 0.0
        self._battery_pack_voltage = 52.0
        self._battery_pack_current = 0.0
        self._instant_power = 0.0
        self._motor_temperature = 32.0
        self._battery_temperature = 28.0
        self._brake_state = False
        self._steering_angle = 0.0
        self._ultrasonic_rear_1_distance = 4.0
        self._ultrasonic_rear_2_distance = 4.0
        self._ultrasonic_rear_3_distance = 4.0
        self._warnings: list[str] = []
        self._soc = 90.0
        self._bms_temp_t1 = 27.0
        self._bms_temp_t2 = 28.0
        self._bms_temp_mos = 30.0
        self._bms_temp_max = 30.0
        self._cell_voltages = [4.02 + (i * 0.0008) for i in range(16)]
        self._cell_min = min(self._cell_voltages)
        self._cell_max = max(self._cell_voltages)
        self._cell_delta = self._cell_max - self._cell_min
        self._charging_state = False
        self._evse_current = 0.0
        self._evse_frequency = 50.0
        self._steering_pot_voltage = 2.5
        self._steering_current = 0.5
        self._rpm = 0.0
        self._ultrasonic_states = [False, False, False]
        self._ultrasonic_distances = [400.0, 400.0, 400.0]
        self._energy_wh = 0.0
        self._battery_sag = 0.0
        self._mode = "SPORT"

        self._timer = QTimer(self)
        self._timer.setInterval(50)
        self._timer.timeout.connect(self.update_simulation)
        self._timer.start()

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def battery_pack_voltage(self) -> float:
        return self._battery_pack_voltage

    @property
    def battery_pack_current(self) -> float:
        return self._battery_pack_current

    @property
    def instant_power(self) -> float:
        return self._instant_power

    @property
    def motor_temperature(self) -> float:
        return self._motor_temperature

    @property
    def battery_temperature(self) -> float:
        return self._battery_temperature

    @property
    def brake_state(self) -> bool:
        return self._brake_state

    @property
    def steering_angle(self) -> float:
        return self._steering_angle

    @property
    def ultrasonic_rear_1_distance(self) -> float:
        return self._ultrasonic_rear_1_distance

    @property
    def ultrasonic_rear_2_distance(self) -> float:
        return self._ultrasonic_rear_2_distance

    @property
    def ultrasonic_rear_3_distance(self) -> float:
        return self._ultrasonic_rear_3_distance

    @property
    def warnings(self) -> list[str]:
        return self._warnings

    @property
    def soc(self) -> float:
        return self._soc

    @property
    def bms_temp_t1(self) -> float:
        return self._bms_temp_t1

    @property
    def bms_temp_t2(self) -> float:
        return self._bms_temp_t2

    @property
    def bms_temp_mos(self) -> float:
        return self._bms_temp_mos

    @property
    def bms_temp_max(self) -> float:
        return self._bms_temp_max

    @property
    def cell_voltages(self) -> list[float]:
        return self._cell_voltages

    @property
    def cell_min(self) -> float:
        return self._cell_min

    @property
    def cell_max(self) -> float:
        return self._cell_max

    @property
    def cell_delta(self) -> float:
        return self._cell_delta

    @property
    def charging_state(self) -> bool:
        return self._charging_state

    @property
    def evse_current(self) -> float:
        return self._evse_current

    @property
    def evse_frequency(self) -> float:
        return self._evse_frequency

    @property
    def steering_pot_voltage(self) -> float:
        return self._steering_pot_voltage

    @property
    def steering_current(self) -> float:
        return self._steering_current

    @property
    def rpm(self) -> float:
        return self._rpm

    @property
    def ultrasonic_states(self) -> list[bool]:
        return self._ultrasonic_states

    @property
    def ultrasonic_distances(self) -> list[float]:
        return self._ultrasonic_distances

    @property
    def energy_wh(self) -> float:
        return self._energy_wh

    @property
    def battery_sag(self) -> float:
        return self._battery_sag

    @property
    def mode(self) -> str:
        return self._mode

    def update_simulation(self) -> None:
        now = time.monotonic()
        t = now - self._start_time
        dt = max(0.001, now - self._last_update)
        self._last_update = now

        speed = max(0.0, min(60.0, 28.0 + 22.0 * math.sin(t * 0.45) + 8.0 * math.sin(t * 1.2)))
        current = max(-200.0, min(200.0, 90.0 * math.sin(t * 0.42) + 40.0 * math.sin(t * 1.35)))
        voltage = max(44.0, min(54.0, 50.0 + 1.8 * math.sin(t * 0.17) - abs(current) * 0.005))
        power = voltage * current

        motor_temp = max(0.0, min(120.0, 45.0 + 20.0 * math.sin(t * 0.06) + speed * 0.15))
        batt_temp = max(0.0, min(80.0, 35.0 + 8.0 * math.sin(t * 0.09) + abs(current) * 0.02))
        brake_state = speed < 8.0 or math.sin(t * 0.8) > 0.92

        steering_angle = max(-35.0, min(35.0, 28.0 * math.sin(t * 0.7)))
        steering_pot_voltage = 2.5 + (steering_angle / 35.0) * 2.1
        steering_current = max(0.0, min(40.0, abs(steering_angle) * 0.25 + 0.5 * random.random()))

        rear_distances_m = [
            max(0.08, min(4.0, 2.0 + 1.6 * math.sin(t * 0.6 + phase)))
            for phase in (0.0, 1.5, 3.0)
        ]
        rear_distances_cm = [d * 100 for d in rear_distances_m]
        rear_states = [d < 0.8 for d in rear_distances_m]

        rpm = max(0.0, min(8000.0, speed * 120.0 + 400.0 * math.sin(t * 1.8)))

        soc = max(0.0, min(100.0, self._soc - dt * (abs(current) / 9000.0)))
        charging_state = current < -20.0 and speed < 5.0
        evse_current = abs(current) * 0.25 if charging_state else 0.0
        evse_frequency = 50.0 + 1.2 * math.sin(t * 0.2)

        self._cell_voltages = [
            max(2.5, min(4.3, 3.85 + 0.12 * soc / 100.0 + 0.01 * math.sin(t * 0.5 + i * 0.35)))
            for i in range(16)
        ]
        cell_min = min(self._cell_voltages)
        cell_max = max(self._cell_voltages)
        cell_delta = cell_max - cell_min

        bms_t1 = max(0.0, min(80.0, batt_temp - 1.2 + 0.4 * math.sin(t * 0.3)))
        bms_t2 = max(0.0, min(80.0, batt_temp + 1.0 + 0.4 * math.sin(t * 0.4 + 1.2)))
        bms_mos = max(0.0, min(100.0, batt_temp + 3.5 + abs(current) * 0.01))
        bms_max = max(bms_t1, bms_t2, bms_mos)

        self._energy_wh += max(0.0, power) * dt / 3600.0

        v_ref = max(44.0, min(54.0, 52.0 + 1.0 * math.sin(t * 0.05)))
        sag = max(0.0, v_ref - voltage)

        warnings = []
        if soc < 20.0:
            warnings.append("battery_low")
        if bms_max > 65.0 or motor_temp > 95.0:
            warnings.append("overtemp")
        if any(d < 0.2 for d in rear_distances_m):
            warnings.append("sensor_close")

        self._speed = speed
        self.speed_changed.emit(self._speed)
        self._battery_pack_voltage = voltage
        self.battery_pack_voltage_changed.emit(self._battery_pack_voltage)
        self._battery_pack_current = current
        self.battery_pack_current_changed.emit(self._battery_pack_current)
        self._instant_power = power
        self.instant_power_changed.emit(self._instant_power)
        self._motor_temperature = motor_temp
        self.motor_temperature_changed.emit(self._motor_temperature)
        self._battery_temperature = batt_temp
        self.battery_temperature_changed.emit(self._battery_temperature)
        self._brake_state = brake_state
        self.brake_state_changed.emit(self._brake_state)
        self._steering_angle = steering_angle
        self.steering_angle_changed.emit(self._steering_angle)

        self._ultrasonic_rear_1_distance = rear_distances_m[0]
        self.ultrasonic_rear_1_distance_changed.emit(self._ultrasonic_rear_1_distance)
        self._ultrasonic_rear_2_distance = rear_distances_m[1]
        self.ultrasonic_rear_2_distance_changed.emit(self._ultrasonic_rear_2_distance)
        self._ultrasonic_rear_3_distance = rear_distances_m[2]
        self.ultrasonic_rear_3_distance_changed.emit(self._ultrasonic_rear_3_distance)

        self._warnings = warnings
        self.warnings_changed.emit(self._warnings)
        self._soc = soc
        self.soc_changed.emit(self._soc)
        self._bms_temp_t1 = bms_t1
        self.bms_temp_t1_changed.emit(self._bms_temp_t1)
        self._bms_temp_t2 = bms_t2
        self.bms_temp_t2_changed.emit(self._bms_temp_t2)
        self._bms_temp_mos = bms_mos
        self.bms_temp_mos_changed.emit(self._bms_temp_mos)
        self._bms_temp_max = bms_max
        self.bms_temp_max_changed.emit(self._bms_temp_max)

        self.cell_voltages_changed.emit(self._cell_voltages)
        self._cell_min = cell_min
        self.cell_min_changed.emit(self._cell_min)
        self._cell_max = cell_max
        self.cell_max_changed.emit(self._cell_max)
        self._cell_delta = cell_delta
        self.cell_delta_changed.emit(self._cell_delta)

        self._charging_state = charging_state
        self.charging_state_changed.emit(self._charging_state)
        self._evse_current = evse_current
        self.evse_current_changed.emit(self._evse_current)
        self._evse_frequency = evse_frequency
        self.evse_frequency_changed.emit(self._evse_frequency)
        self._steering_pot_voltage = steering_pot_voltage
        self.steering_pot_voltage_changed.emit(self._steering_pot_voltage)
        self._steering_current = steering_current
        self.steering_current_changed.emit(self._steering_current)
        self._rpm = rpm
        self.rpm_changed.emit(self._rpm)

        self._ultrasonic_states = rear_states
        self.ultrasonic_states_changed.emit(self._ultrasonic_states)
        self._ultrasonic_distances = rear_distances_cm
        self.ultrasonic_distances_changed.emit(self._ultrasonic_distances)

        self.energy_wh_changed.emit(self._energy_wh)
        self._battery_sag = sag
        self.battery_sag_changed.emit(self._battery_sag)

        if speed < 15.0:
            mode = "ECO"
        elif speed < 40.0:
            mode = "SPORT"
        else:
            mode = "RACE"

        if mode != self._mode:
            self._mode = mode
            self.mode_changed.emit(self._mode)
