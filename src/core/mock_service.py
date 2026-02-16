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

        while self._running:
            t += 0.1

            # 1. Dynamique du véhicule (SIMULÉ)
            speed_target = 28.0 + 22.0 * math.sin(t / 3.0)
            speed += (speed_target - speed) * 0.15
            steer_angle = 18.0 * math.sin(t / 2.5)
            braking = speed_target < speed - 1.5
            motor_temp = 45.0 + (speed / 80.0) * 35.0 + random.uniform(-0.8, 0.8)

            # 2. Sécurité / Ultrasons (SIMULÉ)
            ultrasonic = [
                round(0.7 + 0.4 * abs(math.sin(t * 0.9)) + random.uniform(-0.03, 0.03), 2),
                round(0.9 + 0.3 * abs(math.sin(t * 1.1 + 0.7)) + random.uniform(-0.03, 0.03), 2),
                round(0.8 + 0.35 * abs(math.sin(t * 1.3 + 1.2)) + random.uniform(-0.03, 0.03), 2),
            ]

            # 3. Station de charge (SIMULÉ)
            evse_freq = 50.0 + random.uniform(-0.08, 0.08)
            evse_current = 16.0 + 6.0 * abs(math.sin(t / 5.0)) + random.uniform(-0.2, 0.2)

            # --- PUBLICATION AU STORE ---
            # On envoie tout SAUF les données BMS (Voltage, SOC, Courant) 
            # car elles viennent maintenant de ton vrai HardwareService
            self.state_store.speed_changed.emit(round(max(0.0, speed), 2))
            self.state_store.steer_angle_changed.emit(round(steer_angle, 2))
            self.state_store.brake_status.emit(braking)
            self.state_store.motor_temp_changed.emit(round(motor_temp, 2))

            # Signaux de sécurité et station
            self.state_store.ultrasonic_distances.emit(ultrasonic)
            self.state_store.evse_data.emit(round(evse_freq, 2), round(evse_current, 2))

            time.sleep(0.1)