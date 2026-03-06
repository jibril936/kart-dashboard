import math

from qtpy.QtCore import QPointF, QRectF, Qt
from qtpy.QtGui import QColor, QFont, QPainter, QPen
from qtpy.QtWidgets import QWidget


class AnalogGaugeWidget(QWidget):
    def __init__(
        self,
        minValue=0,
        maxValue=100,
        units="",
        scalaCount=10,
        parent=None,
    ):
        super().__init__(parent)

        self.minValue = float(minValue)
        self.maxValue = float(maxValue)
        self.units = str(units)
        self.scalaCount = max(2, int(scalaCount))
        self.value = self.minValue

        self.startAngle = 225
        self.endAngle = -45

        self.setMinimumSize(180, 180)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def setValue(self, value):
        value = float(value)
        value = max(self.minValue, min(self.maxValue, value))
        if value != self.value:
            self.value = value
            self.update()

    def _format_center_value(self):
        abs_value = abs(self.value)

        if self.units.lower() == "w":
            return f"{int(round(self.value))}", "W"

        if self.units.lower() == "kw":
            if abs_value < 1.0:
                return f"{int(round(self.value * 1000.0))}", "W"
            return f"{self.value:.2f}", "kW"

        return f"{self.value:.1f}", self.units

    def _value_to_angle(self, value):
        span = self.maxValue - self.minValue
        if span <= 0:
            return self.startAngle

        ratio = (value - self.minValue) / span
        angle = self.startAngle + ratio * (self.endAngle - self.startAngle)
        return angle

    def paintEvent(self, event):
        del event

        side = min(self.width(), self.height())
        margin = 12

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 240.0, side / 240.0)

        # fond
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(8, 8, 8))
        painter.drawEllipse(QPointF(0, 0), 112, 112)

        # anneau externe
        pen = QPen(QColor(60, 60, 60), 8)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        rect = QRectF(-92, -92, 184, 184)
        painter.drawArc(rect, int((90 - self.startAngle) * 16), int(-(self.endAngle - self.startAngle) * 16))

        # graduation
        tick_pen = QPen(QColor(190, 190, 190), 2)
        painter.setPen(tick_pen)

        for i in range(self.scalaCount + 1):
            ratio = i / self.scalaCount
            value = self.minValue + ratio * (self.maxValue - self.minValue)
            angle_deg = self._value_to_angle(value)
            angle = math.radians(angle_deg)

            x1 = math.cos(angle) * 76
            y1 = -math.sin(angle) * 76
            x2 = math.cos(angle) * 88
            y2 = -math.sin(angle) * 88
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            label = f"{int(round(value))}"
            lx = math.cos(angle) * 62
            ly = -math.sin(angle) * 62

            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.setPen(QColor(180, 180, 180))
            painter.drawText(QRectF(lx - 16, ly - 8, 32, 16), Qt.AlignmentFlag.AlignCenter, label)
            painter.setPen(tick_pen)

        # zones traction / regen si jauge bipolaire
        if self.minValue < 0 < self.maxValue:
            zero_angle = self._value_to_angle(0.0)
            pos_pen = QPen(QColor(90, 200, 120), 6)
            neg_pen = QPen(QColor(80, 140, 220), 6)

            # côté négatif
            painter.setPen(neg_pen)
            painter.drawArc(
                QRectF(-84, -84, 168, 168),
                int((90 - self.startAngle) * 16),
                int(-(zero_angle - self.startAngle) * 16),
            )

            # côté positif
            painter.setPen(pos_pen)
            painter.drawArc(
                QRectF(-84, -84, 168, 168),
                int((90 - zero_angle) * 16),
                int(-(self.endAngle - zero_angle) * 16),
            )

        # aiguille
        angle_deg = self._value_to_angle(self.value)
        angle = math.radians(angle_deg)

        painter.save()
        painter.rotate(-angle_deg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(220, 60, 60))
        points = [
            QPointF(0, -4),
            QPointF(72, 0),
            QPointF(0, 4),
            QPointF(-12, 0),
        ]
        painter.drawPolygon(points)
        painter.restore()

        # centre
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(26, 26, 26))
        painter.drawEllipse(QPointF(0, 0), 12, 12)

        # texte central
        value_text, unit_text = self._format_center_value()

        font_value = QFont()
        font_value.setPointSize(20)
        font_value.setBold(True)
        painter.setFont(font_value)
        painter.setPen(QColor(245, 245, 245))
        painter.drawText(QRectF(-60, -18, 120, 26), Qt.AlignmentFlag.AlignCenter, value_text)

        font_unit = QFont()
        font_unit.setPointSize(9)
        painter.setFont(font_unit)
        painter.setPen(QColor(180, 180, 180))
        painter.drawText(QRectF(-60, 12, 120, 18), Qt.AlignmentFlag.AlignCenter, unit_text)

        # labels regen / traction si jauge bipolaire
        if self.minValue < 0 < self.maxValue:
            font_tag = QFont()
            font_tag.setPointSize(8)
            painter.setFont(font_tag)

            painter.setPen(QColor(80, 140, 220))
            painter.drawText(QRectF(-95, 70, 60, 18), Qt.AlignmentFlag.AlignCenter, "CHARGE")

            painter.setPen(QColor(90, 200, 120))
            painter.drawText(QRectF(35, 70, 60, 18), Qt.AlignmentFlag.AlignCenter, "POWER")