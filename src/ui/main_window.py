from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from src.core.state import VehicleTechState
from src.ui.cluster_screen import ClusterScreen
from src.ui.tech_screen import TechScreen


class DashboardMainWindow(QMainWindow):
    def __init__(self, ui_scale: float = 1.0) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard — Cluster / Tech")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.cluster_screen = ClusterScreen(ui_scale=ui_scale)
        self.tech_screen = TechScreen()

        self.stack.addWidget(self.cluster_screen)
        self.stack.addWidget(self.tech_screen)

        self.cluster_screen.tech_requested.connect(self.show_tech)
        self.tech_screen.cluster_requested.connect(self.show_cluster)

        self.show_cluster()

    def show_cluster(self) -> None:
        self.stack.setCurrentWidget(self.cluster_screen)

    def show_tech(self) -> None:
        self.stack.setCurrentWidget(self.tech_screen)

    def render(self, state: VehicleTechState) -> None:
        self.cluster_screen.render(state)
        self.tech_screen.render(state)
