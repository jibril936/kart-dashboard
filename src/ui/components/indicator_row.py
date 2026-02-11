from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget


@dataclass(slots=True)
class IndicatorSpec:
    key: str
    icon: str
    label: str


class IndicatorChip(QLabel):
    def __init__(self, icon: str, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._icon = icon
        self._label = label
        self.setMinimumWidth(74)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_status(False)

    def set_status(self, active: bool) -> None:
        css = "IndicatorActive" if active else "IndicatorIdle"
        self.setObjectName(css)
        self.setText(f"{self._icon} {self._label}")
        self.style().unpolish(self)
        self.style().polish(self)


class IndicatorRow(QWidget):
    def __init__(self, indicators: list[IndicatorSpec], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._chips: dict[str, IndicatorChip] = {}
        for spec in indicators:
            chip = IndicatorChip(spec.icon, spec.label)
            layout.addWidget(chip)
            self._chips[spec.key] = chip
        layout.addStretch(1)

    def update_status(self, statuses: dict[str, bool]) -> None:
        for key, chip in self._chips.items():
            chip.set_status(bool(statuses.get(key, False)))
