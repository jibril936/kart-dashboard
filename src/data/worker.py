from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from src.data.sources.base import DataSource
from src.models.telemetry import Telemetry


class DataWorker(QObject):
    telemetry_received = pyqtSignal(Telemetry)

    def __init__(self, source: DataSource, refresh_hz: float) -> None:
        super().__init__()
        self._source = source
        self._interval_ms = int(1000 / refresh_hz) if refresh_hz > 0 else 100
        self._timer: Optional[QTimer] = None
        self._logger = logging.getLogger(__name__)

    def start(self) -> None:
        self._timer = QTimer()
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._poll)
        self._timer.start()

    def stop(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer.deleteLater()
        try:
            self._source.close()
        except Exception as exc:
            self._logger.error("Erreur fermeture source: %s", exc)

    def _poll(self) -> None:
        telemetry = self._source.read()
        self.telemetry_received.emit(telemetry)
