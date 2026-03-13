import struct
import time
from qtpy.QtCore import QObject, QTimer, Signal

try:
    from smbus2 import SMBus, i2c_msg
except Exception:
    SMBus = None
    i2c_msg = None


class VariatorI2CService(QObject):
    MODE_MANUAL = 0
    MODE_AUTO = 1
    MODE_NEUTRAL = 2

    telemetry_received = Signal(float, int, bool)  # vitesse_kmh, mode, frein
    connection_changed = Signal(bool)
    error_changed = Signal(str)
    command_changed = Signal(int, int)  # mode, target_speed

    def __init__(self, bus_id: int = 1, address: int = 0x22, period_ms: int = 50, parent=None):
        super().__init__(parent)
        self.bus_id = int(bus_id)
        self.address = int(address)
        self.period_ms = int(period_ms)

        self._bus = None
        self._connected = False
        self._last_error = ""
        self._mode = self.MODE_NEUTRAL
        self._target_speed = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)

    @property
    def current_mode(self) -> int:
        return self._mode

    @property
    def current_target(self) -> int:
        return self._target_speed

    def start(self):
        if SMBus is None or i2c_msg is None:
            self._set_connected(False)
            self._set_error("smbus2 non installé")
            return

        if self._bus is not None:
            return

        try:
            self._bus = SMBus(self.bus_id)
            self._set_connected(True)
            self._set_error("")
            self._timer.start(self.period_ms)
        except Exception as exc:
            self._bus = None
            self._set_connected(False)
            self._set_error(f"I2C init failed: {exc}")

    def stop(self):
        self._timer.stop()
        if self._bus is not None:
            try:
                self._bus.close()
            except Exception:
                pass
        self._bus = None
        self._set_connected(False)

    def set_command(self, mode: int, target_speed: int):
        try:
            mode = int(mode)
        except Exception:
            mode = self.MODE_NEUTRAL

        if mode not in (self.MODE_MANUAL, self.MODE_AUTO, self.MODE_NEUTRAL):
            mode = self.MODE_NEUTRAL

        try:
            target_speed = int(target_speed)
        except Exception:
            target_speed = 0

        target_speed = max(0, min(255, target_speed))

        changed = (mode != self._mode) or (target_speed != self._target_speed)
        self._mode = mode
        self._target_speed = target_speed

        if changed:
            self.command_changed.emit(self._mode, self._target_speed)

    def _set_connected(self, state: bool):
        state = bool(state)
        if state != self._connected:
            self._connected = state
            self.connection_changed.emit(state)

    def _set_error(self, msg: str):
        msg = str(msg or "")
        if msg != self._last_error:
            self._last_error = msg
            self.error_changed.emit(msg)

    def _poll(self):
        if self._bus is None:
            return

        try:
            # Pi -> ATmega : [mode, vitesseCible]
            write_msg = i2c_msg.write(self.address, [self._mode, self._target_speed])
            self._bus.i2c_rdwr(write_msg)

            time.sleep(0.002)

            # ATmega -> Pi : [uint16 vitesse_x100][uint8 mode][uint8 frein]
            read_msg = i2c_msg.read(self.address, 4)
            self._bus.i2c_rdwr(read_msg)
            raw = bytes(read_msg)

            if len(raw) != 4:
                raise ValueError(f"taille télémétrie invalide: {len(raw)}")

            vitesse_x100, mode, frein = struct.unpack("<HBB", raw)
            vitesse = float(vitesse_x100) / 100.0

            if mode not in (self.MODE_MANUAL, self.MODE_AUTO, self.MODE_NEUTRAL):
                raise ValueError(f"mode invalide: {mode}")

            if vitesse < 0.0 or vitesse > 120.0:
                raise ValueError(f"vitesse hors plage: {vitesse}")

            self._set_connected(True)
            self._set_error("")
            self.telemetry_received.emit(vitesse, int(mode), bool(frein))

        except Exception as exc:
            self._set_connected(False)
            self._set_error(f"I2C poll failed: {exc}")
            self.telemetry_received.emit(0.0, self._mode, False)