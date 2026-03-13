from qtpy.QtCore import QObject, QTimer, Signal

try:
    from smbus2 import SMBus, i2c_msg
except Exception:
    SMBus = None
    i2c_msg = None


class ChargerI2CService(QObject):
    connection_changed = Signal(bool)
    error_changed = Signal(str)
    telemetry_changed = Signal(object)  # dict

    def __init__(self, bus_id: int = 1, address: int = 0x24, period_ms: int = 250, parent=None):
        super().__init__(parent)
        self.bus_id = int(bus_id)
        self.address = int(address)
        self.period_ms = int(period_ms)

        self._bus = None
        self._connected = False
        self._last_error = ""

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)

    def start(self):
        if SMBus is None or i2c_msg is None:
            self._set_connected(False)
            self._set_error("smbus2 non installé")
            self.telemetry_changed.emit(self._offline_snapshot())
            return

        if self._bus is not None:
            return

        try:
            self._bus = SMBus(self.bus_id)
            self._set_connected(False)
            self._set_error("")
            self._timer.start(self.period_ms)
            self.telemetry_changed.emit(self._offline_snapshot())
        except Exception as exc:
            self._bus = None
            self._set_connected(False)
            self._set_error(f"I2C init failed: {exc}")
            self.telemetry_changed.emit(self._offline_snapshot())

    def stop(self):
        self._timer.stop()

        if self._bus is not None:
            try:
                self._bus.close()
            except Exception:
                pass

        self._bus = None
        self._set_connected(False)
        self.telemetry_changed.emit(self._offline_snapshot())

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

    @staticmethod
    def _offline_snapshot():
        return {
            "connected": False,
            "state": "OFFLINE",
            "stage": "OFF",
            "voltage": 0.0,
            "current": 0.0,
            "power_kw": 0.0,
            "on": 0,
            "boost": 0,
            "equalize": 0,
            "float": 0,
            "failure": 0,
        }

    @staticmethod
    def _clamp_led(v):
        try:
            v = int(v)
        except Exception:
            return 0
        return 0 if v < 0 else 2 if v > 2 else v

    def _parse_frame(self, raw: bytes):
        # Trame attendue :
        # [on, boost, equalize, float, failure]
        if len(raw) != 5:
            raise ValueError(f"taille chargeur invalide: {len(raw)}")

        vals = [int(x) for x in raw]
        if any(v not in (0, 1, 2) for v in vals):
            raise ValueError(f"trame chargeur invalide: {vals}")

        on, boost, equalize, float_led, failure = vals

        connected = any(v > 0 for v in vals)

        return {
            "connected": connected,
            "state": "READY" if connected else "OFFLINE",
            "stage": (
                "FAULT" if failure else
                "FLOAT" if float_led else
                "EQUALIZE" if equalize else
                "BOOST" if boost else
                "READY" if on else
                "OFF"
            ),
            "voltage": 0.0,
            "current": 0.0,
            "power_kw": 0.0,
            "on": self._clamp_led(on),
            "boost": self._clamp_led(boost),
            "equalize": self._clamp_led(equalize),
            "float": self._clamp_led(float_led),
            "failure": self._clamp_led(failure),
        }

    def _poll(self):
        if self._bus is None:
            return

        try:
            msg = i2c_msg.read(self.address, 5)
            self._bus.i2c_rdwr(msg)
            raw = bytes(msg)

            snap = self._parse_frame(raw)

            self._set_connected(bool(snap["connected"]))
            self._set_error("")
            self.telemetry_changed.emit(snap)

        except Exception as exc:
            self._set_connected(False)
            self._set_error(f"I2C poll failed: {exc}")
            self.telemetry_changed.emit(self._offline_snapshot())