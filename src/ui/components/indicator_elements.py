from qtpy.QtWidgets import QWidget, QHBoxLayout, QLabel
from qtpy.QtGui import QPainter, QColor, QFont
from qtpy.QtCore import Qt

class IconAlertBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        # États des alertes : False = Gris, True = Couleur
        self.states = {
            "READY": True, "BRAKE": False, "MOT_TEMP": False, 
            "BATT_TEMP": False, "LOW_BATT": False, "LIMIT": False
        }

    def update_alert(self, key, state):
        if key in self.states:
            self.states[key] = state
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        icons = [
            ("READY", QColor(0, 255, 255), "READY"),
            ("BRAKE", QColor(255, 50, 50), "BRAKE"),
            ("MOT_TEMP", QColor(255, 80, 0), "MOT-T"),
            ("BATT_TEMP", QColor(255, 80, 0), "BAT-T"),
            ("LOW_BATT", QColor(255, 30, 30), "LOW-B"),
            ("LIMIT", QColor(255, 200, 0), "LIMIT")
        ]

        w = self.width() / len(icons)
        for i, (key, color, label) in enumerate(icons):
            active = self.states[key]
            rect = Qt.AlignmentFlag.AlignCenter
            
            # Dessin du texte de l'icône
            p.setPen(color if active else QColor(40, 40, 40))
            p.setFont(QFont("Orbitron", 10, QFont.Weight.Bold))
            p.drawText(int(i*w), 0, int(w), 50, int(rect), label)
            
            # Petit trait sous l'icône active
            if active:
                p.fillRect(int(i*w + w*0.2), 40, int(w*0.6), 3, color)

# --- (Garde SegmentedTempBar ici, tel que défini précédemment) ---

# --- 2. JAUGE DE TEMPÉRATURE SEGMENTÉE ---
class SegmentedTempBar(QWidget):
    """Barre de température segmentée optimisée pour 800x480."""
    def __init__(self, label="TEMP", parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 45)
        self.value = 0.0
        self.label = label

    def set_value(self, val):
        self.value = val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        num_segs = 12
        spacing = 3
        seg_w = (self.width() - (num_segs * spacing)) // num_segs
        
        # En PyQt6, Qt.NoPen devient Qt.PenStyle.NoPen
        p.setPen(Qt.PenStyle.NoPen)
        
        for i in range(num_segs):
            threshold = (i / num_segs) * 100
            if i < 7: color = QColor(0, 255, 150) # Vert
            elif i < 10: color = QColor(255, 165, 0) # Orange
            else: color = QColor(255, 50, 50) # Rouge
            
            # Application de la couleur ou du gris (éteint)
            p.setBrush(color if self.value > threshold else QColor(40, 40, 40))
            p.drawRect(i * (seg_w + spacing), 10, seg_w, 12)
            
        # Textes (Correction des couleurs Qt.White -> QColor)
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Orbitron", 8))
        
        # Flags d'alignement explicites pour PyQt6
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft, self.label)
        
        p.setPen(QColor(255, 255, 255)) # Remplace Qt.White qui posait problème
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, f"{int(self.value)}°C")