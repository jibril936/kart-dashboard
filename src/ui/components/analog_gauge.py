import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (QPolygon, QColor, QPen, QFont, QPainter, 
                         QFontMetrics, QConicalGradient, QRadialGradient)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QSize, pyqtSignal

class AnalogGaugeWidget(QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(
        self, 
        minValue: float = 0.0, 
        maxValue: float = 100.0, 
        units: str = "km/h", 
        gaugeColor: str = "#00FFFF", 
        parent=None
    ):
        super().__init__(parent)

        # On utilise les valeurs reçues en paramètres
        self.minValue = minValue
        self.maxValue = maxValue
        self.units = units
        self.NeedleColor = QColor(gaugeColor) 
        
        # Le reste de ta configuration
        self.value = minValue
        self.use_timer_event = False
        self.DisplayValueColor = QColor(245, 245, 245)
        self.ScaleValueColor = QColor(200, 200, 200)
        self.bigScaleMarker = QColor(100, 100, 100)
        self.fineScaleColor = QColor(50, 50, 50)
        
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270
        self.scalaCount = 10
        self.scala_subdiv_count = 5
        
        self.setMinimumSize(250, 250)
        self.rescale_method()

    def setValue(self, value):
        """Méthode compatible avec ton ClusterPage actuel"""
        if value <= self.minValue:
            self.value = self.minValue
        elif value >= self.maxValue:
            self.value = self.maxValue
        else:
            self.value = value
        self.update() # Force le redessin

    def rescale_method(self):
        self.widget_diameter = min(self.width(), self.height())
        # Définition de la forme de l'aiguille (Polygon)
        self.value_needle = [QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, int(-self.widget_diameter / 2 * 0.8)),
            QPoint(0, int(-self.widget_diameter / 2 * 0.8 - 6)),
            QPoint(2, int(-self.widget_diameter / 2 * 0.8))
        ])]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # On dessine sur fond noir pur
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        
        self.rescale_method()
        self.draw_filled_polygon(painter)
        self.draw_big_scaled_marker(painter)
        self.create_fine_scaled_marker(painter)
        self.create_scale_marker_values_text(painter)
        self.create_values_text(painter)
        self.draw_needle(painter)

    def draw_filled_polygon(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.PenStyle.NoPen)

        # Création de l'arc de progression
        # On calcule le ratio de la valeur actuelle pour remplir l'arc
        progress_ratio = (self.value - self.minValue) / (self.maxValue - self.minValue)
        current_span = int(self.scale_angle_size * progress_ratio)

        # Dégradé Conique pour l'effet de couleur
        grad = QConicalGradient(QPointF(0, 0), -self.scale_angle_start_value)
        grad.setColorAt(0, self.NeedleColor)
        grad.setColorAt(1, QColor(30, 30, 30))
        
        painter.setBrush(grad)
        
        # Dessin simplifié de l'arc (plus performant pour la Pi)
        rect = QRect(int(-self.widget_diameter/2), int(-self.widget_diameter/2), 
                     self.widget_diameter, self.widget_diameter)
        painter.drawPie(rect, -self.scale_angle_start_value * 16, -current_span * 16)
        painter.restore()

    def draw_big_scaled_marker(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        pen = QPen(self.bigScaleMarker)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.rotate(self.scale_angle_start_value)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount))
        for i in range(self.scalaCount + 1):
            painter.drawLine(int(self.widget_diameter/2 - 10), 0, int(self.widget_diameter/2), 0)
            painter.rotate(steps_size)
        painter.restore()

    def create_fine_scaled_marker(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(self.fineScaleColor)
        painter.rotate(self.scale_angle_start_value)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount * self.scala_subdiv_count))
        for i in range((self.scalaCount * self.scala_subdiv_count) + 1):
            painter.drawLine(int(self.widget_diameter/2 - 5), 0, int(self.widget_diameter/2), 0)
            painter.rotate(steps_size)
        painter.restore()

    def create_scale_marker_values_text(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(self.ScaleValueColor)
        
        text_radius = self.widget_diameter/2 * 0.8
        scale_per_div = (self.maxValue - self.minValue) / self.scalaCount
        angle_distance = self.scale_angle_size / self.scalaCount
        
        for i in range(self.scalaCount + 1):
            text = str(int(self.minValue + scale_per_div * i))
            angle = math.radians(angle_distance * i + self.scale_angle_start_value)
            x = text_radius * math.cos(angle)
            y = text_radius * math.sin(angle)
            painter.drawText(int(x - 10), int(y + 5), text)
        painter.restore()

    def create_values_text(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(self.DisplayValueColor)
        
        # Valeur centrale massive
        font_value = QFont("Arial", int(self.widget_diameter * 0.15), QFont.Weight.Bold)
        painter.setFont(font_value)
        painter.drawText(QRect(int(-self.width()/2), -20, self.width(), 60), 
                         Qt.AlignmentFlag.AlignCenter, str(int(self.value)))
        
        # Unités en dessous
        font_units = QFont("Arial", int(self.widget_diameter * 0.05))
        painter.setFont(font_units)
        painter.drawText(QRect(int(-self.width()/2), 30, self.width(), 30), 
                         Qt.AlignmentFlag.AlignCenter, self.units)
        painter.restore()

    def draw_needle(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.NeedleColor)
        
        # Rotation de l'aiguille selon la valeur actuelle
        angle = ((self.value - self.minValue) * self.scale_angle_size / 
                 (self.maxValue - self.minValue)) + self.scale_angle_start_value
        painter.rotate(angle + 90)
        painter.drawConvexPolygon(self.value_needle[0])
        painter.restore()