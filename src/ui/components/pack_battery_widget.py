from qtpy.QtWidgets import QWidget
from qtpy.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from qtpy.QtCore import Qt, QRect

class PackBatteryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percentage = 0
        # Taille fixe pour que la grille puisse bien le centrer
        self.setFixedSize(200, 80) 

    def update_status(self, soc, volts=None):
        self.percentage = int(soc)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. La Barre (plus large pour remplir l'espace)
        w, h = 180, 12
        x = (self.width() - w) // 2
        y = 5 # Collé en haut du widget
        
        painter.setBrush(QColor(35, 35, 35))
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawRoundedRect(x, y, w, h, 6, 6)
        
        fill_w = int((self.percentage / 100) * w)
        if fill_w > 0:
            grad = QLinearGradient(x, y, x + fill_w, y)
            grad.setColorAt(0, QColor(0, 255, 127, 180)) 
            grad.setColorAt(1, QColor(0, 255, 127, 255))
            painter.setBrush(grad)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, fill_w, h, 6, 6)

        # 2. Le Texte (Parfaitement centré sous la barre)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Orbitron", 32, QFont.Weight.Bold))
        # Le rectangle prend tout le bas du widget pour centrer le texte
        painter.drawText(QRect(0, 25, self.width(), 55), Qt.AlignCenter, f"{self.percentage}%")