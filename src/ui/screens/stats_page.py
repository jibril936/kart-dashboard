from collections import deque

from qtpy.QtCore import Qt, QTimer, QRectF
from qtpy.QtGui import QColor, QFont, QPainter, QPen
from qtpy.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class TimeSeriesCard(QFrame):
    def __init__(self, title: str, unit: str, color: str, y_min=None, y_max=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.color = QColor(color)
        self.y_min_forced = y_min
        self.y_max_forced = y_max

        self.values = deque(maxlen=120)
        self.current_value = 0.0

        self.setObjectName("Card")
        self.setStyleSheet("""
            QFrame#Card {
                background-color: #111111;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
            }
        """)

        self.value_label = QLabel("--")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_label.setStyleSheet("color: white; font-size: 18px; font-weight: 700;")

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("color: #cfcfcf; font-size: 14px; font-weight: 600;")

        self.chart = MiniChartWidget(color=self.color, y_min=self.y_min_forced, y_max=self.y_max_forced)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.chart, 1)

    def push_value(self, value: float):
        try:
            value = float(value)
        except Exception:
            value = 0.0

        self.current_value = value
        self.values.append(value)
        self.value_label.setText(f"{value:.1f} {self.unit}")
        self.chart.set_values(list(self.values))


class MiniChartWidget(QWidget):
    def __init__(self, color: QColor, y_min=None, y_max=None, parent=None):
        super().__init__(parent)
        self.color = color
        self.values = []
        self.y_min_forced = y_min
        self.y_max_forced = y_max
        self.setMinimumHeight(120)

    def set_values(self, values):
        self.values = values or []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(8, 8, -8, -8)

        # fond
        painter.fillRect(rect, QColor("#0b0b0b"))

        # grille
        grid_pen = QPen(QColor("#262626"))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)

        for i in range(1, 4):
            y = rect.top() + i * rect.height() / 4
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

        for i in range(1, 5):
            x = rect.left() + i * rect.width() / 5
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))

        # bordure
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawRoundedRect(QRectF(rect), 6, 6)

        if len(self.values) < 2:
            painter.setPen(QColor("#7a7a7a"))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "En attente de données")
            return

        data = list(self.values)

        ymin = self.y_min_forced if self.y_min_forced is not None else min(data)
        ymax = self.y_max_forced if self.y_max_forced is not None else max(data)

        if ymin == ymax:
            ymin -= 1.0
            ymax += 1.0

        # marge verticale
        span = ymax - ymin
        ymin -= 0.05 * span
        ymax += 0.05 * span

        points = []
        n = len(data)
        for i, v in enumerate(data):
            x = rect.left() + (i / (n - 1)) * rect.width()
            y = rect.bottom() - ((v - ymin) / (ymax - ymin)) * rect.height()
            points.append((x, y))

        # courbe
        curve_pen = QPen(self.color, 2)
        painter.setPen(curve_pen)
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # dernière valeur
        x_last, y_last = points[-1]
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(x_last) - 3, int(y_last) - 3, 6, 6)

        # labels min / max
        painter.setPen(QColor("#9a9a9a"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(
            rect.adjusted(4, 2, -4, -rect.height() + 14),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop),
            f"{ymax:.1f}",
        )
        painter.drawText(
            rect.adjusted(4, rect.height() - 14, -4, 0),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom),
            f"{ymin:.1f}",
        )

class StatsPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self._voltage = 0.0
        self._current = 0.0
        self._power = 0.0
        self._speed = 0.0

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")

        self._build_ui()
        self._connect_signals()

        # timer de rafraîchissement léger au cas où certaines valeurs changent ensemble
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_cards)
        self._refresh_timer.start(200)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        title = QLabel("STATISTIQUES / SUPERVISION")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: 700;")
        root.addWidget(title)

        subtitle = QLabel("Historique court pour suivi consommation et aide au diagnostic")
        subtitle.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        self.card_voltage = TimeSeriesCard("Tension batterie", "V", "#4fc3f7")
        self.card_current = TimeSeriesCard("Courant batterie", "A", "#ffb74d")
        self.card_power = TimeSeriesCard("Puissance batterie", "W", "#81c784")
        self.card_speed = TimeSeriesCard("Vitesse", "km/h", "#e57373", y_min=0)

        grid.addWidget(self.card_voltage, 0, 0)
        grid.addWidget(self.card_current, 0, 1)
        grid.addWidget(self.card_power, 1, 0)
        grid.addWidget(self.card_speed, 1, 1)

        root.addLayout(grid, 1)

    def _connect_signals(self):
        # Connexions robustes : si un signal n'existe pas, la page continue à fonctionner
        if hasattr(self.store, "pack_voltage_changed"):
            self.store.pack_voltage_changed.connect(self._on_voltage)

        if hasattr(self.store, "pack_current_changed"):
            self.store.pack_current_changed.connect(self._on_current)

        if hasattr(self.store, "speed_changed"):
            self.store.speed_changed.connect(self._on_speed)

    def _on_voltage(self, value):
        try:
            self._voltage = float(value)
        except Exception:
            self._voltage = 0.0
        self._power = self._voltage * self._current

    def _on_current(self, value):
        try:
            self._current = float(value)
        except Exception:
            self._current = 0.0
        self._power = self._voltage * self._current

    def _on_speed(self, value):
        try:
            self._speed = float(value)
        except Exception:
            self._speed = 0.0

    def _refresh_cards(self):
        self.card_voltage.push_value(self._voltage)
        self.card_current.push_value(self._current)
        self.card_power.push_value(self._power)
        self.card_speed.push_value(self._speed)