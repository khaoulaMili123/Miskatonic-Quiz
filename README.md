# Miskatonic Quiz - Générateur de Quiz

Ce projet est un outil numérique destiné aux enseignants de la prestigieuse Miskatonic University. Il permet de gérer une banque de questions et de générer des quiz personnalisés de manière simple et efficace.

L'application est composée d'un serveur API et d'un client web, offrant une architecture moderne et découplée.

## Architecture Technique

Le projet s'articule autour de deux services principaux et de deux bases de données distinctes :

-   **Backend (Serveur API)** : Une API RESTful développée avec **FastAPI** (Python). Elle gère toute la logique métier, l'authentification et les interactions avec les bases de données.
-   **Frontend (Client Web)** : Une application web développée avec **Flask** (Python). Elle sert d'interface utilisateur (IHM) et consomme les données fournies par l'API backend.
-   **Base de Données (Questions)** : **MongoDB** est utilisé pour stocker la collection de questions et les questionnaires générés, offrant flexibilité pour des documents complexes.
-   **Base de Données (Utilisateurs)** : **SQLite** est utilisé pour gérer les utilisateurs, leurs identifiants et leurs mots de passe hachés.

## Fonctionnalités Implémentées

-   ✅ **Gestion des Utilisateurs** : Inscription des enseignants (mots de passe hachés avec bcrypt).
-   ✅ **Gestion des Questions** : Ajout de nouvelles questions à la base de données via une interface dédiée.
-   ✅ **Génération de Quiz** :
    -   Interface de sélection pour filtrer les questions par sujet, type de test et quantité.
    -   Génération d'un "brouillon" de quiz basé sur les critères.
-   ✅ **Curation de Quiz** : Interface permettant de visualiser les questions sélectionnées, de supprimer celles qui ne conviennent pas et de nommer le quiz.
-   ✅ **Sauvegarde et Visualisation** :
    -   Enregistrement du quiz finalisé dans la base de données.
    -   Liste de tous les quiz enregistrés.
    -   Visualisation détaillée et page prête à l'impression pour chaque quiz.

---

## Installation et Lancement

Suivez ces étapes pour lancer l'application en environnement de développement.

### 1. Prérequis

-   Python 3.10+
-   Docker et Docker Compose

### 2. Installation

```bash
# 1. Clonez le dépôt
git clone <URL_DU_DEPOT>
cd Miskatonic-Quiz

# 2. Créez et activez un environnement virtuel (recommandé)
python -m venv mvenv
source mvenv/bin/activate
# Sur Windows : .\mvenv\Scripts\activate

# 3. Installez les dépendances
pip install -r requirements.txt
```

### 3. Lancement de l'Application

L'application nécessite 3 terminaux distincts pour fonctionner : un pour la base de données, un pour le backend et un pour le frontend.

**Terminal 1 : Lancer la base de données**

Utilisez Docker Compose pour démarrer le conteneur MongoDB.

```bash
# Lance le service MongoDB en arrière-plan
docker-compose up -d
```

**Terminal 2 : Lancer le Backend (API)**

```bash
# Assurez-vous que votre environnement virtuel est activé
# Lancez le serveur FastAPI sur le port 8000
uvicorn app.main:app --reload --port 8000
```

**Terminal 3 : Lancer le Frontend (Client Web)**

```bash
# Assurez-vous que votre environnement virtuel est activé
# Lancez le serveur Flask sur le port 5000
flask --app frontend/app run --port 5000
```

### 4. Accéder à l'application

-   **Application Web** : Ouvrez votre navigateur et allez à l'adresse [http://localhost:5000](http://localhost:5000)
-   **Documentation de l'API** : L'API FastAPI génère automatiquement une documentation interactive. Vous pouvez la consulter à l'adresse [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Peupler la base de données (Optionnel)

Pour ajouter des questions initiales à la base de données MongoDB, vous pouvez utiliser le script `etl.py`.

```bash
# Exécutez ce script une fois que MongoDB est lancé
python etl.py
```
