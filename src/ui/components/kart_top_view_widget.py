from __future__ import annotations

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


class KartTopViewWidget(QLabel):
    def __init__(self, parent: QLabel | None = None) -> None:
        super().__init__(parent)
        image_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "kart_top.png")
        print(f"DEBUG PATH: {os.path.abspath(image_path)}")
        asset_path = os.path.abspath(image_path)
        self.pixmap = QPixmap(asset_path)
        if self.pixmap.isNull():
            print("\033[91m" + "=" * 80)
            print("ERREUR CRITIQUE: IMPOSSIBLE DE CHARGER L'IMAGE KART")
            print(f"CHEMIN TESTÉ: {asset_path}")
            print("VÉRIFIE LE FICHIER src/assets/kart_top.png")
            print("=" * 80 + "\033[0m")

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

        target_height = max(1, int(self.height() * 0.8))
        target_width = max(1, self.width())

        scaled = self.pixmap.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
