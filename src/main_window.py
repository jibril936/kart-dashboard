from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from src.core.state_store import StateStore
from src.ui.screens.cluster_page import ClusterPage


class MainWindow(QMainWindow):
    """Dashboard shell with a primary cluster page."""

    # On ajoute 'store' ici pour qu'il accepte l'argument envoyé par main.py
    def __init__(self, store: StateStore) -> None:
        super().__init__()
        self.setWindowTitle("Kart Dashboard")
        self.resize(1024, 600)
        self.setStyleSheet("background-color: #000000;")

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        # On utilise le store passé en paramètre au lieu d'en créer un nouveau !
        self.store = store 
        
        # On passe ce même store à la ClusterPage
        self.cluster_page = ClusterPage(self.store, self)
        
        self.stack.addWidget(self.cluster_page)
        self.stack.setCurrentWidget(self.cluster_page)