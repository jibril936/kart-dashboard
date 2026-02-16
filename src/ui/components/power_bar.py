from qtpy.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve
from qtpy.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen
from qtpy.QtWidgets import QWidget

class PowerBar(QWidget): # Nom corrigé
    def __init__(self, parent=None):
        super().__init__(parent)
        self.display_kw = 0.0
        self.max_kw = 30.0 # Puissance max estimée du Kart
        self.setFixedHeight(60)

        self.animation = QVariantAnimation()
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutQuint)
        self.animation.valueChanged.connect(self._animate)

    def _animate(self, value):
        self.display_kw = value
        self.update()

    def update_power(self, voltage, current):
        kw = (voltage * current) / 1000.0
        self.animation.setStartValue(self.display_kw)
        self.animation.setEndValue(float(kw))
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        center_x, bar_h, bar_y = w // 2, 10, 15
        margin = 100

        # Fond sombre (Style Khamisi Theme 3)
        painter.setBrush(QColor(25, 25, 28))
        painter.setPen(QPen(QColor(50, 50, 55), 1))
        painter.drawRoundedRect(margin, bar_y, w - (margin*2), bar_h, 5, 5)

        # Calcul de la barre
        val_ratio = self.display_kw / self.max_kw
        active_w = abs(val_ratio * ((w - (margin*2)) / 2))

        if self.display_kw >= 0:
            grad = QLinearGradient(center_x, bar_y, center_x + active_w, bar_y)
            grad.setColorAt(0, QColor(0, 164, 189, 150)) # Cyan
            grad.setColorAt(1, QColor(85, 255, 255, 255))
        else:
            grad = QLinearGradient(center_x, bar_y, center_x - active_w, bar_y)
            grad.setColorAt(0, QColor(0, 150, 100, 150)) # Vert Regen
            grad.setColorAt(1, QColor(0, 255, 127, 255))
        
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        start_x = center_x if self.display_kw >= 0 else center_x - active_w
        painter.drawRect(QRectF(float(start_x), float(bar_y), float(active_w), float(bar_h)))

        # Texte kW central
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Orbitron", 10, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, f"{self.display_kw:.1f} kW")