from __future__ import annotations

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget


class BottomBar(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BottomBarStrip")
        self._warning_visible = True

        self.setStyleSheet(
            """
            QFrame#BottomBarStrip {
                background-color: #171717;
                border: 1px solid #333333;
                border-radius: 14px;
            }
            QLabel {
                border: none;
                color: #EDEDED;
                background: transparent;
                font-weight: 700;
            }
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(16)

        self.motor_temp_label = QLabel("Moteur: --°C")
        self.motor_temp_label.setStyleSheet("font-size: 26px;")

        self.batt_temp_label = QLabel("Batt: --°C")
        self.batt_temp_label.setStyleSheet("font-size: 26px;")

        self.warning_label = QLabel("OK")
        self.warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_label.setStyleSheet(
            "font-size: 24px; color: #8AFF8A; background-color: #0E220E; border: 1px solid #225522; border-radius: 8px; padding: 6px;"
        )

        layout.addWidget(self.motor_temp_label, 1)
        layout.addWidget(self.batt_temp_label, 1)
        layout.addWidget(self.warning_label, 2)

        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(450)
        self._blink_timer.timeout.connect(self._toggle_warning)

    def update_temperatures(self, motor_temp: float, battery_temp: float) -> None:
        motor = float(motor_temp)
        batt = float(battery_temp)

        self.motor_temp_label.setText(f"Moteur: {motor:.0f}°C")
        self.batt_temp_label.setText(f"Batt: {batt:.0f}°C")

        motor_color = "#FF4D4D" if motor > 90.0 else "#EDEDED"
        self.motor_temp_label.setStyleSheet(f"font-size: 26px; color: {motor_color};")

    def update_warning(self, warnings: list[str]) -> None:
        if warnings:
            text = " | ".join(warnings).upper()
            self.warning_label.setText(text)
            self.warning_label.setStyleSheet(
                "font-size: 24px; color: #FFD7D7; background-color: #5A0000; border: 1px solid #FF4D4D; border-radius: 8px; padding: 6px;"
            )
            if not self._blink_timer.isActive():
                self._warning_visible = True
                self._blink_timer.start()
            self.warning_label.setVisible(True)
        else:
            self._blink_timer.stop()
            self.warning_label.setVisible(True)
            self.warning_label.setText("OK")
            self.warning_label.setStyleSheet(
                "font-size: 24px; color: #8AFF8A; background-color: #0E220E; border: 1px solid #225522; border-radius: 8px; padding: 6px;"
            )

    def _toggle_warning(self) -> None:
        self._warning_visible = not self._warning_visible
        self.warning_label.setVisible(self._warning_visible)

    def set_values(self, battery_voltage: float | None, battery_soc_percent: float | None, motor_temp_c: float | None) -> None:
        _ = (battery_voltage, battery_soc_percent)
        if motor_temp_c is not None:
            self.update_temperatures(float(motor_temp_c), 0.0)


BottomBarStrip = BottomBar
