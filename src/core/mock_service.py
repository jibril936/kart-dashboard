import time
import math
import random
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
            # Simulation Vitesse
            speed = 40 + 20 * math.sin(t / 5.0)
            self.state_store.speed = speed
            self.state_store.speed_changed.emit(speed)
            
            # Simulation Statuts
            self.state_store.system_ready.emit(True)
            self.state_store.brake_active.emit(speed < 32)
            self.state_store.is_limiting.emit(False)
            
            # Note : On ne touche plus au BMS ici.
            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.wait()