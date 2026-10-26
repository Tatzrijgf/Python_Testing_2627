<br />

# GÜDLFT — Plateforme Fédérale de Réservation Régionale( fait par AHOUSSI GOMIS)

> **Statut du Projet :** Production / Prêt pour Révision de Code (QA Branch)

Ce projet est une preuve de concept (POC) d'une application web légère d'administration conçue exclusivement pour les secrétaires de clubs sportifs. Elle leur permet d'échanger leurs points d'organisation contre des places d'accès rapide aux compétitions régionales pour leurs athlètes, éliminant ainsi la gestion administrative lourde tout en garantissant une transparence totale.

***

## 🏗️ Architecture Technique de l'Application

L'application est construite sur une architecture découplée, rapide et sans persistance sur base de données relationnelle lourde (conformément aux directives de réduction des temps de rendu et de configuration). Elle s'appuie sur des fichiers d'échange de données structurés au format JSON.

```text
📁 GUDLFT_PROJECT/
│
├── 📁 templates/               # Couche de Présentation (Moteur de rendu Jinja2)
│   ├── 📄 index.html           # Page d'accueil publique et formulaire d'authentification
│   ├── 📄 welcome.html         # Tableau de bord privé du secrétariat
│   ├── 📄 booking.html         # Formulaire d'achat et de réservation de places
│   └── 📄 points.html          # Tableau public des scores (Lecture seule — Phase 2)
│
├── 📁 tests/                   # Suite de Validation Automatisée (Normes QA)
│   ├── 📄 conftest.py          # Configuration des Fixtures et isolation de l'environnement Flask
│   ├── 📁 unit/                # Tests Unitaires (Logique de calcul, structures isolées)
│   │   └── 📄 test_server_units.py
│   └── 📁 integration/         # Tests d'Intégration (Cycles de requêtes HTTP, Happy/Sad paths)
│       └── 📄 test_server_integration.py
│
├── 📄 server.py                # Contrôleur Principal (Logique métier, contrôles de flux et routes API)
├── 📄 clubs.json               # Base de données volatile des associations sportives
├── 📄 competitions.json        # Base de données volatile des événements régionaux
├── 📄 locustfile.py            # Script d'injection de charge pour les tests de performance
└── 📄 requirements.txt         # Manifeste des dépendances gelées de l'environnement virtuel
```

***

## 🛠️ Cartographie Complète des Routes API

| Méthode  | Route HTTP            | Niveau d'accès     | Description Technique & Fonctionnelle                                         |
| :------- | :-------------------- | :----------------- | :---------------------------------------------------------------------------- |
| **GET**  | `/`                   | Public             | Page d'accueil. Présente le formulaire d'identification par e-mail.           |
| **GET**  | `/points`             | Public (Phase 2)   | Tableau d'affichage en lecture seule. Liste tous les clubs et leurs scores.   |
| **POST** | `/showSummary`        | Privé (Secrétaire) | Traite l'authentification et charge le tableau de bord du club ciblé.         |
| **GET**  | `/book/<comp>/<club>` | Privé (Secrétaire) | Génère le formulaire d'achat pour une compétition spécifique.                 |
| **POST** | `/purchasePlaces`     | Privé (Secrétaire) | Route transactionnelle critique. Valide et applique les déductions de stocks. |
| **GET**  | `/logout`             | Privé (Secrétaire) | Clôture la session courante et redirige vers la racine `/`.                   |

***

## 🔒 Matrice de Résolution des Bogues & Sécurisation (Sad Paths)

L'implémentation initiale présentait des vulnérabilités de logique métier qui ont été systématiquement corrigées au cours des sprints de la Phase 1 :

