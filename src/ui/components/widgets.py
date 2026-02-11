from __future__ import annotations

import math

from src.qt_compat import (
    ALIGN_CENTER,
    FONT_BOLD,
    QColor,
    QFont,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    NO_PEN,
    QPainter,
    QPen,
    QPointF,
    QVBoxLayout,
    QWidget,
)
from src.core.types import Alert, AlertLevel


class GaugeNeedle(QWidget):
    def __init__(self, minimum: float, maximum: float, redline: float) -> None:
        super().__init__()
        self._min = minimum
        self._max = maximum
        self._redline = redline
        self._value = minimum
        self._display_value = minimum
        self.setMinimumHeight(220)

    def set_value(self, value: float) -> None:
        value = min(self._max, max(self._min, value))
        self._display_value = self._display_value * 0.78 + value * 0.22
        self._value = value
        self.update()

    def paintEvent(self, _) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(14, 14, -14, -14)

        painter.setPen(QPen(QColor("#203050"), 12))
        painter.drawArc(rect, 30 * 16, 120 * 16)

        red_start = self._value_to_deg(self._redline)
        painter.setPen(QPen(QColor("#FF5B5B"), 12))
        painter.drawArc(rect, int((180 - red_start) * 16), int((red_start - 30) * 16))

        angle = math.radians(self._value_to_deg(self._display_value))
        center = rect.center()
        length = rect.width() * 0.39
        end = QPointF(center.x() + math.cos(angle) * length, center.y() - math.sin(angle) * length)
        painter.setPen(QPen(QColor("#5ED0FF"), 5))
        painter.drawLine(center, end)
        painter.setPen(NO_PEN)
        painter.setBrush(QColor("#F8FBFF"))
        painter.drawEllipse(center, 6, 6)

    def _value_to_deg(self, value: float) -> float:
        ratio = (value - self._min) / max(1e-9, self._max - self._min)
        return 30 + ratio * 120


class DialContainer(QFrame):
    def __init__(self, title: str | None = None) -> None:
        super().__init__()
        self.setProperty("dial", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(10)
        self._title = QLabel(title or "")
        self._title.setProperty("kpi", True)
        self._title.setAlignment(ALIGN_CENTER)
        self._title.setVisible(bool(title))
        layout.addWidget(self._title)
        self._body = QVBoxLayout()
        self._body.setSpacing(6)
        layout.addLayout(self._body, 1)

    def set_title(self, title: str) -> None:
        self._title.setText(title)
        self._title.setVisible(bool(title))

    def body_layout(self) -> QVBoxLayout:
        return self._body


class ClusterTile(QFrame):
    def __init__(self, title: str, unit: str) -> None:
        super().__init__()
        self.setProperty("clusterTile", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        self._title = QLabel(title)
        self._title.setProperty("kpi", True)
        self._title.setAlignment(ALIGN_CENTER)

        self._value = QLabel("--")
        self._value.setProperty("tileValue", True)
        self._value.setAlignment(ALIGN_CENTER)

        self._unit = QLabel(unit)
        self._unit.setProperty("tileUnit", True)
        self._unit.setAlignment(ALIGN_CENTER)

        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._unit)

    def set_value(self, text: str) -> None:
        self._value.setText(text)


class BatteryWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setProperty("card", True)
        layout = QVBoxLayout(self)
        self._soc = QLabel("-- %")
        self._soc.setProperty("value", True)
        self._meta = QLabel("-- V · -- km")
        self._meta.setProperty("kpi", True)
        layout.addWidget(self._soc)
        layout.addWidget(self._meta)

    def update_values(self, soc: float, voltage: float, range_km: float) -> None:
        self._soc.setText(f"{soc:.0f}%")
        self._meta.setText(f"{voltage:.1f} V · {range_km:.0f} km")


class TempCard(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setProperty("card", True)
        layout = QVBoxLayout(self)
        self._title = QLabel(title)
        self._title.setProperty("kpi", True)
        self._value = QLabel("-- °C")
        self._value.setProperty("value", True)
        layout.addWidget(self._title)
        layout.addWidget(self._value)

    def set_temp(self, value: float) -> None:
        self._value.setText(f"{value:.1f} °C")


class AlertBanner(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setProperty("card", True)
        layout = QHBoxLayout(self)
        self._icon = QLabel("ⓘ")
        self._icon.setFont(QFont("Arial", 24, FONT_BOLD))
        self._text = QLabel("System nominal")
        self._text.setWordWrap(True)
        layout.addWidget(self._icon)
        layout.addWidget(self._text, 1)

    def update_alerts(self, alerts: list[Alert]) -> None:
        if not alerts:
            self.setStyleSheet("background:#10201A; border:1px solid #1D6C4B; border-radius:14px;")
            self._icon.setText("✓")
            self._text.setText("All systems nominal")
            return
        top = sorted(alerts, key=lambda a: [AlertLevel.INFO, AlertLevel.WARNING, AlertLevel.CRITICAL].index(a.level))[-1]
        if top.level == AlertLevel.CRITICAL:
            self.setStyleSheet("background:#2C1116; border:1px solid #A73447; border-radius:14px;")
            self._icon.setText("⚠")
        elif top.level == AlertLevel.WARNING:
            self.setStyleSheet("background:#2B2412; border:1px solid #8C6A1A; border-radius:14px;")
            self._icon.setText("!")
        else:
            self.setStyleSheet("background:#142131; border:1px solid #315B90; border-radius:14px;")
            self._icon.setText("ⓘ")
        self._text.setText(top.message)


class AlertHistoryList(QListWidget):
    def push_alerts(self, alerts: list[Alert]) -> None:
        self.clear()
        for alert in reversed(alerts[-80:]):
            item = QListWidgetItem(
                f"{alert.created_at.strftime('%H:%M:%S')} · {alert.level.value} · {alert.message} · {alert.action}"
            )
            self.addItem(item)
