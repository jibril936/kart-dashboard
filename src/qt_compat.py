from __future__ import annotations

"""Qt compatibility layer (PyQt6 first, PyQt5 fallback)."""

try:  # pragma: no cover - runtime dependent
    from PyQt6.QtCore import QObject, QPointF, QThread, QTimer, Qt, pyqtSignal
    from PyQt6.QtGui import QColor, QFont, QPainter, QPen
    from PyQt6.QtWidgets import (
        QApplication,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QPushButton,
        QSizePolicy,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )

    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    ALIGN_LEFT = Qt.AlignmentFlag.AlignLeft
    ALIGN_RIGHT = Qt.AlignmentFlag.AlignRight
    FONT_BOLD = QFont.Weight.Bold
    NO_PEN = Qt.PenStyle.NoPen
except ImportError:  # pragma: no cover - runtime dependent
    from PyQt5.QtCore import QObject, QPointF, QThread, QTimer, Qt, pyqtSignal
    from PyQt5.QtGui import QColor, QFont, QPainter, QPen
    from PyQt5.QtWidgets import (
        QApplication,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QPushButton,
        QSizePolicy,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )

    ALIGN_CENTER = Qt.AlignCenter
    ALIGN_LEFT = Qt.AlignLeft
    ALIGN_RIGHT = Qt.AlignRight
    FONT_BOLD = QFont.Bold
    NO_PEN = Qt.NoPen

__all__ = [
    "ALIGN_CENTER",
    "ALIGN_LEFT",
    "ALIGN_RIGHT",
    "QApplication",
    "QColor",
    "QFont",
    "FONT_BOLD",
    "QFrame",
    "QGridLayout",
    "QHBoxLayout",
    "QLabel",
    "QListWidget",
    "QListWidgetItem",
    "QMainWindow",
    "NO_PEN",
    "QObject",
    "QPainter",
    "QPen",
    "QPointF",
    "QPushButton",
    "QSizePolicy",
    "QStackedWidget",
    "QThread",
    "QTimer",
    "QVBoxLayout",
    "QWidget",
    "pyqtSignal",
]
