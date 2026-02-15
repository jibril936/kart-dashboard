from __future__ import annotations

import time

from .base_data_service import BaseDataService


class HardwareService(BaseDataService):
    """Placeholder for real hardware data acquisition (I2C, CAN, GPIO)."""

    def run(self) -> None:
        self._running = True
        while self._running:
            print("Lecture I2C... véhicule")
            print("Lecture I2C... BMS")
            print("Lecture I2C... sécurité")
            print("Lecture I2C... station")
            time.sleep(0.5)
