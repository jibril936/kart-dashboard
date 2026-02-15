from __future__ import annotations

import math
import random
import time

from .base_data_service import BaseDataService


class MockService(BaseDataService):
    """Simulated telemetry source for local development."""

    def run(self) -> None:
        self._running = True

        t = 0.0
        speed = 0.0
        pack_voltage = 403.2
        soc = 1.0

        while self._running:
            t += 0.1

            # Vehicle dynamics
            speed_target = 28.0 + 22.0 * math.sin(t / 3.0)
            speed += (speed_target - speed) * 0.15
            steer_angle = 18.0 * math.sin(t / 2.5)
            braking = speed_target < speed - 1.5
            motor_temp = 45.0 + (speed / 80.0) * 35.0 + random.uniform(-0.8, 0.8)

            # BMS values
            soc = max(0.0, soc - 0.00015)
            pack_voltage = max(320.0, pack_voltage - 0.0015 + random.uniform(-0.015, 0.015))
            pack_current = 12.0 + speed * 1.1 + random.uniform(-4.0, 4.0)
            cell_nominal = 3.2 + soc * 0.95
            cell_voltages = [round(cell_nominal + random.uniform(-0.015, 0.015), 3) for _ in range(8)]
            bms_temp = 31.0 + speed * 0.2 + random.uniform(-1.2, 1.2)

            # Safety (3 ultrasonic sensors)
            ultrasonic = [
                round(0.7 + 0.4 * abs(math.sin(t * 0.9)) + random.uniform(-0.03, 0.03), 2),
                round(0.9 + 0.3 * abs(math.sin(t * 1.1 + 0.7)) + random.uniform(-0.03, 0.03), 2),
                round(0.8 + 0.35 * abs(math.sin(t * 1.3 + 1.2)) + random.uniform(-0.03, 0.03), 2),
            ]

            # EVSE station
            evse_freq = 50.0 + random.uniform(-0.08, 0.08)
            evse_current = 16.0 + 6.0 * abs(math.sin(t / 5.0)) + random.uniform(-0.2, 0.2)

            # Publish to store
            self.state_store.speed_changed.emit(round(max(0.0, speed), 2))
            self.state_store.steer_angle_changed.emit(round(steer_angle, 2))
            self.state_store.brake_status.emit(braking)
            self.state_store.motor_temp_changed.emit(round(motor_temp, 2))

            self.state_store.pack_voltage_changed.emit(round(pack_voltage, 2))
            self.state_store.pack_current_changed.emit(round(pack_current, 2))
            self.state_store.cell_voltages_changed.emit(cell_voltages)
            self.state_store.bms_temp_changed.emit(round(bms_temp, 2))

            self.state_store.ultrasonic_distances.emit(ultrasonic)
            self.state_store.evse_data.emit(round(evse_freq, 2), round(evse_current, 2))

            time.sleep(0.1)
