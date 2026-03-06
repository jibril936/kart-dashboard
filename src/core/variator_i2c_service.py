import struct
import time

from qtpy.QtCore import QObject, QTimer, Signal

try:
    from smbus2 import SMBus, i2c_msg
except Exception:
    SMBus = None
    i2c_msg = None


class VariatorI2CService(QObject):
    telemetry_received = Signal(float, int, bool)   # vitesse_kmh, mode, frein
    connection_changed = Signal(bool)
    error_changed = Signal(str)

    def __init__(self, bus_id: int = 1, address: int = 0x22, period_ms: int = 50, parent=None):
        super().__init__(parent)
        self.bus_id = bus_id
        self.address = address
        self.period_ms = period_ms

        self._bus = None
        self._connected = False
        self._last_error = ""

        self._mode = 0
        self._target_speed = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)

    def start(self):
        if SMBus is None or i2c_msg is None:
            self._set_error("smbus2 non installé")
            self._set_connected(False)
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
        mode = 1 if int(mode) else 0
        target_speed = max(0, min(255, int(target_speed)))
        self._mode = mode
        self._target_speed = target_speed

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
            # Pi -> ATmega : 2 octets [mode, vitesseCible]
            write_msg = i2c_msg.write(self.address, [self._mode, self._target_speed])
            self._bus.i2c_rdwr(write_msg)

            # petite pause pour laisser la carte mettre à jour la télémétrie
            time.sleep(0.001)

            # ATmega -> Pi : 6 octets [float vitesse][uint8 mode][uint8 frein]
            read_msg = i2c_msg.read(self.address, 6)
            self._bus.i2c_rdwr(read_msg)
            raw = bytes(read_msg)

            if len(raw) != 6:
                raise ValueError(f"taille télémétrie invalide: {len(raw)}")

            vitesse, mode, frein = struct.unpack("<fBB", raw)
    
            self._set_connected(True)
            self._set_error("")
            self.telemetry_received.emit(float(vitesse), int(mode), bool(frein))

        except Exception as exc:
            self._set_connected(False)
            self._set_error(f"I2C poll failed: {exc}")