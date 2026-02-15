from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QWidget

STEER_VISUAL_CLAMP_DEG = 30.0
STEER_ANIM_MIN_MS = 90
STEER_ANIM_MAX_MS = 220


class KartTopViewWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._target_angle_deg = 0.0
        self._display_angle_deg = 0.0
        self._compact = False
        self._ui_scale = 1.0

        assets_path = Path(__file__).resolve().parents[3] / "assets" / "kart_top.png"
        self._kart_pixmap = QPixmap(str(assets_path)) if assets_path.exists() else QPixmap()

        self._steer_anim = QPropertyAnimation(self, b"steerAngleDeg", self)
        self._steer_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._steer_anim.setDuration(STEER_ANIM_MIN_MS)

        self.setMinimumHeight(170)
        self.setStyleSheet("background: transparent; border: none;")

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._compact = compact
        self._ui_scale = ui_scale
        self.update()

    def set_steer_angle(self, deg: float | None) -> None:
        value = 0.0 if deg is None else float(deg)
        self._target_angle_deg = max(-STEER_VISUAL_CLAMP_DEG, min(STEER_VISUAL_CLAMP_DEG, value))
        delta = abs(self._target_angle_deg - self._display_angle_deg)
        if delta < 0.05:
            self._set_steer_angle_internal(self._target_angle_deg)
            return

        duration = int(min(STEER_ANIM_MAX_MS, max(STEER_ANIM_MIN_MS, 6.0 * delta + 85.0)))
        self._steer_anim.stop()
        self._steer_anim.setDuration(duration)
        self._steer_anim.setStartValue(self._display_angle_deg)
        self._steer_anim.setEndValue(self._target_angle_deg)
        self._steer_anim.start()

    def _set_steer_angle_internal(self, value: float) -> None:
        self._display_angle_deg = float(value)
        self.update()

    @pyqtProperty(float)
    def steerAngleDeg(self) -> float:  # noqa: N802
        return self._display_angle_deg

    @steerAngleDeg.setter
    def steerAngleDeg(self, value: float) -> None:  # noqa: N802
        self._set_steer_angle_internal(value)

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        zone = QRectF(self.rect()).adjusted(18, 14, -18, -14)
        if zone.width() <= 0 or zone.height() <= 0:
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#151515"))
        painter.drawRoundedRect(zone, 12, 12)

        image_zone = zone.adjusted(zone.width() * 0.12, zone.height() * 0.08, -zone.width() * 0.12, -zone.height() * 0.1)
        if not self._kart_pixmap.isNull():
            scaled = self._kart_pixmap.scaled(
                int(image_zone.width()),
                int(image_zone.height()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = int(image_zone.center().x() - scaled.width() / 2)
            y = int(image_zone.center().y() - scaled.height() / 2)
            painter.drawPixmap(x, y, scaled)
        else:
            painter.setPen(QPen(QColor("#2a2a2a"), 2.0))
            painter.drawRoundedRect(image_zone, 10, 10)

        steer_ratio = max(-1.0, min(1.0, self._display_angle_deg / STEER_VISUAL_CLAMP_DEG))
        bar = zone.adjusted(zone.width() * 0.2, zone.height() * 0.86, -zone.width() * 0.2, -zone.height() * 0.06)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#222"))
        painter.drawRoundedRect(bar, 4, 4)

        center_x = bar.center().x()
        if steer_ratio >= 0:
            fill = QRectF(center_x, bar.top(), (bar.width() / 2.0) * steer_ratio, bar.height())
        else:
            fill = QRectF(center_x + (bar.width() / 2.0) * steer_ratio, bar.top(), (bar.width() / 2.0) * (-steer_ratio), bar.height())

        painter.setBrush(QColor("#18a9ff"))
        painter.drawRoundedRect(fill.normalized(), 4, 4)
