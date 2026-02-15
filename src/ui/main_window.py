from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from src.core.model import KartDataModel
from src.core.state import VehicleTechState
from src.ui.cluster_screen import ClusterScreen
from src.ui.components.bottom_bar import NavButton
from src.ui.screens import GraphsScreen, TechScreen


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("KART DASHBOARD PRO V2 - ACTIVE")
        self.resize(1024, 600)

        self.model = KartDataModel(self)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.stack = QStackedWidget(central_widget)
        self.cluster_screen = ClusterScreen()
        self.cluster_screen.tech_requested.connect(lambda: self._set_page(1))
        self.stack.addWidget(self.cluster_screen)
        self.stack.addWidget(TechScreen())
        self.stack.addWidget(GraphsScreen())

        nav_widget = QWidget(central_widget)
        nav_widget.setStyleSheet("background: #0A0A0A; border-top: 1px solid #1C1C1C;")
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(320, 8, 320, 6)
        nav_layout.setSpacing(26)

        self.btn_driving = NavButton("CLUSTER")
        self.btn_tech = NavButton("TECH")
        self.btn_graphs = NavButton("GRAPHS")

        for button in (self.btn_driving, self.btn_tech, self.btn_graphs):
            button.setMinimumHeight(26)
            nav_layout.addWidget(button)

        root_layout.addWidget(self.stack, 1)
        root_layout.addWidget(nav_widget, 0)
        self.setCentralWidget(central_widget)

        self.btn_driving.clicked.connect(lambda: self._set_page(0))
        self.btn_tech.clicked.connect(lambda: self._set_page(1))
        self.btn_graphs.clicked.connect(lambda: self._set_page(2))
        self._set_page(0)

        self.model.speed_changed.connect(lambda _value: self._render_cluster())
        self._render_cluster()

    def _set_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        self.btn_driving.set_active(index == 0)
        self.btn_tech.set_active(index == 1)
        self.btn_graphs.set_active(index == 2)

    def _render_cluster(self) -> None:
        state = VehicleTechState(
            speed_kmh=self.model.speed,
            steering_angle_deg=self.model.steering_angle,
            charging_state=self.model.charging_state,
            battery_voltage_V=self.model.battery_pack_voltage,
            battery_charge_current_A=self.model.battery_pack_current,
            motor_temp_C=self.model.motor_temperature,
        )
        self.cluster_screen.render(state)
