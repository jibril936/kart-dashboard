from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class KartTopViewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._compact = False
        self._ui_scale = 1.0

        assets_path = Path(__file__).resolve().parents[3] / "assets" / "kart_top.png"
        self._kart_pixmap = QPixmap(str(assets_path))

        self.setStyleSheet("background: transparent; border: none;")

        self._image = QLabel()
        self._image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image.setStyleSheet("background: transparent; border: none;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._image, 1)

        self._update_pixmap()

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        self._update_pixmap()

    def set_steer_angle(self, deg: float | None) -> None:
        _ = deg

    def _update_pixmap(self) -> None:
        if self._kart_pixmap.isNull():
            self._image.setText("KART")
            self._image.setStyleSheet("color: #EAF7FF; font-size: 38px; letter-spacing: 6px; background: transparent; border: none;")
            return

        max_w = int(self.width() * 0.88) if self.width() else 640
        max_h = int(self.height() * 0.88) if self.height() else 340
        scaled = self._kart_pixmap.scaled(max_w, max_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self._image.setPixmap(scaled)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_pixmap()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
