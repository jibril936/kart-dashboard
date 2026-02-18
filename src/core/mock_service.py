import time
import random
import math
from qtpy.QtCore import QThread

class MockService(QThread):
    """Simulateur bridé : Il ne gère QUE la vitesse et les statuts système."""
    def __init__(self, state_store):
        super().__init__()
        self.state_store = state_store
        self.running = True

    def run(self):
        t = 0
        while self.running:
            t += 0.1
            
            # 1. Simulation Vitesse (On simule un kart qui roule un peu)
            speed = 35 + 15 * math.sin(t / 5.0)
            self.state_store.speed_changed.emit(speed)
            
            # 2. États système (Ceux que tu n'as pas encore en Hardware)
            self.state_store.system_ready.emit(True)
            self.state_store.brake_active.emit(speed < 32)
            self.state_store.is_limiting.emit(False)
            
            # 3. Température Moteur (Simulée car pas de sonde moteur RS485)
            self.state_store.motor_temp_changed.emit(45 + 5 * math.sin(t/10.0))

            # --- AUCUNE ÉMISSION BMS ICI ---
            # Ni courant, ni tension, ni cellules, ni SOC.
            # Tout cela DOIT venir du HardwareService.

            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.wait()