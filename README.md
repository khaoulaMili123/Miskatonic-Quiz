
#  Miskatonic Quiz Generator

> **Projet universitaire** – Application web complète pour la création, la génération et la gestion de quiz.  
> Réalisé dans le cadre d’un module de développement full stack à la *Miskatonic University* (projet pédagogique).

---

##  Contexte et objectifs

Le projet **Miskatonic Quiz** a pour but de développer une **application web complète** permettant aux enseignants :

- de **créer leurs propres quiz** en ligne,  
- d’utiliser une **base de questions existante**,  
- et de **faire passer les quiz** à leurs étudiants.  

L’application a été conçue pour répondre à un **besoin pédagogique** :  
faciliter l’évaluation et la révision dans un environnement numérique simple et sécurisé.

---

##  Architecture générale

Le projet est organisé en **deux parties principales** :

| Composant | Description |
|------------|-------------|
| **Backend (API)** | Développé avec **FastAPI**, il gère les utilisateurs, les questions et les quiz. |
| **Frontend (Interface Web)** | Réalisé avec **Flask**, il permet aux enseignants d’interagir avec l’application via des pages HTML. |

Les deux communiquent via des requêtes HTTP (`requests`).

---

##  Technologies principales

| Domaine | Outil / Bibliothèque | Rôle |
|----------|----------------------|------|
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) | Framework Python moderne pour API REST |
| **Frontend Web** | [Flask](https://flask.palletsprojects.com/) | Interface utilisateur et rendu HTML (Jinja2) |
| **BDD NoSQL** | [MongoDB](https://www.mongodb.com/) + [PyMongo](https://pymongo.readthedocs.io/) | Stockage des questions et quiz |
| **BDD SQL** | [SQLite3](https://docs.python.org/3/library/sqlite3.html) | Gestion des utilisateurs et des rôles |
| **Sécurité** | [bcrypt](https://pypi.org/project/bcrypt/) | Hashage sécurisé des mots de passe |
| **Traitement des données** | [pandas](https://pandas.pydata.org/) | Lecture et transformation du CSV (ETL) |
| **Requêtes API** | [requests](https://requests.readthedocs.io/) | Communication entre Flask et FastAPI |
| **Documentation API** | OpenAPI (auto-générée par FastAPI) | Documentation interactive `/docs` |
| **Conteneurisation** | Docker + docker-compose | Déploiement multi-services |

---

##  Structure du projet

```
.
├── app
│   ├── main.py                  # Point d’entrée FastAPI
│   ├── routers/                 # Routes principales (auth, questions, quizzes)
│   ├── models/                  # Modèles de données
│   └── database/                # Connexions MongoDB & SQLite
│
├── frontend
│   ├── app.py                   # Application Flask (interface utilisateur)
│   ├── templates/               # Pages HTML (Jinja2)
│   └── static/                  # CSS, images, JS
│
├── data/
│   ├── questions.csv            # Données fournies
│   └── bdd_connexion.sqlite     # Base SQLite (utilisateurs)
│
├── SQLite/
│   ├── add_user.py              # Gestion utilisateurs (hashage bcrypt)
│   └── bdd_create.py            # Création et initialisation de la base SQLite
│
├── etl.py                       # Script ETL : import CSV → MongoDB
├── docker-compose.yml           # Configuration Docker (API, MongoDB, frontend)
├── README.md                    # Ce fichier 
└── requirements.txt             # Dépendances Python
```

---

##  Bases de données

###  **SQLite** (utilisateurs)

Structure relationnelle classique :
- `utilisateurs` : nom, identifiant, mot de passe (haché bcrypt), rôle  
- `roles` : enseignant, étudiant, administrateur  

> Créée automatiquement via le script `bdd_create.py`.

---

###  **MongoDB** (questions & quiz)

Chaque question suit le **template de document MongoDB** suivant :

```json
{
  "subject": "Réseaux",
  "use": "QCM",
  "question": "Quel protocole est utilisé pour envoyer des e-mails ?",
  "responses": {
    "A": "SMTP",
    "B": "HTTP",
    "C": "FTP",
    "D": "SNMP"
  },
  "correct": "A",
  "remark": "SMTP est le protocole standard d’envoi de mails."
}
```

Chargement automatisé via le script `etl.py` (lecture du CSV fourni).

---

##  Sécurité

- **Hashage des mots de passe :** via la librairie `bcrypt`  
  → les mots de passe ne sont jamais stockés en clair.  
- **Authentification :** API `/auth/register` et `/auth/login` (prévue pour évolution JWT).  
- **Séparation des rôles :** administrateur / enseignant / étudiant.  

---

##  Installation et exécution

###  Prérequis
- Python ≥ 3.10  
- MongoDB ≥ 6.0  
- (Optionnel) Docker / Docker Compose

---

###  Installation manuelle

 **Cloner le projet**
```bash
git clone https://github.com/<ton-utilisateur>/MiskatonicQuiz.git
cd MiskatonicQuiz
```

 **Créer l’environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # (ou venv\Scripts\activate sous Windows)
```

 **Installer les dépendances**
```bash
pip install -r requirements.txt
```

 **Lancer l’API FastAPI**
```bash
cd app
uvicorn main:app --reload --port 8080
```

 API accessible sur : [http://localhost:8080/docs](http://localhost:8080/docs)

 **Lancer le frontend Flask**
```bash
cd ../frontend
python app.py
```

 Interface accessible sur : [http://localhost:5000](http://localhost:5000)

---

###  Lancement via Docker
```bash
docker-compose up --build
```

- API FastAPI → port `8080`  
- Frontend Flask → port `5000`  
- MongoDB → port `27017`

---

##  Chargement des données (ETL)

Le script `etl.py` permet de charger automatiquement les questions fournies (fichier CSV) dans la base MongoDB

```bash
python etl.py
```

 Nettoie les données  
 Crée les collections `questions`, `subjects`, `test_types`, `questionnaires`

---

##  Fonctionnalités principales

 Authentification et création de compte  
 Ajout de questions par les enseignants  
 Génération automatique de quiz  
 Passage et correction de quiz  
 Visualisation et suppression des quiz  
 Interface responsive et moderne (CSS personnalisé + Google Fonts)

---

##  Auteurs

Malgorzata Ryczer-Dumas https://github.com/go2375  
Mathieu Laronce https://github.com/MathieuLaronce  
Khawla MILI https://github.com/khaoulaMili123

---

##  Licence

Projet réalisé à des fins pédagogiques — © Université Miskatonic 2025  

---
