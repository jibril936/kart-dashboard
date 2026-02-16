from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from src.core.state_store import StateStore
from src.ui.components.analog_gauge import AnalogGaugeWidget

class ClusterPage(QWidget):
    def __init__(self, store: StateStore, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.store = store
        self.setStyleSheet("background-color: #000000;")

        # 1. On ne crée qu'UNE SEULE jauge pour l'instant
        self.speed_gauge = AnalogGaugeWidget(
            minValue=0,
            maxValue=100,
            units="km/h",
            gaugeColor="#00FFFF", # Ton Cyan OLED
            parent=self,
        )

        # 2. Layout simple : on la met au centre
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.speed_gauge)

        # 3. On branche le tuyau de données
        self._connect_store_signals()

    def _connect_store_signals(self) -> None:
        # On connecte le signal du simulateur à notre jauge unique
        self.store.speed_changed.connect(self.speed_gauge.setValue)