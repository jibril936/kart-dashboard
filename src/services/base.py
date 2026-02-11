from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.state import VehicleTechState


class DataService(ABC):
    @abstractmethod
    def sample(self) -> VehicleTechState:
        raise NotImplementedError
