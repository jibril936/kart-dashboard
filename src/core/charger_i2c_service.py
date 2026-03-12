from qtpy.QtCore import QObject, Signal


class ChargerI2CService(QObject):
    connection_changed = Signal(bool)
    error_changed = Signal(str)

    def __init__(self, bus_id: int = 1, address: int = 0x57, parent=None):
        super().__init__(parent)
        self.bus_id = bus_id
        self.address = address
        self._connected = False
        self._last_error = ""

    def start(self):
        self._set_connected(True)
        self._set_error("")

    def stop(self):
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