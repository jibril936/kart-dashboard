from __future__ import annotations

from src.core.store import StateStore
from src.core.types import DashboardState
from src.qt_compat import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, pyqtSignal
from src.ui.components import AlertHistoryList

try:  # pragma: no cover - optional dependency
    import pyqtgraph as pg
except Exception:  # pragma: no cover
    pg = None


class DetailsScreen(QWidget):
    drive_requested = pyqtSignal()

    def __init__(self, store: StateStore) -> None:
        super().__init__()
        self._store = store
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)

        top = QHBoxLayout()
        btn = QPushButton("Back to Drive")
        btn.setMinimumHeight(52)
        btn.clicked.connect(self.drive_requested.emit)
        self._stats = QLabel("Stats pending")
        top.addWidget(btn)
        top.addWidget(self._stats, 1)
        root.addLayout(top)

        self._plot = None
        self._curves = {}
        if pg is not None:
            self._plot = pg.PlotWidget(background="#070B14")
            self._plot.addLegend()
            self._plot.showGrid(x=True, y=True, alpha=0.3)
            self._curves = {
                "speed": self._plot.plot(pen=pg.mkPen("#52B9FF", width=2), name="speed"),
                "rpm": self._plot.plot(pen=pg.mkPen("#9D7DFF", width=2), name="rpm/100"),
                "voltage": self._plot.plot(pen=pg.mkPen("#64D38A", width=2), name="voltage"),
                "battery_temp": self._plot.plot(pen=pg.mkPen("#F6B64A", width=2), name="battery temp"),
            }
            root.addWidget(self._plot, 2)
        else:
            root.addWidget(QLabel("pyqtgraph unavailable"), 2)

        bottom = QGridLayout()
        self._history = AlertHistoryList()
        bottom.addWidget(self._history, 0, 0)
        root.addLayout(bottom, 2)

    def render(self, state: DashboardState) -> None:
        speed_stats = self._store.stats_for("speed")
        volt_stats = self._store.stats_for("voltage")
        self._stats.setText(
            f"Speed avg {speed_stats.avg_value:.1f} · min/max {speed_stats.min_value:.1f}/{speed_stats.max_value:.1f} km/h"
            f"   | Voltage avg {volt_stats.avg_value:.2f} V"
        )
        self._history.push_alerts(state.alert_history)

        if not self._curves:
            return
        series = self._store.latest_series()
        x = list(range(len(series["speed"])))
        self._curves["speed"].setData(x, series["speed"])
        self._curves["rpm"].setData(x, [v / 100 for v in series["rpm"]])
        self._curves["voltage"].setData(x, series["voltage"])
        self._curves["battery_temp"].setData(x, series["battery_temp"])
