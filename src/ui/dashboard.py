from __future__ import annotations

from src.qt_compat import QMainWindow, QStackedWidget

from src.models.telemetry import Telemetry
from src.ui.diag_view import DiagView
from src.ui.drive_view import DriveView


class DashboardWindow(QMainWindow):
    def __init__(self, refresh_hz: float) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard")
        self.setStyleSheet("background-color: #0b0f1a; color: #F9FAFB;")

        self._stack = QStackedWidget()
        self._drive = DriveView()
        self._diag = DiagView(refresh_hz=refresh_hz)

        self._stack.addWidget(self._drive)
        self._stack.addWidget(self._diag)
        self.setCentralWidget(self._stack)

        self._drive.diagnostics_requested.connect(self.show_diag)
        self._diag.back_requested.connect(self.show_drive)

    def show_drive(self) -> None:
        self._stack.setCurrentWidget(self._drive)

    def show_diag(self) -> None:
        self._stack.setCurrentWidget(self._diag)

    def update_telemetry(self, telemetry: Telemetry) -> None:
        self._drive.update_telemetry(telemetry)
        self._diag.update_telemetry(telemetry)
