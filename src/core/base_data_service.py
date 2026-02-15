from __future__ import annotations

import abc
from abc import ABC, abstractmethod

from PyQt6.QtCore import QThread

from .state_store import StateStore


class QABCMeta(type(QThread), abc.ABCMeta):
    """Meta-class bridging PyQt's QObject meta-type and ABCMeta."""


class BaseDataService(QThread, ABC, metaclass=QABCMeta):
    """Threaded service base that publishes data to the shared StateStore."""

    def __init__(self, state_store: StateStore, parent=None) -> None:
        super().__init__(parent)
        self.state_store = state_store
        self._running = False

    def stop(self) -> None:
        self._running = False
        self.wait()

    @abstractmethod
    def run(self) -> None:
        """Produce data and emit updates to the StateStore."""
