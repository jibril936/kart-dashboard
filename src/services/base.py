from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.types import TelemetrySample


class DataService(ABC):
    def start(self) -> None:
        """Optional startup hook."""

    def stop(self) -> None:
        """Optional stop hook."""

    @abstractmethod
    def read(self) -> TelemetrySample:
        raise NotImplementedError
