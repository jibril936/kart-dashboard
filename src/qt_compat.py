from __future__ import annotations

"""Qt compatibility layer (PyQt6 first, PyQt5 fallback)."""

try:  # pragma: no cover - runtime dependent
    from PyQt6.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import (
        QApplication,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )

    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    FONT_BOLD = QFont.Weight.Bold
except ImportError:  # pragma: no cover - runtime dependent
    from PyQt5.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (
        QApplication,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )

    ALIGN_CENTER = Qt.AlignCenter
    FONT_BOLD = QFont.Bold

__all__ = [
    "ALIGN_CENTER",
    "QApplication",
    "QFont",
    "FONT_BOLD",
    "QFrame",
    "QGridLayout",
    "QHBoxLayout",
    "QLabel",
    "QMainWindow",
    "QObject",
    "QPushButton",
    "QStackedWidget",
    "QThread",
    "QTimer",
    "QVBoxLayout",
    "QWidget",
    "pyqtSignal",
]
