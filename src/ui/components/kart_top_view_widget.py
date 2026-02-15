from __future__ import annotations

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPixmap, QRadialGradient, QColor
from PyQt6.QtWidgets import QWidget


class KartTopViewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        image_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "kart_top.png")
        asset_path = os.path.abspath(image_path)
        self.pixmap = QPixmap(asset_path)
        self._scaled_pixmap = QPixmap()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        _ = (compact, ui_scale)

    def set_steer_angle(self, deg: float | None) -> None:
        _ = deg

    def _update_scaled_pixmap(self) -> None:
        if self.pixmap.isNull():
            self._scaled_pixmap = QPixmap()
            return

        target_height = max(1, int(self.height() * 0.76))
        target_width = max(1, self.width())
        self._scaled_pixmap = self.pixmap.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QRadialGradient(self.width() / 2, self.height() * 0.56, max(self.width(), self.height()) * 0.42)
        gradient.setColorAt(0.0, QColor(10, 30, 48, 180))
        gradient.setColorAt(0.5, QColor(5, 14, 22, 100))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

        if self._scaled_pixmap.isNull():
            self._update_scaled_pixmap()

        if not self._scaled_pixmap.isNull():
            x = (self.width() - self._scaled_pixmap.width()) // 2
            y = int((self.height() - self._scaled_pixmap.height()) * 0.40)
            painter.drawPixmap(x, y, self._scaled_pixmap)
