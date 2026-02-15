from __future__ import annotations

import math

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QPointF, QRectF, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.state import VehicleTechState
from src.ui.components.bottom_bar import BottomBarStrip
from src.ui.components.center_panel import CenterPanel

SPEED_MIN_KMH = 0
SPEED_MAX_KMH = 60
POWER_MIN_KW = -12.0
POWER_MAX_KW = 12.0


class SegmentedGauge(QWidget):
    def __init__(self, title: str, unit: str, minimum: float, maximum: float, segments: int = 36, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._unit = unit
        self._min = float(minimum)
        self._max = float(maximum)
        self._value = self._min
        self._display_value = self._min
        self._segments = segments

        self.setMinimumSize(260, 260)
        self.setStyleSheet("background: transparent; border: none;")

        self._anim = QPropertyAnimation(self, b"displayValue", self)
        self._anim.setDuration(240)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._value_label = QLabel("0")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setStyleSheet("color: #F1F7FF; border: none; background: transparent;")
        self._value_label.setFont(QFont("Bahnschrift", 46, QFont.Weight.Bold))

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(30)
        glow.setOffset(0, 0)
        glow.setColor(QColor("#179BFF"))
        self._value_label.setGraphicsEffect(glow)

        self._unit_label = QLabel(unit)
        self._unit_label.setStyleSheet("color: #7d95ae; font-size: 14px; border: none; background: transparent;")

        self._title_label = QLabel(title)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet("color: #7d95ae; font-size: 13px; letter-spacing: 2px; border: none; background: transparent;")

        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.setSpacing(6)
        value_row.addStretch(1)
        value_row.addWidget(self._value_label)
        value_row.addWidget(self._unit_label, 0, Qt.AlignmentFlag.AlignBottom)
        value_row.addStretch(1)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(0)
        root.addWidget(self._title_label)
        root.addStretch(1)
        root.addLayout(value_row)
        root.addStretch(1)

    def set_value(self, value: float) -> None:
        self._value = max(self._min, min(self._max, float(value)))
        self._anim.stop()
        self._anim.setStartValue(self._display_value)
        self._anim.setEndValue(self._value)
        self._anim.start()

    @pyqtProperty(float)
    def displayValue(self) -> float:  # noqa: N802
        return self._display_value

    @displayValue.setter
    def displayValue(self, value: float) -> None:  # noqa: N802
        self._display_value = float(value)
        shown = int(round(self._display_value)) if self._unit == "km/h" else self._display_value
        if self._unit == "kW":
            self._value_label.setText(f"{shown:+.1f}")
        else:
            self._value_label.setText(f"{shown:d}")
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        zone = QRectF(self.rect()).adjusted(18, 18, -18, -18)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#151515"))
        painter.drawRoundedRect(zone, 12, 12)

        center = zone.center()
        radius = min(zone.width(), zone.height()) * 0.43
        start = 210.0
        span = 300.0
        seg_angle = span / self._segments
        ratio = 0.0 if self._max == self._min else (self._display_value - self._min) / (self._max - self._min)
        active = int(max(0, min(self._segments, round(ratio * self._segments))))

        for idx in range(self._segments):
            a0 = start - idx * seg_angle
            a1 = a0 - seg_angle * 0.58
            p0 = QPointF(center.x() + radius * math.cos(math.radians(a0)), center.y() - radius * math.sin(math.radians(a0)))
            p1 = QPointF(center.x() + radius * math.cos(math.radians(a1)), center.y() - radius * math.sin(math.radians(a1)))
            if idx < active:
                glow = 80 + int(140 * (idx / max(1, self._segments - 1)))
                painter.setPen(QPen(QColor(40, 165, 255, glow), 5.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            else:
                painter.setPen(QPen(QColor(50, 50, 50, 90), 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(p0, p1)


class ClusterScreen(QWidget):
    tech_requested = pyqtSignal()

    def __init__(self, ui_scale: float = 1.0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_ui_scale = ui_scale
        self._effective_scale = ui_scale
        self.setObjectName("ClusterScreen")
        self.setStyleSheet(
            """
            #ClusterScreen { background: #0A0A0A; border: none; }
            QWidget { border: none; }
            QPushButton#TechButton {
                background: #151515;
                color: #dbe7f7;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 13px;
                letter-spacing: 1px;
            }
            QPushButton#TechButton:hover { background: #1d1d1d; }
            """
        )

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(22, 16, 22, 14)
        self.root.setSpacing(12)

        self.top_bar = QHBoxLayout()
        self.top_bar.setSpacing(10)

        self.tech_button = QPushButton("TECH")
        self.tech_button.setObjectName("TechButton")
        self.tech_button.clicked.connect(self.tech_requested.emit)

        self.top_bar.addStretch(1)
        self.top_bar.addWidget(self.tech_button)
        self.root.addLayout(self.top_bar)

        self.middle = QHBoxLayout()
        self.middle.setSpacing(18)

        self.speed_gauge = SegmentedGauge("SPEED", "km/h", SPEED_MIN_KMH, SPEED_MAX_KMH)
        self.center_panel = CenterPanel()
        self.power_gauge = SegmentedGauge("POWER", "kW", POWER_MIN_KW, POWER_MAX_KW, segments=28)

        self.middle.addWidget(self.speed_gauge, 2)
        self.middle.addWidget(self.center_panel, 3)
        self.middle.addWidget(self.power_gauge, 2)
        self.root.addLayout(self.middle, 1)

        self.bottom_bar = BottomBarStrip()
        self.root.addWidget(self.bottom_bar)
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        compact = self.width() < 1200 or self.height() < 680
        self._effective_scale = max(0.8, min(1.2, self._base_ui_scale * (0.9 if compact else 1.0)))
        s = self._effective_scale
        self.root.setContentsMargins(int(18 * s), int(14 * s), int(18 * s), int(12 * s))
        self.middle.setSpacing(int(14 * s))
        self.center_panel.set_compact_mode(compact, s)
        self.center_panel.kart_widget.set_compact_mode(compact, s)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._apply_responsive_layout()

    def render(self, state: VehicleTechState) -> None:
        speed = state.speed_kmh
        steering_angle = state.steering_angle_deg
        charging = state.charging_state
        battery_v = state.battery_voltage_V
        brake = state.brake_state
        motor_temp = state.motor_temp_C

        self.speed_gauge.setVisible(speed is not None)
        if speed is not None:
            self.speed_gauge.set_value(float(speed))

        drive_mode = getattr(state, "drive_mode", None)
        control_mode = getattr(state, "control_mode", None)

        self.center_panel.set_state(
            float(steering_angle) if steering_angle is not None else None,
            drive_mode=drive_mode,
            control_mode=control_mode,
            charging_state=charging,
            gear=None,
        )

        battery_current = state.battery_charge_current_A
        if battery_v is not None and battery_current is not None:
            self.power_gauge.set_value((float(battery_v) * float(battery_current)) / 1000.0)

        _ = brake

        self.bottom_bar.set_values(
            battery_voltage=battery_v,
            battery_soc_percent=None,
            motor_temp_c=motor_temp,
        )

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect())
        painter.fillRect(rect, QColor("#0A0A0A"))

        painter.setPen(QPen(QColor(255, 255, 255, 18), 1.0))
        frame = rect.adjusted(10, 8, -10, -8)
        painter.drawRoundedRect(frame, 14, 14)
