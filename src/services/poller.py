from __future__ import annotations

import time

from src.qt_compat import QObject, QTimer, pyqtSignal
from src.services.base import DataService


class DataPoller(QObject):
    sample_ready = pyqtSignal(object, int)

    def __init__(self, service: DataService, data_hz: float) -> None:
        super().__init__()
        self._service = service
        self._timer = QTimer(self)
        self._timer.setInterval(max(5, int(1000 / data_hz)))
        self._timer.timeout.connect(self._tick)
        self._last_emit = 0.0

    def start(self) -> None:
        self._service.start()
        self._last_emit = time.monotonic()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self._service.stop()

    def _tick(self) -> None:
        sample = self._service.read()
        now = time.monotonic()
        stale_ms = int((now - self._last_emit) * 1000)
        self._last_emit = now
        self.sample_ready.emit(sample, stale_ms)
