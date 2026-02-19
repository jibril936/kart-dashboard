import time
import math
from qtpy.QtCore import QThread

class MockService(QThread):
    def __init__(self, state_store):
        super().__init__()
        self.state_store = state_store
        self.running = True

    def run(self):
        t = 0
        while self.running:
            t += 0.1
            # --- ON NE SIMULE QUE LA VITESSE ET L'ÉTAT DU KART ---
            speed = 40 + 20 * math.sin(t / 5.0)
            self.state_store.speed_changed.emit(speed)
            self.state_store.system_ready.emit(True)
            self.state_store.brake_active.emit(speed < 35)
            self.state_store.motor_temp_changed.emit(45 + 5 * math.sin(t/10.0))
            time.sleep(0.1)