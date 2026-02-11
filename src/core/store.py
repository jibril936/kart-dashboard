from __future__ import annotations

from collections import deque

from src.core.types import DashboardState, RollingStats, TelemetrySample
from src.qt_compat import QObject, pyqtSignal


class StateStore(QObject):
    state_changed = pyqtSignal(object)

    def __init__(self, initial_state: DashboardState) -> None:
        super().__init__()
        self._state = initial_state
        self._speed = deque(maxlen=300)
        self._rpm = deque(maxlen=300)
        self._voltage = deque(maxlen=300)
        self._battery_temp = deque(maxlen=300)

    @property
    def state(self) -> DashboardState:
        return self._state

    def update(self, state: DashboardState) -> None:
        self._state = state
        self._speed.append(state.sample.speed_kph)
        self._rpm.append(state.sample.motor_rpm)
        self._voltage.append(state.sample.pack_voltage_v)
        self._battery_temp.append(state.sample.battery_temp_c)
        self.state_changed.emit(state)

    def latest_series(self) -> dict[str, list[float]]:
        return {
            "speed": list(self._speed),
            "rpm": list(self._rpm),
            "voltage": list(self._voltage),
            "battery_temp": list(self._battery_temp),
        }

    def stats_for(self, name: str) -> RollingStats:
        values = self.latest_series().get(name, [])
        if not values:
            return RollingStats(0.0, 0.0, 0.0)
        return RollingStats(min(values), max(values), sum(values) / len(values))


from datetime import datetime


def default_state() -> DashboardState:
    return DashboardState(sample=TelemetrySample(timestamp=datetime.utcnow()))
