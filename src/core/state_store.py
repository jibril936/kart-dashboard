from PyQt6.QtCore import QObject, pyqtSignal


class StateStore(QObject):
    """Central state and signal hub for dashboard data updates."""

    # Vehicle
    speed_changed = pyqtSignal(float)
    steer_angle_changed = pyqtSignal(float)
    brake_status = pyqtSignal(bool)
    motor_temp_changed = pyqtSignal(float)

    # BMS
    soc_changed = pyqtSignal(int)
    pack_voltage_changed = pyqtSignal(float)
    pack_current_changed = pyqtSignal(float)
    cell_voltages_changed = pyqtSignal(list)
    bms_temp_changed = pyqtSignal(float)

    # Safety
    ultrasonic_distances = pyqtSignal(list)

    # Station
    evse_data = pyqtSignal(float, float)
