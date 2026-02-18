from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton
from qtpy.QtCore import Signal, Qt

class NavBar(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 5)
        
        self.buttons = []
        labels = ["DRIVE", "BMS EXPERT", "STATS"]
        
        for i, label in enumerate(labels):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedSize(180, 45)
            btn.setStyleSheet("""
                QPushButton {
                    background: #111; color: #555; border: 1px solid #222;
                    border-radius: 10px; font-family: 'Orbitron'; font-weight: bold;
                }
                QPushButton:checked {
                    background: #00FFFF; color: black; border: none;
                }
            """)
            btn.clicked.connect(lambda checked, index=i: self._on_click(index))
            layout.addWidget(btn)
            self.buttons.append(btn)
        
        self.buttons[0].setChecked(True)

    def _on_click(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.page_selected.emit(index)