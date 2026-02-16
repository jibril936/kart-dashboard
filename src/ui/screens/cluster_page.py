from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.core.state_store import StateStore
from src.ui.components.analog_gauge import AnalogGaugeWidget
from src.ui.components.kart_widget import KartWidget


class ClusterPage(QWidget):
    """Main dashboard cluster with dual analog gauges and center kart widget."""

    def __init__(self, store: StateStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.store = store
        self.setStyleSheet("background-color: #000000;")

        self.speed_gauge = AnalogGaugeWidget(
            minValue=0,
            maxValue=100,
            units="km/h",
            gaugeColor="#00FFFF",
            parent=self,
        )
        self.power_gauge = AnalogGaugeWidget(
            minValue=-10,
            maxValue=50,
            units="kW",
            gaugeColor="#FF4D00",
            parent=self,
        )
        self.kart_widget = KartWidget(self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.speed_gauge, stretch=1)
        layout.addWidget(self.kart_widget, stretch=2)
        layout.addWidget(self.power_gauge, stretch=1)

        self._connect_store_signals()

    def _connect_store_signals(self) -> None:
        self.store.speed_changed.connect(self._on_speed_changed)
        self.store.pack_current_changed.connect(self._on_pack_current_changed)

    def _on_speed_changed(self, speed: float) -> None:
        self.speed_gauge.setValue(speed)

    def _on_pack_current_changed(self, pack_current: float) -> None:
        self.power_gauge.setValue(pack_current)
