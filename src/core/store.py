from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from src.core.state import VehicleTechState


class StateStore(QObject):
    """Single source of truth for UI and services."""

    state_changed = pyqtSignal(object)

    def __init__(self, initial_state: VehicleTechState) -> None:
        super().__init__()
        self._state = initial_state

    @property
    def state(self) -> VehicleTechState:
        return self._state

    def update(self, state: VehicleTechState) -> None:
        self._state = state
        self.state_changed.emit(state)
