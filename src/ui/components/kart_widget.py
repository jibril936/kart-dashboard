from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QResizeEvent
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class KartWidget(QWidget):
    """Widget displaying the top-view kart image."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._source_pixmap = QPixmap(
            str(Path(__file__).resolve().parents[3] / "assets" / "kart_top.png")
        )

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self._update_pixmap()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_pixmap()

    def _update_pixmap(self) -> None:
        if self._source_pixmap.isNull():
            self._label.clear()
            return

        scaled = self._source_pixmap.scaled(
            self._label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)
