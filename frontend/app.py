import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, flash
from SQLite.add_user import add_users, register_user  # fonctions pour login et création
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime

app = Flask(__name__)
app.secret_key = "une_clef_secrete"

# Rendre la date disponible dans tous les templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Connexion MongoDB
client = MongoClient("mongodb://isen:isen@localhost:27017/?authSource=admin")
db = client['quiz_db']
questions_collection = db['questions']
questionnaires_collection = db['questionnaires']

# ---- PAGE LOGIN ----
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        identifiant = request.form.get('identif')
        mdp = request.form.get('password')
        role_id = 1  # par défaut enseignant

        success, message = add_users(identifiant, identifiant, mdp, role_id)
        flash(message)
        if success:
            return redirect(url_for('choix'))
        return redirect(url_for('home'))

    return render_template('index.html')

import requests

# ---- PAGE CREER UN COMPTE ----
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        # ... (le reste de la logique de formulaire reste identique)
        nom_utilisateur = request.form.get('username')
        mot_de_passe = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if mot_de_passe != confirm_password:
            flash("Les mots de passe ne correspondent pas")
            return redirect(url_for('inscription'))

        # Préparer les données pour l'API
        user_data = {
            "nom_utilisateur": nom_utilisateur,
            "identifiant": nom_utilisateur, # Utilise le nom d'utilisateur comme identifiant
            "mot_de_passe": mot_de_passe,
            "role_id": 1 # enseignant par défaut
        }

        # Appeler l'API backend
        try:
            api_url = "http://localhost:8000/auth/register"
            response = requests.post(api_url, json=user_data)

            if response.status_code == 201: # 201 Created
                flash("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                return redirect(url_for('home'))
            else:
                # Utiliser le message d'erreur de l'API
                error_message = response.json().get('detail', "Une erreur est survenue.")
                flash(error_message)
                return redirect(url_for('inscription'))

        except requests.exceptions.ConnectionError:
            flash("Erreur de connexion à l'API. Le serveur backend est-il démarré ?")
            return redirect(url_for('inscription'))

    return render_template('create.html')

# ---- PAGE CHOIX : Ajouter questions ou accéder au générateur ----
@app.route('/choix')
def choix():
    return render_template('choix.html')

# ---- PAGE AJOUTER QUESTIONS ----
@app.route('/add_quest', methods=['GET', 'POST'])
def add_quest():
    if request.method == 'POST':
        subject = request.form.get("subject")
        if subject == "__new__":
            subject = request.form.get("new_subject")

        test_type = request.form.get("use")
        if test_type == "__new__":
            test_type = request.form.get("new_use")

        # Préparer le payload pour l'API
        question_data = {
            "subject": subject,
            "use": test_type,
            "question": request.form.get("question"),
            "responses": {
                "A": request.form.get("responseA"),
                "B": request.form.get("responseB"),
                "C": request.form.get("responseC"),
                "D": request.form.get("responseD")
            },
            "correct": request.form.get("correct"),
            "remark": request.form.get("remark")
        }

        # Appeler l'API backend
        try:
            api_url = "http://localhost:8000/questions"
            # Note : Plus tard, nous ajouterons les headers d'authentification ici
            response = requests.post(api_url, json=question_data)

            if response.status_code == 201:
                flash("Question ajoutée avec succès !")
            else:
                error_message = response.json().get('detail', "Une erreur API est survenue.")
                flash(f"Erreur lors de l'ajout de la question: {error_message}")
        
        except requests.exceptions.ConnectionError:
            flash("Erreur de connexion à l'API. Le serveur backend est-il démarré ?")
        
        return redirect(url_for("add_quest"))

    # La logique GET pour afficher les filtres reste la même
    subjects = questions_collection.distinct("subject")
    test_types = questions_collection.distinct("use")
    return render_template("ajoute_qst.html", subjects=subjects, test_types=test_types)

# ---- PAGE LISTE DES QUIZ ----
@app.route('/liste-quiz')
def liste_quiz():
    try:
        api_url = "http://localhost:8000/quizzes"
        response = requests.get(api_url)
        response.raise_for_status()
        quizzes = response.json()
        return render_template("liste_quiz.html", quizzes=quizzes)
    except requests.exceptions.RequestException as e:
        return redirect(url_for('choix'))

# ---- PAGE VISUALISER UN QUIZ ----
@app.route('/visualiser_quiz/<quiz_id>')
def visualiser_quiz(quiz_id):
    try:
        api_url = f"http://localhost:8000/quizzes/{quiz_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        quiz = response.json()
        return render_template("visualiser_quiz.html", quiz=quiz)
    except requests.exceptions.RequestException as e:
        flash(f"Impossible de charger le quiz: {e}")
        return redirect(url_for('liste_quiz'))


# ---- PAGE ACCEDER AU GENERATEUR ----
@app.route('/acceder', methods=['GET'])
def acceder():
    try:
        subjects_response = requests.get("http://localhost:8000/questions/subjects")
        uses_response = requests.get("http://localhost:8000/questions/uses")
        subjects_response.raise_for_status()
        uses_response.raise_for_status()
        subjects = subjects_response.json()
        test_types = uses_response.json()
        if not subjects or not test_types:
            flash("L\'API a retourné des listes vides pour les sujets ou les types. La base de données est-elle peuplée ?", "warning")
        return render_template("generer_quiz.html", subjects=subjects, test_types=test_types)
    except requests.exceptions.RequestException as e:
        flash(f"ERREUR CRITIQUE: Impossible de contacter l\'API. Vérifiez que le serveur backend (uvicorn) est bien lancé. Détails: {e}", "error")
        return render_template("generer_quiz.html", subjects=[], test_types=[])

# ---- PAGE DU QUIZ ----
@app.route('/quiz', methods=['POST'])
def quiz():
    selected_subjects = request.form.getlist('subjects')
    selected_types = request.form.getlist('test_types')
    quantity = request.form.get('quantity', 20)
    params = {'quantity': quantity, 'subjects': selected_subjects, 'uses': selected_types}
    try:
        api_url = "http://localhost:8000/questions"
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            flash(f"ERREUR: L\'API a répondu avec un code d\'erreur {response.status_code}. Réponse: {response.text}", "error")
            return redirect(url_for('acceder'))
        filtered_questions = response.json()
        if not filtered_questions:
            flash("INFO: Aucun quiz ne correspond à ces filtres. Essayez d\'être moins spécifique.", "warning")
            return redirect(url_for('acceder'))
        return render_template("quiz.html", questions=filtered_questions, title="Affiner le Quiz")
    except requests.exceptions.RequestException as e:
        flash(f"ERREUR CRITIQUE: Impossible de contacter l\'API. Vérifiez que le serveur backend (uvicorn) est bien lancé. Détails: {e}", "error")
        return redirect(url_for('acceder'))


if __name__ == '__main__':
    app.run(debug=True)

