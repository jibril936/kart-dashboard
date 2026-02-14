from __future__ import annotations

from collections.abc import Mapping

from PyQt6.QtWidgets import QWidget

from src.ui.third_party.analoggaugewidget.analoggaugewidget import AnalogGaugeWidget


class SpeedGaugeOEM(QWidget):
    """Project wrapper around vendorized analog gauge implementation."""

    def __init__(
        self,
        title: str,
        unit: str,
        min_value: float,
        max_value: float,
        major_tick_step: float = 10,
        minor_ticks_per_major: int = 1,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._gauge = AnalogGaugeWidget(self)
        self._gauge.setTitle(title)
        self._gauge.setDisplayUnits(unit)
        self._gauge.setMinValue(min_value)
        self._gauge.setMaxValue(max_value)

        major_count = max(1, int(round((max_value - min_value) / max(1.0, major_tick_step))))
        self._gauge.setScalaMainCount(major_count)
        self._gauge.setScalaSubDivCount(max(0, int(minor_ticks_per_major)))

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._gauge.setGeometry(self.rect())

    def set_value(self, value: float) -> None:
        self._gauge.updateValue(value)

    def set_speed(self, value: float) -> None:
        self.set_value(value)

    def set_range(self, min_value: float, max_value: float) -> None:
        self._gauge.setMinValue(min_value)
        self._gauge.setMaxValue(max_value)

    def set_style(self, style: Mapping[str, object] | None = None, **kwargs: object) -> None:
        """Apply style overrides to the vendor gauge.

        Keys can be passed either via mapping or keyword args and are forwarded
        to ``AnalogGaugeWidget.setStyleProfile``.
        """

        merged: dict[str, object] = {}
        if style:
            merged.update(style)
        merged.update(kwargs)
        if merged:
            self._gauge.setStyleProfile(**merged)

    def set_compact_mode(self, compact: bool, ui_scale: float = 1.0) -> None:
        self._gauge.set_compact_mode(compact, ui_scale)
