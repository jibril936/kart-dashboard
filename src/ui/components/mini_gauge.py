from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget


class MiniGauge(QFrame):
    def __init__(self, title: str, unit: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("MiniGauge")
        self._unit = unit

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MiniGaugeTitle")
        self.value_label = QLabel(f"-- {unit}")
        self.value_label.setObjectName("MiniGaugeValue")

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        row = QHBoxLayout()
        row.addWidget(self.title_label)
        row.addStretch(1)
        row.addWidget(self.value_label, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(row)
        layout.addWidget(self.progress)

    def set_value(self, value: float, ratio: float, status: str = "OK") -> None:
        self.value_label.setText(f"{value:.1f} {self._unit}")
        self.progress.setValue(int(max(0, min(100, ratio * 100))))
        self.progress.setProperty("status", status)
        self.progress.style().unpolish(self.progress)
        self.progress.style().polish(self.progress)
