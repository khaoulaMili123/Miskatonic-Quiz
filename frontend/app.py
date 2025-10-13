import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "une_clef_secrete_par_defaut")

# --- CONFIGURATION ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")

# Rendre la date disponible dans tous les templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Connexion MongoDB - A SUPPRIMER A TERME
MONGO_URI = os.getenv("MONGO_URI", "mongodb://isen:isen@localhost:27017/?authSource=admin")
client = MongoClient(MONGO_URI)
db = client['quiz_db']
questions_collection = db['questions']
questionnaires_collection = db['questionnaires']

# ---- PAGE LOGIN ----
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        identifiant = request.form.get('identif')
        mdp = request.form.get('password')
        login_data = {"identifiant": identifiant, "mot_de_passe": mdp}

        try:
            api_url = f"{API_BASE_URL}/auth/login"
            response = requests.post(api_url, json=login_data)

            if response.status_code == 200:
                flash("Connexion réussie !", "success")
                return redirect(url_for('choix'))
            else:
                error_message = response.json().get('detail', "Identifiants incorrects.")
                flash(error_message, "danger")
        except requests.exceptions.ConnectionError:
            flash(f"Erreur de connexion à l'API sur {API_BASE_URL}. Le serveur backend est-il démarré ?", "danger")
        
        return redirect(url_for('home'))

    return render_template('index.html')

# ---- PAGE CREER UN COMPTE ----
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nom_utilisateur = request.form.get('username')
        mot_de_passe = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if mot_de_passe != confirm_password:
            flash("Les mots de passe ne correspondent pas", "warning")
            return redirect(url_for('inscription'))

        user_data = {
            "nom_utilisateur": nom_utilisateur,
            "identifiant": nom_utilisateur,
            "mot_de_passe": mot_de_passe,
            "role_id": 1
        }

        try:
            api_url = f"{API_BASE_URL}/auth/register"
            response = requests.post(api_url, json=user_data)

            if response.status_code == 201:
                flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for('home'))
            else:
                error_message = response.json().get('detail', "Une erreur est survenue.")
                flash(error_message, "danger")
        except requests.exceptions.ConnectionError:
            flash(f"Erreur de connexion à l'API sur {API_BASE_URL}. Le serveur backend est-il démarré ?", "danger")
        
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
        # Note: This only handles one question at a time currently.
        subject = request.form.get("subject")
        if subject == "__new__":
            subject = request.form.get("new_subject")

        test_type = request.form.get("use")
        if test_type == "__new__":
            test_type = request.form.get("new_use")

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

        try:
            api_url = f"{API_BASE_URL}/questions"
            response = requests.post(api_url, json=question_data)

            if response.status_code == 201:
                flash("Question ajoutée avec succès !", "success")
            else:
                error_message = response.json().get('detail', "Une erreur API est survenue.")
                flash(f"Erreur lors de l'ajout de la question: {error_message}", "danger")
        except requests.exceptions.ConnectionError:
            flash(f"Erreur de connexion à l'API sur {API_BASE_URL}.", "danger")
        
        return redirect(url_for("add_quest"))

    subjects = questions_collection.distinct("subject")
    test_types = questions_collection.distinct("use")
    return render_template("ajoute_qst.html", subjects=subjects, test_types=test_types)

# ---- PAGE LISTE DES QUIZ ----
@app.route('/liste-quiz')
def liste_quiz():
    try:
        api_url = f"{API_BASE_URL}/quizzes"
        response = requests.get(api_url)
        response.raise_for_status()
        quizzes = response.json()
        return render_template("liste_quiz.html", quizzes=quizzes)
    except requests.exceptions.RequestException as e:
        flash(f"Impossible de charger la liste des quiz: {e}", "danger")
        return redirect(url_for('choix'))

# ---- PAGE VISUALISER UN QUIZ ----
@app.route('/visualiser_quiz/<quiz_id>')
def visualiser_quiz(quiz_id):
    try:
        api_url = f"{API_BASE_URL}/quizzes/{quiz_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        quiz = response.json()
        return render_template("visualiser_quiz.html", quiz=quiz)
    except requests.exceptions.RequestException as e:
        flash(f"Impossible de charger le quiz: {e}", "danger")
        return redirect(url_for('liste_quiz'))

# ---- PAGE ACCEDER AU GENERATEUR ----
@app.route('/acceder', methods=['GET'])
def acceder():
    try:
        subjects_response = requests.get(f"{API_BASE_URL}/questions/subjects")
        uses_response = requests.get(f"{API_BASE_URL}/questions/uses")
        subjects_response.raise_for_status()
        uses_response.raise_for_status()
        subjects = subjects_response.json()
        test_types = uses_response.json()
        if not subjects or not test_types:
            flash("L'API a retourné des listes vides pour les sujets ou les types. La base de données est-elle peuplée ?", "warning")
        return render_template("generer_quiz.html", subjects=subjects, test_types=test_types)
    except requests.exceptions.RequestException as e:
        flash(f"ERREUR CRITIQUE: Impossible de contacter l'API. Détails: {e}", "danger")
        return render_template("generer_quiz.html", subjects=[], test_types=[])

