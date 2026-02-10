from __future__ import annotations

import logging

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.data.sources.base import DataSource
from src.models.telemetry import Telemetry


class DataWorker(QObject):
    telemetry_received = pyqtSignal(Telemetry)

    def __init__(self, source: DataSource, refresh_hz: float) -> None:
        super().__init__()
        self._source = source
        self._interval_ms = max(10, int(1000 / refresh_hz)) if refresh_hz > 0 else 100
        self._timer = QTimer(self)
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._poll)
        self._logger = logging.getLogger(__name__)

    def start(self) -> None:
        self._source.start()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        try:
            self._source.stop()
        except Exception as exc:
            self._logger.exception("Source stop failed: %s", exc)

    def _poll(self) -> None:
        telemetry = self._source.read()
        self.telemetry_received.emit(telemetry)
