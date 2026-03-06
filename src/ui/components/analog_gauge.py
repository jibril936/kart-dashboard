import math

from qtpy.QtCore import QPoint, QRect, Qt, Signal
from qtpy.QtGui import QColor, QFont, QPainter, QPen, QPolygon
from qtpy.QtWidgets import QWidget


class AnalogGaugeWidget(QWidget):
    valueChanged = Signal(int)

    def __init__(
        self,
        minValue=0,
        maxValue=100,
        units="",
        gaugeColor="#00FFFF",
        scalaCount=10,
        parent=None,
    ):
        super().__init__(parent)

        self.minValue = float(minValue)
        self.maxValue = float(maxValue)
        self.units = units
        self.gaugeColor = QColor(gaugeColor)
        self.value = float(minValue)
        self.scalaCount = int(scalaCount)
        self.subDivCount = 5

        self.scale_angle_start_value = 135
        self.scale_angle_size = 270

        self.setMinimumSize(300, 300)

    def setValue(self, value):
        try:
            val = float(value)
            self.value = max(self.minValue, min(self.maxValue, val))
            self.valueChanged.emit(int(self.value))
            self.update()
        except Exception:
            pass

    def paintEvent(self, event):
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        self.diameter = min(w, h)

        painter.translate(w / 2, h / 2)

        self.draw_fine_ticks(painter)
        self.draw_scale_markers(painter)
        self.draw_scale(painter)
        self.draw_progress(painter)
        self.draw_needle(painter)
        self.draw_digital_value(painter)

    def draw_fine_ticks(self, painter):
        painter.save()

        pen = QPen(QColor(80, 80, 80), 1)
        painter.setPen(pen)

        total_ticks = self.scalaCount * self.subDivCount
        radius_outer = self.diameter / 2 - 5
        radius_inner = self.diameter / 2 - 15

        for i in range(total_ticks + 1):
            angle = math.radians(
                self.scale_angle_start_value + (i * self.scale_angle_size / total_ticks)
            )
            x1 = radius_outer * math.cos(angle)
            y1 = radius_outer * math.sin(angle)
            x2 = radius_inner * math.cos(angle)
            y2 = radius_inner * math.sin(angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.restore()

    def draw_scale(self, painter):
        painter.save()

        pen = QPen(QColor(60, 60, 60), 2)
        painter.setPen(pen)

        painter.drawArc(
            int(-self.diameter / 2 + 5),
            int(-self.diameter / 2 + 5),
            int(self.diameter - 10),
            int(self.diameter - 10),
            int(-self.scale_angle_start_value * 16),
            int(-self.scale_angle_size * 16),
        )

        painter.restore()

    def draw_progress(self, painter):
        painter.save()

        span_total = self.maxValue - self.minValue
        if span_total <= 0:
            painter.restore()
            return

        val_ratio = (self.value - self.minValue) / span_total
        current_angle = self.scale_angle_start_value + (val_ratio * self.scale_angle_size)

        pen_width = 8

        # Jauge vitesse = cyan plein arc depuis le début
        if self.units == "km/h":
            color = QColor(0, 255, 255)
            start_angle = self.scale_angle_start_value

        else:
            # Jauge puissance bipolaire :
            # départ à zéro, négatif d'un côté, positif de l'autre
            if self.minValue < 0 < self.maxValue:
                zero_ratio = (0.0 - self.minValue) / span_total
                start_angle = self.scale_angle_start_value + (zero_ratio * self.scale_angle_size)
            else:
                start_angle = self.scale_angle_start_value

            if self.value < 0:
                color = QColor(0, 255, 127)
            else:
                if self.maxValue > 0:
                    pos_ratio = self.value / self.maxValue
                else:
                    pos_ratio = 0.0

                if pos_ratio < 0.33:
                    color = QColor(255, 255, 0)
                elif pos_ratio < 0.66:
                    color = QColor(255, 150, 0)
                else:
                    color = QColor(255, 50, 50)

        painter.setPen(QPen(color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        span = -(current_angle - start_angle)
        painter.drawArc(
            int(-self.diameter / 2 + 5),
            int(-self.diameter / 2 + 5),
            int(self.diameter - 10),
            int(self.diameter - 10),
            int(-start_angle * 16),
            int(span * 16),
        )

        painter.restore()

    def draw_digital_value(self, painter):
        painter.save()

        y_base = int(self.diameter / 6.0)

        painter.setPen(QColor(255, 255, 255))

        # Valeur principale
        font_val = QFont("Orbitron", int(self.diameter * 0.14), QFont.Weight.Bold)
        painter.setFont(font_val)

        val_rect = QRect(-100, y_base - 40, 200, 60)

        if self.units == "km/h":
            text_value = f"{self.value:.0f}"
        else:
            text_value = f"{self.value:.0f}"

        painter.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, text_value)

        # Unité
        font_unit = QFont("Orbitron", int(self.diameter * 0.04), QFont.Weight.Normal)
        painter.setFont(font_unit)
        painter.setPen(QColor(140, 140, 140))

        unit_rect = QRect(-100, y_base + 30, 200, 30)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, self.units)

        painter.restore()

    def draw_scale_markers(self, painter):
        painter.save()

        painter.setPen(QColor(100, 100, 100))
        painter.setFont(QFont("Orbitron", 7))

        radius = self.diameter / 2 - 45

        for i in range(self.scalaCount + 1):
            val = self.minValue + (i * (self.maxValue - self.minValue) / self.scalaCount)
            angle = math.radians(
                self.scale_angle_start_value + (i * self.scale_angle_size / self.scalaCount)
            )
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            if abs(val) < 0.0001:
                label = "0"
            else:
                label = f"{val:.0f}"

            painter.drawText(
                QRect(int(x) - 20, int(y) - 10, 40, 20),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        painter.restore()

    def draw_needle(self, painter):
        painter.save()

        span_total = self.maxValue - self.minValue
        if span_total <= 0:
            painter.restore()
            return

        ratio = (self.value - self.minValue) / span_total
        angle = self.scale_angle_start_value + (ratio * self.scale_angle_size)

        painter.rotate(angle)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))

        needle = QPolygon(
            [
                QPoint(int(self.diameter / 2 - 15), 0),
                QPoint(0, 3),
                QPoint(0, -3),
            ]
        )
        painter.drawConvexPolygon(needle)

        painter.restore()