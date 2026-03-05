from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget


class NavBar(QWidget):
    page_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 5)
        layout.setSpacing(12)

        self.buttons = []
        labels = ["DRIVE", "BMS EXPERT", "STATS"]

        for i, label in enumerate(labels):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedSize(180, 45)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

            # Style via QSS
            btn.setProperty("nav", True)

            btn.clicked.connect(lambda checked, index=i: self._on_click(index))
            layout.addWidget(btn)
            self.buttons.append(btn)

        self.buttons[0].setChecked(True)

    def _on_click(self, index: int):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)

        self.page_selected.emit(index)