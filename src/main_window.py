from qtpy.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from qtpy.QtCore import Qt
from src.ui.screens.cluster_page import ClusterPage
from src.ui.screens.expert_page import ExpertPage
from src.ui.components.nav_bar import NavBar

class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        
        # 1. CONFIGURATION DE LA FENÊTRE
        self.setWindowTitle("Kart Dashboard Pro")
        # On ajuste à la résolution réelle de ton écran 7 pouces
        self.setFixedSize(800, 480) 
        self.setStyleSheet("background-color: black;")
        
        # Pour cacher le curseur de la souris sur l'écran tactile (optionnel)
        # self.setCursor(Qt.BlankCursor) 
        
        # 2. CONTENEUR PRINCIPAL (Layout Vertical)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Plein écran sans bordures
        self.main_layout.setSpacing(0)

        # 3. LE STACKED WIDGET (Les Pages)
        self.stack = QStackedWidget()
        
        # Initialisation des pages avec le store partagé
        self.page_cluster = ClusterPage(self.store)
        self.page_expert = ExpertPage(self.store)
        # self.page_stats = StatsPage(self.store) # À décommenter une fois créée

        self.stack.addWidget(self.page_cluster) # Index 0
        self.stack.addWidget(self.page_expert)  # Index 1
        
        # Le stack prend tout l'espace disponible en haut
        self.main_layout.addWidget(self.stack)

        # 4. LA BARRE DE NAVIGATION (Tactile)
        # Placée en bas pour un accès facile avec les pouces
        self.nav_bar = NavBar()
        self.main_layout.addWidget(self.nav_bar)

        # 5. CONNEXIONS
        # Le signal de la NavBar pilote directement le changement de page
        self.nav_bar.page_selected.connect(self.stack.setCurrentIndex)

    def keyPressEvent(self, event):
        """Gestion du clavier pour le débug ou les boutons physiques externes."""
        if event.key() == Qt.Key.Key_1:
            self._update_navigation(0)
        elif event.key() == Qt.Key.Key_2:
            self._update_navigation(1)
        elif event.key() == Qt.Key.Key_3:
            self._update_navigation(2)
        
        # Optionnel : Touche 'F' pour basculer en plein écran
        elif event.key() == Qt.Key.Key_F:
            if self.isFullScreen(): self.showNormal()
            else: self.showFullScreen()

    def _update_navigation(self, index):
        """Synchronise le stack et l'état visuel de la NavBar."""
        if index < self.stack.count():
            self.stack.setCurrentIndex(index)
            # On informe la nav_bar du changement (pour mettre à jour le bouton actif)
            if hasattr(self.nav_bar, 'set_active_button'):
                self.nav_bar.set_active_button(index)

    def closeEvent(self, event):
        """S'assure que les services s'arrêtent proprement à la fermeture."""
        # Tu peux ajouter ici des appels pour stopper tes threads HardwareService
        super().closeEvent(event)