1. **Robustesse des Index (`IndexError`) :** Remplacement des accès par index direct sans vérification préalable. L'application intercepte désormais les altérations d'identifiants dans l'URL ou les formulaires et redirige proprement avec un message d'alerte.
2. **Déduction Équitable des Points :** Correction du défaut de facturation. Chaque réservation applique une déduction stricte sur le solde de points du club à raison de *1 point pour 1 place acquise*.
3. **Étanchéité des Soldes Créditeurs :** Blocage des transactions si la quantité de places demandées est supérieure au capital de points possédés par le club, empêchant les soldes négatifs.
4. **Plafond d'Équité Fédérale (Limite des 12 places) :** Implémentation d'une structure persistante en mémoire (`booking_history`) bloquant l'accumulation ou l'achat unitaire de plus de 12 places par club pour un même événement.
5. **Verrouillage Temporel :** Intégration du module `datetime`. L'application compare les dates des événements avec l'horloge système instantanée, désactivant l'achat sur les compétitions historiquement terminées.
6. **Contrôle d'Approvisionnement (Surréservation) :** Interdiction stricte de commander une quantité supérieure au volume physique de places disponibles (`numberOfPlaces`) dans la compétition.
7. **Sanitisation des Entrées Numériques :** Ajout de barrières de validation (HTML5 `min="1"` + contrôle serveur `placesRequired <= 0`) pour interdire l'injection de nombres négatifs ou nuls, qui permettaient de créditer frauduleusement des points.

***

## 🚀 Installation, Configuration et Déploiement Local

### Prérequis

* Python v3.12 ou supérieur (pleinement compatible avec la bibliothèque épurée `pkgutil` de Python 3.14).
* Outil de gestion des privilèges en ligne de commande.

### Procédure d'installation rapide

1. **Cloner le projet et se positionner dans le répertoire :**
   ```bash
   git clone <url-du-repo>
   cd Python_Testing_2627
   ```
2. **Initialiser l'environnement virtuel isolé :**
   ```bash
   python -m venv venv
   ```
3. **Activer l'environnement de travail :**
   * *Sur Windows (Prompt) :* `.\venv\Scripts\activate.bat`
   * *Sur Windows (PowerShell) :* `.\venv\Scripts\Activate.ps1`
   * *Sur Linux / macOS :* `source venv/bin/activate`
4. **Mettre à niveau l'installateur et déployer les paquets :**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Lancer le serveur d'application local :**
   ```bash
   python server.py
   ```
   *L'application s'exécute en mode débogage actif sur l'adresse locale : `http://127.0.0.1:5000`.*

***

## 🧪 Suite de Validation et Assurance Qualité (QA)

### 1. Tests d'Architecture et Couverture (`pytest` & `coverage`)

La suite de tests est calibrée pour valider de manière exhaustive la logique unitaire ainsi que les interactions d'intégration complexes, en respectant la contrainte d'avoir deux fois plus de tests unitaires.

Pour exécuter les assertions et générer le rapport d'analyse de couverture, utilisez :

```bash
# Exécution sans pollution de cache système sous Windows
coverage run -m pytest -p no:cacheprovider

# Génération du rapport de synthèse sur la console
coverage report -m

# Génération de l'interface d'audit HTML
coverage html
```

*Le rapport détaillé est alors consultable en ouvrant le fichier `htmlcov/index.html` via votre navigateur.*

### 2. Évaluation des Performances sous Charge (`Locust`)

Pour certifier la robustesse de l'application face aux flux d'utilisateurs simultanés (Seuils : Affichage < 5s, Échange < 2s) avec une charge nominale de **6 utilisateurs concurrents**, exécutez la commande automatisée suivante :

```bash
# Attention : Assurez-vous que le serveur 'python server.py' tourne en parallèle dans un autre terminal
locust -f locustfile.py --headless -u 6 -r 1 --run-time 1m --html rapport_performance.html
```

#### Analyse des indicateurs observés lors des simulations :

* **Taux de pannes (Failures) :** 0.0% stabilisé en continu.
* **Requêtes de consultation (GET `/`, `/points`) :** Temps de réponse moyen mesuré à **130 ms** (Plafond autorisé : 5000 ms).
* **Requêtes transactionnelles (POST `/purchasePlaces`) :** Temps de réponse moyen mesuré à **120 ms** (Plafond autorisé : 2000 ms).

Le fichier `rapport_performance.html` généré à la racine fait foi pour l'audit de livraison.

<br />

### 3. Rapport de Conformité de Style (`Flake8`)

L'analyse statique du code a été réalisée pour garantir l'alignement avec les standards de qualité de la PEP 8.

```bash
# Commande pour exécuter l'analyse en excluant l'environnement virtuel
flake8 . --exclude=venv --format=default --output-file=flake8_report.txt
```

Le fichier d'audit `flake8_report.txt` est joint à la racine du projet pour révision.