# ---- PAGE DU QUIZ ----
@app.route('/quiz', methods=['POST'])
def quiz():
    selected_subjects = request.form.getlist('subjects')
    selected_types = request.form.getlist('test_types')
    quantity = request.form.get('quantity', 20)
    params = {'quantity': quantity, 'subjects': selected_subjects, 'uses': selected_types}
    try:
        api_url = f"{API_BASE_URL}/questions"
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            flash(f"ERREUR: L'API a répondu avec un code d'erreur {response.status_code}. Réponse: {response.text}", "danger")
            return redirect(url_for('acceder'))
        filtered_questions = response.json()
        if not filtered_questions:
            flash("INFO: Aucun quiz ne correspond à ces filtres. Essayez d'être moins spécifique.", "warning")
            return redirect(url_for('acceder'))
        return render_template("quiz.html", questions=filtered_questions, title="Affiner le Quiz")
    except requests.exceptions.RequestException as e:
        flash(f"ERREUR CRITIQUE: Impossible de contacter l'API. Détails: {e}", "danger")
        return redirect(url_for('acceder'))

# ---- LOGIQUE DE SAUVEGARDE DU QUIZ ----
@app.route('/save_quiz', methods=['POST'])
def save_quiz():
    try:
        title = request.form.get('quiz_title')
        question_ids = request.form.getlist('selected_questions')

        if not title or not question_ids:
            flash("Le titre et au moins une question sont requis pour enregistrer un quiz.", "warning")
            return redirect(url_for('acceder'))

        quiz_data = {
            "title": title,
            "question_ids": question_ids
        }

        api_url = f"{API_BASE_URL}/quizzes/"
        response = requests.post(api_url, json=quiz_data)

        if response.status_code == 201: # Created
            flash("Quiz enregistré avec succès !", "success")
            return redirect(url_for('liste_quiz'))
        else:
            error_message = response.json().get('detail', "Erreur lors de la sauvegarde du quiz.")
            flash(f"Erreur: {error_message}", "danger")
            return redirect(url_for('acceder'))

    except requests.exceptions.RequestException as e:
        flash(f"ERREUR CRITIQUE: Impossible de contacter l'API pour la sauvegarde. Détails: {e}", "danger")
        return redirect(url_for('acceder'))

# ---- LOGIQUE DE SOUMISSION ET CORRECTION DU QUIZ ----
@app.route('/submit_quiz/<quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    try:
        # 1. Récupérer le quiz complet avec les bonnes réponses
        api_url = f"{API_BASE_URL}/quizzes/{quiz_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        quiz = response.json()

        # 2. Récupérer les réponses de l'étudiant depuis le formulaire
        student_answers = request.form

        # 3. Calculer le score
        score = 0
        total = len(quiz['questions'])
        for i, question in enumerate(quiz['questions']):
            submitted_answer = student_answers.get(f'question_{i}')
            correct_answer = question.get('correct')
            if submitted_answer and submitted_answer in correct_answer:
                score += 1

        # 4. Afficher la page de résultats
        return render_template("resultats.html", 
                                 score=score, 
                                 total=total, 
                                 quiz_title=quiz['title'])

    except requests.exceptions.RequestException as e:
        flash(f"Erreur lors de la soumission du quiz: {e}", "danger")
        return redirect(url_for('home'))

# ---- PAGE POUR PASSER UN QUIZ (VUE ETUDIANT) ----
@app.route('/passer_quiz/<quiz_id>')
def passer_quiz(quiz_id):
    try:
        api_url = f"{API_BASE_URL}/quizzes/{quiz_id}"
        response = requests.get(api_url)
        response.raise_for_status()
        quiz = response.json()
        return render_template("passer_quiz.html", quiz=quiz)
    except requests.exceptions.RequestException as e:
        flash(f"Impossible de charger le quiz: {e}", "danger")
        return redirect(url_for('home'))

# ---- LOGIQUE DE SUPPRESSION DU QUIZ ----
@app.route('/delete_quiz/<quiz_id>', methods=['POST'])
def delete_quiz_route(quiz_id):
    try:
        api_url = f"{API_BASE_URL}/quizzes/{quiz_id}"
        response = requests.delete(api_url)

        if response.status_code == 200:
            flash("Quiz supprimé avec succès.", "success")
        else:
            error_message = response.json().get('detail', "Erreur lors de la suppression du quiz.")
            flash(f"Erreur: {error_message}", "danger")
            
    except requests.exceptions.RequestException as e:
        flash(f"ERREUR CRITIQUE: Impossible de contacter l'API pour la suppression. Détails: {e}", "danger")

    return redirect(url_for('liste_quiz'))

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)