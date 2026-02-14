from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget


class DrivingScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #121212; border: 2px solid #AA2222;")

        layout = QGridLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        label = QLabel("CLUSTER")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 1, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)


class TechScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #091530;")

        layout = QGridLayout(self)
        label = QLabel("TECH")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)


class GraphsScreen(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

        layout = QGridLayout(self)
        label = QLabel("GRAPHS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        layout.addWidget(label, 0, 0)
