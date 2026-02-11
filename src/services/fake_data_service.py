from __future__ import annotations

import math
import random
import time
from dataclasses import replace

from src.core.state import VehicleTechState, default_state, utc_now_ms
from src.services.base import DataService


class FakeDataService(DataService):
    """Desktop fake source with multiple simple scenarios."""

    def __init__(self, scenario: str = "normal") -> None:
        self.scenario = scenario
        self._t0 = time.monotonic()
        self._state = default_state()

    def sample(self) -> VehicleTechState:
        t = time.monotonic() - self._t0
        now = utc_now_ms()

        base_speed = 12.0 + 10.0 * (0.5 + 0.5 * math.sin(0.35 * t))
        base_rpm = int(900 + 1200 * (0.5 + 0.5 * math.sin(0.35 * t + 0.5)))

        self._state.battery_voltage_V = 52.0 + 0.35 * math.sin(0.3 * t)
        self._state.battery_charge_current_A = 8.0 + 1.5 * math.sin(0.5 * t)
        self._state.charging_state = True

        self._state.station_frequency_Hz = 50.0 + 0.08 * math.sin(0.2 * t)
        self._state.station_current_A = 16.0 + 0.6 * math.sin(0.6 * t)

        self._state.steering_pot_voltage_V = 2.5 + 0.6 * math.sin(0.9 * t)
        self._state.steering_angle_deg = 30.0 * math.sin(0.9 * t)
        self._state.steering_current_A = 1.2 + 0.4 * abs(math.sin(0.9 * t))

        self._state.speed_kmh = base_speed
        self._state.rpm = base_rpm
        self._state.brake_state = 0.0 if random.random() > 0.96 else 18.0

        self._state.motor_temp_C = 40.0 + 5.0 * (0.5 + 0.5 * math.sin(0.1 * t))

        if self.scenario == "battery_drop":
            self._state.battery_voltage_V = 50.0 - min(6.0, 0.22 * t)
            self._state.battery_charge_current_A = max(0.0, 8.0 - 0.35 * t)
            self._state.charging_state = self._state.battery_charge_current_A > 1.0
        elif self.scenario == "overheat":
            self._state.motor_temp_C = min(105.0, 72.0 + 0.8 * t)
            self._state.speed_kmh = base_speed + 12.0
            self._state.rpm = min(6800, base_rpm + 1400)
        elif self.scenario == "sensor_ko":
            self._state.steering_pot_voltage_V = 4.9
            self._state.station_frequency_Hz = 0.0
            self._state.station_current_A = 0.0

        self._state.sample_timestamp_ms = now
        for key in self._state.field_timestamps_ms:
            self._state.field_timestamps_ms[key] = now

        return replace(self._state)
