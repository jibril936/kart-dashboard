from qtpy.QtCore import QObject, Signal

class StateStore(QObject):
    """Hub central pour toutes les données du véhicule et du BMS."""

    def __init__(self):
        super().__init__()
        # Valeurs par défaut pour éviter les erreurs de type 'None' au démarrage
        self.soc = 0
        self.last_delta = 0.0
        self.last_min = 0.0
        self.last_max = 0.0
        self.is_ready = False

    def get_soc(self):
        """Retourne le pourcentage de batterie (soc) ou 0 par défaut"""
        return getattr(self, 'soc', 0)

    # --- ÉTAT DU VÉHICULE & SYSTÈME ---
    speed_changed = Signal(float)       # Vitesse en km/h
    steer_angle_changed = Signal(float) # Angle de direction
    motor_temp_changed = Signal(float)  # Température moteur
    system_ready = Signal(bool)         # État armé du kart (INFO)
    brake_active = Signal(bool)         # Statut du frein (INFO)
    is_limiting = Signal(bool)          # Mode bridage de puissance (STATUS)

    # --- BMS GLOBAL ---
    soc_changed = Signal(int)           # Pourcentage batterie (0-100)
    pack_voltage_changed = Signal(float)# Tension totale (V)
    pack_current_changed = Signal(float)# Courant instantané (A)
    power_changed = Signal(float)       # Puissance calculée (W ou kW)
    capacity_remaining_ah = Signal(float)
    cycle_count = Signal(int)

    # --- BMS CELLULES ---
    cell_voltages_changed = Signal(list)# Liste des tensions individuelles
    cell_min_v = Signal(float)          # Cellule la plus basse (MIN)
    cell_max_v = Signal(float)          # Cellule la plus haute (MAX)
    cell_delta_v = Signal(float)         # Écart de tension (ΔV)

    # --- BMS TEMPÉRATURES ---
    batt_temp_changed = Signal(float)   # Température principale batterie
    temp_mosfet = Signal(float)         # Température transistors BMS
    temp_sensor_1 = Signal(float)       # Sonde 1 (Cellules)
    temp_sensor_2 = Signal(float)       # Sonde 2 (Cellules)

    # --- ALERTES & ALARMES ---
    bms_alarm = Signal(str)             # Message d'erreur BMS (CRITICAL)
    bms_status_bitmask = Signal(int)    # État brut du BMS
    bms_alarms = Signal(list)           # Liste complète des erreurs actives

    # --- SÉCURITÉ & STATION ---
    ultrasonic_distances = Signal(list) # Capteurs de proximité
    evse_data = Signal(float, float)    # Fréquence et Courant de charge