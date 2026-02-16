from qtpy.QtWidgets import QMainWindow, QStackedWidget
from qtpy.QtCore import Qt
from src.ui.screens.cluster_page import ClusterPage
from src.ui.screens.expert_page import ExpertPage

class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.resize(1024, 600)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Création des pages
        self.page_cluster = ClusterPage(self.store)
        self.page_expert = ExpertPage(self.store)
        
        self.stack.addWidget(self.page_cluster)
        self.stack.addWidget(self.page_expert)

    def keyPressEvent(self, event):
        # Touche 1 -> Pilotage / Touche 2 -> Diagnostic
        if event.key() == Qt.Key.Key_1:
            self.stack.setCurrentIndex(0)
        elif event.key() == Qt.Key.Key_2:
            self.stack.setCurrentIndex(1)