from __future__ import annotations

from PyQt6.QtWidgets import QWidget


def value_is_present(value: object) -> bool:
    return value is not None


def set_visible_if(widget: QWidget, condition: bool) -> bool:
    widget.setVisible(condition)
    return condition
