from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QKeyEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.state import VehicleTechState
from src.ui.cluster_screen import ClusterScreen
from src.ui.tech_screen import TechScreen


class DashboardMainWindow(QMainWindow):
    def __init__(self, ui_scale: float = 1.0) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard — Cluster / Tech")
        self._allow_escape_fullscreen = False
        self._hide_cursor_in_fullscreen = False

        self._central_widget = QWidget(self)
        self._root_layout = QVBoxLayout(self._central_widget)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self._root_layout.addWidget(self.stack, 1)

        self._navigation_layout = QHBoxLayout()
        self._navigation_layout.setContentsMargins(8, 8, 8, 8)
        self._navigation_layout.setSpacing(8)
        self._root_layout.addLayout(self._navigation_layout)

        self._cluster_button = QPushButton("Cluster")
        self._tech_button = QPushButton("Tech")
        self._graphs_button = QPushButton("Graphs")
        self._navigation_layout.addWidget(self._cluster_button)
        self._navigation_layout.addWidget(self._tech_button)
        self._navigation_layout.addWidget(self._graphs_button)

        self.setCentralWidget(self._central_widget)

        self.cluster_screen = ClusterScreen(ui_scale=ui_scale)
        self.tech_screen = TechScreen()
        self.graphs_screen = self._build_placeholder_frame("#1B5E20")

        self.cluster_container = self._build_placeholder_frame("#8B0000")
        self.tech_container = self._build_placeholder_frame("#003366")

        self._set_frame_content(self.cluster_container, self.cluster_screen)
        self._set_frame_content(self.tech_container, self.tech_screen)

        self.stack.addWidget(self.cluster_container)
        self.stack.addWidget(self.tech_container)
        self.stack.addWidget(self.graphs_screen)

        self.cluster_screen.tech_requested.connect(self.show_tech)
        self.tech_screen.cluster_requested.connect(self.show_cluster)
        self._cluster_button.clicked.connect(self.show_cluster)
        self._tech_button.clicked.connect(self.show_tech)
        self._graphs_button.clicked.connect(self.show_graphs)

        self.show_cluster()

    def _build_placeholder_frame(self, color_hex: str) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"background-color: {color_hex};")
        return frame

    def _set_frame_content(self, frame: QFrame, content: QWidget) -> None:
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(content)

    def show_cluster(self) -> None:
        self.stack.setCurrentIndex(0)

    def show_tech(self) -> None:
        self.stack.setCurrentIndex(1)

    def show_graphs(self) -> None:
        self.stack.setCurrentIndex(2)

    def render(self, state: VehicleTechState) -> None:
        self.cluster_screen.render(state)
        self.tech_screen.render(state)

    def enable_escape_fullscreen(self) -> None:
        self._allow_escape_fullscreen = True

    def set_hide_cursor_in_fullscreen(self, enabled: bool) -> None:
        self._hide_cursor_in_fullscreen = enabled

    def apply_fullscreen_cursor(self) -> None:
        if self._hide_cursor_in_fullscreen and self.isFullScreen():
            self.setCursor(QCursor(Qt.CursorShape.BlankCursor))
            return
        self.unsetCursor()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._allow_escape_fullscreen and self.isFullScreen() and event.key() == Qt.Key.Key_Escape:
            self.showNormal()
            self.apply_fullscreen_cursor()
            event.accept()
            return
        super().keyPressEvent(event)
