from __future__ import annotations

import math
import time

from .base_data_service import BaseDataService


class MockService(BaseDataService):
    """
    Simulation UNIQUEMENT:
      - vitesse
      - température moteur
    Aucun signal BMS ici.
    """

    def __init__(self, state_store, parent=None) -> None:
        super().__init__(state_store, parent=parent)

    def run(self) -> None:
        self._running = True
        t0 = time.time()

        while self._running:
            t = time.time() - t0

            # Vitesse: oscillation "track"
            speed = 18.0 + 22.0 * (0.5 + 0.5 * math.sin(t * 0.55))
            self.state_store.set_speed(speed)

            # Temp moteur: suit l'effort
            motor_temp = 32.0 + (speed / 70.0) * 55.0 + 6.0 * math.sin(t * 0.18)
            self.state_store.set_motor_temp(motor_temp)

            time.sleep(0.10)
