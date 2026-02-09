from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from src.data.sources.base import DataSource
from src.models.telemetry import Telemetry

try:
    from smbus2 import SMBus  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SMBus = None  # type: ignore


class I2CSource(DataSource):
    """Stub I2C prêt à être complété quand le protocole est défini."""

    def __init__(self, bus: int, address: int, reconnect_delay_s: float = 2.0) -> None:
        self._bus_id = bus
        self._address = address
        self._bus: Optional[SMBus] = None
        self._reconnect_delay_s = reconnect_delay_s
        self._logger = logging.getLogger(__name__)
        self._available = SMBus is not None
        if not self._available:
            self._logger.warning("smbus2 indisponible, I2CSource en mode dégradé")

    def _connect(self) -> None:
        if not self._available:
            return
        if self._bus is None:
            self._bus = SMBus(self._bus_id)
            self._logger.info("Connexion I2C ouverte (bus=%s, address=0x%X)", self._bus_id, self._address)

    def read(self) -> Telemetry:
        if not self._available:
            return Telemetry(
                timestamp=datetime.utcnow(),
                speed_kph=None,
                rpm=None,
                temp_c=None,
                battery_v=None,
                status="ALERTE",
            )
        try:
            self._connect()
            # TODO: implémenter le protocole capteur quand il sera défini.
            # Exemple de lecture brute (à adapter):
            # raw = self._bus.read_i2c_block_data(self._address, 0x00, 6)
            # Parse raw -> telemetry
            return Telemetry(
                timestamp=datetime.utcnow(),
                speed_kph=None,
                rpm=None,
                temp_c=None,
                battery_v=None,
                status="ALERTE",
            )
        except Exception as exc:  # pragma: no cover - dépend du matériel
            self._logger.error("Erreur I2C: %s", exc)
            self.close()
            return Telemetry(
                timestamp=datetime.utcnow(),
                speed_kph=None,
                rpm=None,
                temp_c=None,
                battery_v=None,
                status="ALERTE",
            )

    def close(self) -> None:
        if self._bus is not None:
            try:
                self._bus.close()
            finally:
                self._bus = None
