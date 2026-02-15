from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


class KartTopViewWidget(QLabel):
    def __init__(self, parent: QLabel | None = None) -> None:
        super().__init__(parent)
        self.pixmap = QPixmap("./assets/kart_top.png")
        if self.pixmap.isNull():
            print("ERREUR CRITIQUE: Image du kart non trouvée dans assets/")

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setStyleSheet("background: transparent; border: none;")

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        _ = (compact, ui_scale)

    def set_steer_angle(self, deg: float | None) -> None:
        _ = deg

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self.pixmap.isNull():
            self.clear()
            return

        scaled = self.pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
