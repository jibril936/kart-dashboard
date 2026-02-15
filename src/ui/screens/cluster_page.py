from PyQt6.QtWidgets import QHBoxLayout, QWidget

from src.ui.components.kart_widget import KartWidget


class ClusterPage(QWidget):
    """Main cluster layout with reserved side columns and a centered kart."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        left_column = QWidget(self)
        center_column = QWidget(self)
        right_column = QWidget(self)

        center_layout = QHBoxLayout(center_column)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(KartWidget(center_column))

        layout.addWidget(left_column, 1)
        layout.addWidget(center_column, 2)
        layout.addWidget(right_column, 1)
