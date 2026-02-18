import time
import random
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
            # 1. Simulation Pilotage
            speed = 40 + 20 * math.sin(t / 5.0)
            self.state_store.speed_changed.emit(speed)
            self.state_store.pack_current_changed.emit(speed * 2.1)
            
            # 2. États (Ready / Brake)
            self.state_store.system_ready.emit(True)
            self.state_store.brake_active.emit(speed < 35)
            
            # 3. Températures et SOC
            self.state_store.motor_temp_changed.emit(50 + 10 * math.sin(t/10.0))
            self.state_store.batt_temp_changed.emit(35 + 2 * math.sin(t/20.0))
            self.state_store.soc_changed.emit(80)

            # 4. Cellules BMS
            v_list = [3.5 + random.uniform(-0.02, 0.02) for _ in range(16)]
            self.state_store.cell_voltages_changed.emit(v_list)
            self.state_store.cell_min_v.emit(min(v_list))
            self.state_store.cell_max_v.emit(max(v_list))
            self.state_store.cell_delta_v.emit(max(v_list) - min(v_list))

            time.sleep(0.1)

    def stop(self):
        self.running = False
        self.wait()