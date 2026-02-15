# Architecture technique

Ce document décrit les **4 piliers** de l'architecture de Kart Dashboard Pro V3. L'objectif est de garantir une exécution fluide sur Raspberry Pi 4, tout en gardant une base logicielle industrialisable.

## 1) Couche Hardware / Service

Cette couche encapsule l'accès aux périphériques physiques (I2C, USB, etc.) et protège l'interface graphique contre les blocages liés aux entrées/sorties.

### Responsabilités
- Lire les données capteurs en continu.
- Isoler la logique d'accès matériel.
- Publier des données normalisées vers la couche Core.

### Mécanisme d'exécution
- Utilisation de **`QThread`** pour déplacer les lectures I/O hors du thread UI.
- Chaque service fonctionne de manière asynchrone pour éviter tout gel de l'interface.

## 2) Couche Simulation

La couche Simulation fournit un **`MockService`** qui reproduit le comportement des capteurs sans matériel connecté.

### Objectifs
- Développer et tester l'UI et la logique métier sans dépendance matérielle.
- Reproduire des scénarios (valeurs nominales, pics, erreurs, pertes de signal).
- Faciliter l'intégration continue et les démonstrations.

Le `MockService` suit les mêmes contrats d'interface que les services réels, ce qui permet un remplacement transparent.

## 3) Couche Core (StateStore)

Le **`StateStore`** est le cerveau du système.

### Rôle central
- Il constitue **l'unique source de vérité** (*single source of truth*).
- Il reçoit les données des services (réels ou simulés).
- Il valide, agrège et stocke l'état applicatif courant.

### Communication
- Le Store diffuse les changements via des **`pyqtSignal`**.
- Les consommateurs s'abonnent aux signaux au lieu d'accéder directement aux services.

Ce modèle limite les couplages transverses et améliore la traçabilité des données.

## 4) Couche UI

La couche UI est strictement découplée des entrées matérielles.

### Principes
- L'interface ne lit pas les capteurs directement.
- Elle ne contient pas de logique d'acquisition.
- Elle se contente de **dessiner l'état** publié par le Store.

Résultat : une UI plus stable, plus simple à maintenir, et plus facile à faire évoluer (nouveaux widgets, thèmes, écrans).

## Flux de données

```mermaid
flowchart LR
    A[Capteurs I2C/USB] --> B[Service (QThread)]
    A2[MockService (Simulation)] --> B
    B --> C[StateStore (single source of truth)]
    C -->|pyqtSignal| D[UI (rendu uniquement)]
```

## Résumé des bénéfices

- **Temps réel robuste** : I/O hors thread UI.
- **Développement accéléré** : simulation sans matériel.
- **Cohérence fonctionnelle** : état centralisé.
- **Modularité** : UI découplée et remplaçable.
