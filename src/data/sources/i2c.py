from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from src.data.sources.base import DataSource
from src.models.telemetry import SourceState, Telemetry

try:
    from smbus2 import SMBus  # type: ignore
except Exception:  # pragma: no cover
    SMBus = None  # type: ignore


class I2CDataSource(DataSource):
    """I2C scaffold. Parsing/protocol can be added without touching UI."""

    def __init__(self, bus: int, address: int) -> None:
        self._bus_id = bus
        self._address = address
        self._bus: Optional[SMBus] = None
        self._logger = logging.getLogger(__name__)

    @property
    def is_available(self) -> bool:
        return SMBus is not None

    def start(self) -> None:
        if SMBus is None:
            self._logger.warning("smbus2 not installed; I2CDataSource running in stub mode")
            return
        if self._bus is None:
            self._bus = SMBus(self._bus_id)

    def stop(self) -> None:
        if self._bus is not None:
            self._bus.close()
            self._bus = None

    def read(self) -> Telemetry:
        if SMBus is None:
            return Telemetry(timestamp=datetime.utcnow(), source_state=SourceState.ERROR, alerts=["I2C unavailable: install smbus2"])

        try:
            if self._bus is None:
                self.start()
            # TODO: replace with actual register protocol decoding.
            # raw = self._bus.read_i2c_block_data(self._address, 0x00, 16)
            return Telemetry(
                timestamp=datetime.utcnow(),
                source_state=SourceState.TIMEOUT,
                alerts=[f"I2C stub active @ 0x{self._address:02X}", "Protocol parser not implemented"],
            )
        except Exception as exc:  # pragma: no cover
            self._logger.exception("I2C read failed: %s", exc)
            self.stop()
            return Telemetry(timestamp=datetime.utcnow(), source_state=SourceState.ERROR, alerts=[str(exc)])
