from __future__ import annotations

from src.core.types import AppConfig, DashboardState
from src.qt_compat import QMainWindow, QStackedWidget
from src.ui.details_screen import DetailsScreen
from src.ui.drive_screen import DriveScreen


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig, details_screen: DetailsScreen) -> None:
        super().__init__()
        self.setWindowTitle("EV Kart Cluster")
        self._stack = QStackedWidget()
        self._drive = DriveScreen(config)
        self._details = details_screen
        self._stack.addWidget(self._drive)
        self._stack.addWidget(self._details)
        self.setCentralWidget(self._stack)

        self._drive.details_requested.connect(self.show_details)
        self._details.drive_requested.connect(self.show_drive)

    def show_drive(self) -> None:
        self._stack.setCurrentWidget(self._drive)

    def show_details(self) -> None:
        self._stack.setCurrentWidget(self._details)

    def render(self, state: DashboardState) -> None:
        self._drive.render(state)
        self._details.render(state)
