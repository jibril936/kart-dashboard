from qtpy.QtCore import QObject, Signal, QTimer


class BorneI2CService(QObject):
    connection_changed = Signal(bool)
    error_changed = Signal(str)
    telemetry_changed = Signal(object)

    def __init__(self, bus_id: int = 1, address: int = 0x56, parent=None):
        super().__init__(parent)
        self.bus_id = bus_id
        self.address = address
        self._connected = False
        self._last_error = ""
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._emit_snapshot)

    def start(self):
        self._set_connected(True)
        self._set_error("")
        self._emit_snapshot()
        if not self._timer.isActive():
            self._timer.start()

    def stop(self):
        if self._timer.isActive():
            self._timer.stop()
        self._set_connected(False)

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

    def _build_snapshot(self) -> dict:
        connected = bool(self._connected)
        return {
            "connected": connected,
            "state": "connected" if connected else "disconnected",
            "status": "stub",
            "error": self._last_error,
            "current_limit": 0.0,
            "cable_limit": 0.0,
            "cp_duty": 0.0,
            "cp_freq": 1000.0,
            "cp_neg": False,
            "cp_ok": connected,
            "pp_voltage": 0.0,
            "sector_present": connected,
            "bus_id": self.bus_id,
            "address": self.address,
        }

    def _emit_snapshot(self):
        self.telemetry_changed.emit(self._build_snapshot())