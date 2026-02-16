import math
from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QPolygon, QColor, QPen, QFont, QPainter
from qtpy.QtCore import Qt, QPoint, QRect, Signal

class AnalogGaugeWidget(QWidget):
    valueChanged = Signal(int)

    def __init__(self, minValue=0, maxValue=100, units="", gaugeColor="#00FFFF", scalaCount=10, parent=None):
        super().__init__(parent)
        self.minValue = minValue
        self.maxValue = maxValue
        self.units = units
        self.gaugeColor = QColor(gaugeColor)
        self.value = minValue
        self.scalaCount = scalaCount 
        self.subDivCount = 5 # Nombre de petits traits entre chaque gros chiffre
        
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270
        self.setMinimumSize(300, 300)

    def setValue(self, value):
        try:
            val = float(value)
            self.value = max(self.minValue, min(self.maxValue, val))
            self.update()
        except: pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        self.diameter = min(w, h)
        painter.translate(w / 2, h / 2)

        self.draw_fine_ticks(painter)    # Les petites graduations (nouveauté)
        self.draw_scale_markers(painter) # Les gros chiffres
        self.draw_scale(painter)         # L'arc de fond
        self.draw_progress(painter)      # L'arc coloré
        self.draw_needle(painter)        # L'aiguille
        self.draw_digital_value(painter) # Les chiffres numériques remontés

    def draw_fine_ticks(self, painter):
        """Dessine les petits traits de graduation pour le look 'Pro'"""
        painter.save()
        pen = QPen(QColor(80, 80, 80), 1)
        painter.setPen(pen)
        
        total_ticks = self.scalaCount * self.subDivCount
        radius_outer = self.diameter / 2 - 5
        radius_inner = self.diameter / 2 - 15

        for i in range(total_ticks + 1):
            angle = math.radians(self.scale_angle_start_value + (i * self.scale_angle_size / total_ticks))
            x1 = radius_outer * math.cos(angle)
            y1 = radius_outer * math.sin(angle)
            x2 = radius_inner * math.cos(angle)
            y2 = radius_inner * math.sin(angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.restore()

    def draw_scale(self, painter):
        painter.save()
        pen = QPen(QColor(60, 60, 60), 2) # Un peu plus fin pour laisser voir les ticks
        painter.setPen(pen)
        painter.drawArc(int(-self.diameter/2 + 5), int(-self.diameter/2 + 5), self.diameter-10, self.diameter-10, 
                        -self.scale_angle_start_value * 16, -self.scale_angle_size * 16)
        painter.restore()

    def draw_progress(self, painter):
        painter.save()
        val_ratio = (self.value - self.minValue) / (self.maxValue - self.minValue)
        current_angle = self.scale_angle_start_value + (val_ratio * self.scale_angle_size)
        pen_width = 8
        
        # Logique de couleur Vitesse (Cyan) vs Puissance (Multi-couleur)
        if self.units == "km/h":
            color = QColor(0, 255, 255)
            start_angle = self.scale_angle_start_value
        else:
            # Pour les kW, on part toujours du Zéro
            zero_ratio = (0 - self.minValue) / (self.maxValue - self.minValue)
            start_angle = self.scale_angle_start_value + (zero_ratio * self.scale_angle_size)
            
            if self.value < 0: color = QColor(0, 255, 127)
            else:
                pos_ratio = self.value / self.maxValue
                if pos_ratio < 0.33: color = QColor(255, 255, 0)
                elif pos_ratio < 0.66: color = QColor(255, 150, 0)
                else: color = QColor(255, 50, 50)

        painter.setPen(QPen(color, pen_width, Qt.SolidLine, Qt.RoundCap))
        span = -(current_angle - start_angle)
        painter.drawArc(int(-self.diameter/2 + 5), int(-self.diameter/2 + 5), self.diameter-10, self.diameter-10, 
                        int(-start_angle * 16), int(span * 16))
        painter.restore()

    def draw_digital_value(self, painter):
        painter.save()
        # On remonte encore l'ensemble (plus le diviseur est grand, plus on monte)
        # On passe à 6 pour libérer vraiment le bas du cadran
        y_base = int(self.diameter / 6.0) 
        
        painter.setPen(QColor(255, 255, 255))
        
        # 1. CHIFFRE PRINCIPAL (Réduit à 14% du diamètre pour plus de finesse)
        font_val = QFont("Orbitron", int(self.diameter * 0.14), QFont.Weight.Bold)
        painter.setFont(font_val)
        
        # Rectangle de dessin du chiffre
        val_rect = QRect(-100, y_base - 40, 200, 60)
        painter.drawText(val_rect, Qt.AlignCenter, f"{abs(self.value):.0f}")
        
        # 2. UNITÉ (Réduite à 4% et passée en gris plus sombre pour le contraste)
        font_unit = QFont("Orbitron", int(self.diameter * 0.04), QFont.Weight.Normal)
        painter.setFont(font_unit)
        painter.setPen(QColor(140, 140, 140)) # Gris plus discret
        
        # On augmente l'écart : positionnée 35 pixels sous la base du chiffre
        unit_rect = QRect(-100, y_base + 30, 200, 30)
        painter.drawText(unit_rect, Qt.AlignCenter, self.units)
        painter.restore()

    def draw_scale_markers(self, painter):
        """Graduations encore plus discrètes pour ne pas polluer le regard"""
        painter.save()
        painter.setPen(QColor(100, 100, 100)) # Gris plus sombre
        painter.setFont(QFont("Orbitron", 7)) # Plus petit
        radius = self.diameter / 2 - 45 # On les éloigne encore un peu du bord
        
        for i in range(self.scalaCount + 1):
            val = self.minValue + (i * (self.maxValue - self.minValue) / self.scalaCount)
            angle = math.radians(self.scale_angle_start_value + (i * self.scale_angle_size / self.scalaCount))
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            painter.drawText(QRect(int(x)-20, int(y)-10, 40, 20), Qt.AlignCenter, f"{val:.0f}")
        painter.restore()

    def draw_needle(self, painter):
        painter.save()
        ratio = (self.value - self.minValue) / (self.maxValue - self.minValue)
        angle = self.scale_angle_start_value + (ratio * self.scale_angle_size)
        painter.rotate(angle)
        painter.setPen(Qt.NoPen)
        # Aiguille blanche pour ressortir sur les couleurs
        painter.setBrush(QColor(255, 255, 255))
        needle = QPolygon([QPoint(int(self.diameter/2 - 15), 0), QPoint(0, 3), QPoint(0, -3)])
        painter.drawConvexPolygon(needle)
        painter.restore()