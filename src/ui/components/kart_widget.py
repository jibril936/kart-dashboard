from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class KartWidget(QWidget):
    """Minimal center widget placeholder for the kart visual."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #070707;"
            "border: 2px solid #2A2A2A;"
            "border-radius: 14px;"
        )
        self.setMinimumSize(320, 240)

        label = QLabel("KART", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #00FFFF; font-size: 40px; font-weight: 700;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(label)
