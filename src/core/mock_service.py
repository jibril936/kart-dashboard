from __future__ import annotations

import math
import time

from .base_data_service import BaseDataService


class MockService(BaseDataService):
    """
    Simulation UNIQUEMENT:
      - vitesse
      - température moteur
      - chargeur (Skylla TG): état de branchement + états des LEDs (on/boost/equalize/float/failure)
    """

    LED_OFF = 0
    LED_ON = 1
    LED_BLINK = 2

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

            # -------------------------
            # Charger (Skylla TG) - SIMU
            # -------------------------
            # 45s branché / 15s débranché
            plugged = (t % 60.0) < 45.0
            if hasattr(self.state_store, "set_charger_connected"):
                self.state_store.set_charger_connected(plugged)

            if hasattr(self.state_store, "set_charger_leds"):
                if not plugged:
                    # Tout éteint
                    self.state_store.set_charger_leds()
                else:
                    phase = t % 45.0

                    # Cycle: ON -> BOOST -> EQUALIZE -> FLOAT
                    on = self.LED_ON
                    boost = self.LED_OFF
                    equalize = self.LED_OFF
                    float_ = self.LED_OFF
                    failure = self.LED_OFF

                    if phase < 2.0:
                        on = self.LED_BLINK
                    elif phase < 18.0:
                        boost = self.LED_ON
                    elif phase < 28.0:
                        equalize = self.LED_ON
                    else:
                        float_ = self.LED_ON

                    # Mini fenêtre "défaut" pour tester UI
                    if 38.0 <= phase < 41.0:
                        on = self.LED_BLINK
                        boost = self.LED_OFF
                        equalize = self.LED_OFF
                        float_ = self.LED_OFF
                        failure = self.LED_ON
                    elif 41.0 <= phase < 45.0:
                        failure = self.LED_BLINK

                    self.state_store.set_charger_leds(
                        on=on,
                        boost=boost,
                        equalize=equalize,
                        float_=float_,
                        failure=failure,
                    )

            time.sleep(0.10)