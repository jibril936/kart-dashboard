from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.telemetry import Telemetry


class DataSource(ABC):
    """Contract for telemetry providers (I2C/Serial/CAN/BLE/Simulated)."""

    def start(self) -> None:
        """Optional hook to initialize hardware resources."""

    def stop(self) -> None:
        """Optional hook to release hardware resources."""

    @abstractmethod
    def read(self) -> Telemetry:
        """Read one telemetry sample."""
        raise NotImplementedError
