from __future__ import annotations

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


class BrakeWidget(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._active = False
        self.setFixedHeight(96)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        layout.addStretch(1)

        self.label = QLabel("BRAKE")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 24px; font-weight: 900; letter-spacing: 2px;"
        )
        layout.addWidget(self.label)
        layout.addStretch(1)
        self._apply_style()

    def _apply_style(self) -> None:
        border = "#384b5f"
        bg = "#202d3b"
        text = "#5f7388"
        if self._active:
            border = "#ff0000"
            bg = "#ff0000"
            text = "#ffffff"

        self.setStyleSheet(
            f"""
            QFrame {{
                border-radius: 12px;
                border: 2px solid {border};
                background-color: {bg};
            }}
            QLabel {{
                color: {text};
                background: transparent;
                border: none;
            }}
            """
        )

    def set_brake_state(self, active: bool) -> None:
        self._active = bool(active)
        self._apply_style()


class SteeringWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._angle = 0.0
        self.setMinimumHeight(130)

    def set_steering_angle(self, angle_deg: float) -> None:
        self._angle = max(-35.0, min(35.0, float(angle_deg)))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect().adjusted(12, 14, -12, -18)
        cx = rect.center().x()
        cy = rect.center().y() + 6
        half_w = rect.width() * 0.38

        painter.setPen(QPen(QColor("#415669"), 2))
        painter.drawLine(QPointF(cx - half_w, cy), QPointF(cx + half_w, cy))

        painter.setPen(QPen(QColor("#587086"), 1))
        for i in range(-3, 4):
            x = cx + (half_w * i / 3.0)
            painter.drawLine(QPointF(x, cy - 9), QPointF(x, cy + 9))

        painter.setPen(QPen(QColor("#00e5ff"), 3))
        pointer_x = cx + (self._angle / 35.0) * half_w
        painter.drawLine(QPointF(pointer_x, cy - 24), QPointF(pointer_x, cy + 24))


class DynamicsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(220)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1a2634;
                border-radius: 12px;
                border: 1px solid #2c3e50;
            }
            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        brake_title = QLabel("FREIN")
        brake_title.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 10px; font-weight: 700; color: #8da7be;"
        )
        self.brake_widget = BrakeWidget(self)

        steering_title = QLabel("DIRECTION")
        steering_title.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 10px; font-weight: 700; color: #8da7be;"
        )
        self.steering_widget = SteeringWidget(self)

        self.steering_value = QLabel("+0°")
        self.steering_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.steering_value.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 20px; font-weight: 800; color: #e9f2fc;"
        )

        radar_title = QLabel("RADARS ARRIÈRE")
        radar_title.setStyleSheet(
            "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 10px; font-weight: 700; color: #8da7be;"
        )

        root.addWidget(brake_title)
        root.addWidget(self.brake_widget)
        root.addWidget(steering_title)
        root.addWidget(self.steering_widget)
        root.addWidget(self.steering_value)
        root.addWidget(radar_title)

        radar_names = ["G", "C", "D"]
        self.radar_bars: list[QProgressBar] = []
        for name in radar_names:
            row = QHBoxLayout()
            row.setSpacing(8)

            label = QLabel(name)
            label.setFixedWidth(16)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                "font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 12px; font-weight: 700; color: #8da7be;"
            )

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setMinimumHeight(8)
            self._set_radar_bar_style(bar, "#2b3c4c")

            row.addWidget(label)
            row.addWidget(bar, 1)

            host = QWidget(self)
            host.setLayout(row)
            host.setStyleSheet("background: transparent; border: none;")
            root.addWidget(host)
            self.radar_bars.append(bar)

        root.addStretch(1)

    def _set_radar_bar_style(self, bar: QProgressBar, color: str) -> None:
        bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #31495a;
                border-radius: 4px;
                background-color: #0d121a;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
                background-color: {color};
            }}
            """
        )

    def set_brake_state(self, active: bool) -> None:
        self.brake_widget.set_brake_state(active)

    def set_steering_angle(self, angle_deg: float) -> None:
        angle = max(-35.0, min(35.0, float(angle_deg)))
        self.steering_widget.set_steering_angle(angle)
        self.steering_value.setText(f"{angle:+.0f}°")

    def update_radars(self, distances: list[float]) -> None:
        clipped = [max(0.0, min(400.0, float(d))) for d in distances[:3]]
        while len(clipped) < 3:
            clipped.append(400.0)

        for bar, distance in zip(self.radar_bars, clipped):
            proximity = int(round(((400.0 - distance) / 400.0) * 100.0))
            bar.setValue(proximity)
            if distance < 120.0:
                color = "#ff3b30"
            elif distance < 240.0:
                color = "#ff9f0a"
            else:
                color = "#34d399"
            self._set_radar_bar_style(bar, color)
