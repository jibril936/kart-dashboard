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

    telemetry_received = Signal(float, int, bool)   # vitesse_kmh, mode, frein
    connection_changed = Signal(bool)
    error_changed = Signal(str)
    command_changed = Signal(int, int)              # mode, target_speed

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

        # Dernière vitesse valide pour éviter les chutes brutales si une lecture foire
        self._last_valid_speed = 0.0

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
            print("[I2C ERROR] smbus2 non installé")
            return

        if self._bus is not None:
            return

        try:
            self._bus = SMBus(self.bus_id)
            self._set_connected(True)
            self._set_error("")
            self._timer.start(self.period_ms)
            print(f"[I2C] Bus ouvert bus_id={self.bus_id} addr=0x{self.address:02X}")
        except Exception as exc:
            self._bus = None
            self._set_connected(False)
            self._set_error(f"I2C init failed: {exc}")
            print(f"[I2C ERROR] init failed: {exc}")

    def stop(self):
        self._timer.stop()

        if self._bus is not None:
            try:
                self._bus.close()
            except Exception:
                pass

        self._bus = None
        self._set_connected(False)
        print("[I2C] Bus fermé")

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
            print(f"[I2C CMD] mode={self._mode} target={self._target_speed}")

    def _set_connected(self, state: bool):
        state = bool(state)
        if state != self._connected:
            self._connected = state
            self.connection_changed.emit(state)
            print(f"[I2C] connected={state}")

    def _set_error(self, msg: str):
        msg = str(msg or "")
        if msg != self._last_error:
            self._last_error = msg
            self.error_changed.emit(msg)
            if msg:
                print(f"[I2C ERROR] {msg}")

    def _poll(self):
        if self._bus is None:
            return

        try:
            # 1) Envoi de la commande au slave
            write_msg = i2c_msg.write(self.address, [self._mode, self._target_speed])
            self._bus.i2c_rdwr(write_msg)

            # Petite pause pour laisser le slave préparer la réponse
            time.sleep(0.002)

            # 2) Lecture télémétrie
            #
            # On essaye d'abord 6 octets :
            #   float vitesse (4) + mode (1) + frein (1)
            # Si ça ne va pas, on essaie 4 octets :
            #   uint16 vitesse_x100 (2) + mode (1) + frein (1)
            raw6 = self._read_exactly(6)
            vitesse, mode, frein = self._decode_telemetry(raw6)

            if vitesse is None:
                raw4 = self._read_exactly(4)
                vitesse, mode, frein = self._decode_telemetry(raw4)

            if vitesse is None:
                raise ValueError("Impossible de décoder la télémétrie I2C")

            # Filtrage minimal
            if mode not in (self.MODE_MANUAL, self.MODE_AUTO, self.MODE_NEUTRAL):
                raise ValueError(f"mode invalide: {mode}")

            if vitesse < 0.0 or vitesse > 200.0:
                raise ValueError(f"vitesse hors plage: {vitesse}")

            self._last_valid_speed = float(vitesse)
            self._set_connected(True)
            self._set_error("")

            print(f"[I2C RAW OK] vitesse={vitesse:.2f} mode={mode} frein={bool(frein)}")
            self.telemetry_received.emit(float(vitesse), int(mode), bool(frein))

        except Exception as exc:
            self._set_connected(False)
            self._set_error(f"I2C poll failed: {exc}")
            print(f"[I2C ERROR] poll failed: {exc}")

            # On garde au moins le mode courant et la dernière vitesse connue
            self.telemetry_received.emit(float(self._last_valid_speed), int(self._mode), False)

    def _read_exactly(self, size: int) -> bytes:
        read_msg = i2c_msg.read(self.address, size)
        self._bus.i2c_rdwr(read_msg)
        raw = bytes(read_msg)

        if len(raw) != size:
            raise ValueError(f"lecture I2C incomplète: attendu={size} reçu={len(raw)}")

        return raw

    def _decode_telemetry(self, raw: bytes):
        """
        Retourne (vitesse, mode, frein) ou (None, None, None) si non reconnu.
        """

        # Debug hex
        hex_dump = " ".join(f"{b:02X}" for b in raw)
        print(f"[I2C BYTES] len={len(raw)} data={hex_dump}")

        # Format 1: 6 octets
        # <fBB = float little-endian + uint8 + uint8
        if len(raw) == 6:
            try:
                vitesse, mode, frein = struct.unpack("<fBB", raw)

                # Validation légère
                if not (0.0 <= float(vitesse) <= 200.0):
                    return None, None, None
                if mode not in (0, 1, 2):
                    return None, None, None
                if frein not in (0, 1):
                    return None, None, None

                return float(vitesse), int(mode), int(frein)
            except Exception:
                return None, None, None

        # Format 2: 4 octets
        # <HBB = uint16 little-endian + uint8 + uint8
        if len(raw) == 4:
            try:
                vitesse_x100, mode, frein = struct.unpack("<HBB", raw)
                vitesse = float(vitesse_x100) / 100.0

                if not (0.0 <= vitesse <= 200.0):
                    return None, None, None
                if mode not in (0, 1, 2):
                    return None, None, None
                if frein not in (0, 1):
                    return None, None, None

                return vitesse, int(mode), int(frein)
            except Exception:
                return None, None, None

        return None, None, None