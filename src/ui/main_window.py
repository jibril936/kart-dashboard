from __future__ import annotations

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.core.model import KartDataModel
from src.ui.screens import DrivingScreen, GraphsScreen, TechScreen


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kart Dashboard")
        self.resize(1024, 600)

        self.model = KartDataModel(self)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.stack = QStackedWidget(central_widget)
        self.stack.addWidget(DrivingScreen())
        self.stack.addWidget(TechScreen())
        self.stack.addWidget(GraphsScreen())

        nav_widget = QWidget(central_widget)
        nav_widget.setStyleSheet("background-color: #191919;")
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(12, 10, 12, 10)
        nav_layout.setSpacing(12)

        self.btn_driving = QPushButton("CLUSTER")
        self.btn_tech = QPushButton("TECH")
        self.btn_graphs = QPushButton("GRAPHS")

        for button in (self.btn_driving, self.btn_tech, self.btn_graphs):
            button.setMinimumHeight(56)
            nav_layout.addWidget(button)

        root_layout.addWidget(self.stack, 1)
        root_layout.addWidget(nav_widget, 0)
        self.setCentralWidget(central_widget)

        self.btn_driving.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_tech.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_graphs.clicked.connect(lambda: self.stack.setCurrentIndex(2))
