import sys
import signal
from PyQt6.QtWidgets import QApplication

# Import de la structure
from src.main_window import MainWindow
from src.core.state_store import StateStore

# Import des deux moteurs (Services)
from src.core.mock_service import MockService
from src.core.hardware_service import HardwareService

def main() -> int:
    # 1. Initialisation de l'application Qt
    app = QApplication(sys.argv)

    # 2. Création du "Cerveau" unique (StateStore)
    # C'est l'objet que tout le monde va écouter
    state_store = StateStore()

    # 3. Création des services
    # On leur donne le même cerveau pour qu'ils puissent y écrire en parallèle
    simu_service = MockService(state_store)      # Gère Vitesse, Direction, etc.
    bms_service = HardwareService(state_store)   # Gère ton vrai BMS (RS485)

    # 4. Création de l'interface
    # On lui donne aussi le cerveau pour qu'elle puisse lire les données
    window = MainWindow(state_store)
    window.show()

    # 5. Démarrage des moteurs
    # Ils tournent chacun dans leur propre Thread (fil d'exécution)
    print("--- Démarrage des services ---")
    simu_service.start()
    bms_service.start()

    # 6. Gestion propre de la fermeture
    def shutdown(*_args):
        print("\nArrêt en cours...")
        simu_service.stop()
        bms_service.stop()
        app.quit()

    # Capture le Ctrl+C dans le terminal et la fermeture de la fenêtre
    app.aboutToQuit.connect(shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # Lancement de la boucle d'affichage
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        pass