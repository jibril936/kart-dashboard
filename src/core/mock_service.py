import time
import random
from qtpy.QtCore import QThread

class MockService(QThread):
    """Simulateur de données pour tester l'interface sans kart réel."""
    def __init__(self, state_store):
        super().__init__()
        self.state_store = state_store
        self.running = True

    def run(self):
        print("--- Démarrage du simulateur (Mock) ---")
        speed = 0
        soc = 80
        temp_m = 20
        temp_b = 20
        
        while self.running:
            # 1. Simulation Vitesse et Puissance
            speed = (speed + random.uniform(-1, 2)) % 70
            current = (speed * 2.5) + random.uniform(-5, 5)
            
            # 2. Simulation Températures (montée progressive)
            temp_m = min(100, temp_m + 0.05)
            temp_b = min(60, temp_b + 0.02)
            
            # 3. Envoi des signaux de base
            self.state_store.speed_changed.emit(speed)
            self.state_store.pack_current_changed.emit(current)
            self.state_store.motor_temp_changed.emit(temp_m)
            self.state_store.batt_temp_changed.emit(temp_b)
            self.state_store.soc_changed.emit(int(soc))
            
            # 4. Simulation Freinage et Alertes
            braking = random.choice([True, False, False, False])
            self.state_store.brake_active.emit(braking) # CORRIGÉ : brake_active au lieu de brake_status
            
            if braking:
                self.state_store.system_ready.emit(True) # Juste pour test
            
            # 5. Simulation BMS Cellules (Page Expert)
            cells = [3.5 + random.uniform(-0.05, 0.05) for _ in range(16)]
            min_v = min(cells)
            max_v = max(cells)
            self.state_store.cell_voltages_changed.emit(cells)
            self.state_store.cell_min_v.emit(min_v)
            self.state_store.cell_max_v.emit(max_v)
            self.state_store.cell_delta_v.emit(max_v - min_v)

            # Simulation alerte surchauffe
            if temp_m > 85:
                self.state_store.bms_alarm.emit("MOTOR OVERHEAT")
            elif soc < 15:
                self.state_store.bms_alarm.emit("LOW BATTERY")
            else:
                self.state_store.bms_alarm.emit("") # Clear alerte

            time.sleep(0.1) # 10Hz

    def stop(self):
        self.running = False
        self.wait()