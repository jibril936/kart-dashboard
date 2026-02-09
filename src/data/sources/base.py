from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from src.models.telemetry import Telemetry


class DataSource(ABC):
    """Interface commune pour toutes les sources de données."""

    @abstractmethod
    def read(self) -> Telemetry:
        raise NotImplementedError

    def close(self) -> None:
        return None


class SupportsClose(Protocol):
    def close(self) -> None:
        ...
