import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, flash
from SQLite.add_user import add_users, register_user  # fonctions pour login et création
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "une_clef_secrete"

# Connexion MongoDB
client = MongoClient("mongodb://isen:isen@localhost:27017/")
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

# ---- PAGE CREER UN COMPTE ----
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        nom_utilisateur = request.form.get('username')
        identifiant = request.form.get('username')
        mot_de_passe = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role_id = 2  # étudiant par défaut

        if mot_de_passe != confirm_password:
            flash("Les mots de passe ne correspondent pas")
            return redirect(url_for('inscription'))

        success, message = register_user(nom_utilisateur, identifiant, mot_de_passe, role_id)
        flash(message)
        if success:
            return redirect(url_for('home'))
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

        question = request.form.get("question")
        responses = {
            "A": request.form.get("responseA"),
            "B": request.form.get("responseB"),
            "C": request.form.get("responseC"),
            "D": request.form.get("responseD")
        }
        correct = request.form.get("correct")
        remark = request.form.get("remark")

        questions_collection.insert_one({
            "subject": subject,
            "use": test_type,
            "question": question,
            "responses": responses,
            "correct": correct,
            "remark": remark
        })

        flash("Question ajoutée avec succès !")
        return redirect(url_for("add_quest"))

    subjects = questions_collection.distinct("subject")
    test_types = questions_collection.distinct("use")
    return render_template("ajoute_qst.html", subjects=subjects, test_types=test_types)

# ---- PAGE ACCEDER AU GENERATEUR ----
@app.route('/acceder', methods=['GET', 'POST'])
def acceder():
    if request.method == 'GET':
        subjects = questions_collection.distinct("subject")
        questions_by_subject = {}
        for subj in subjects:
            questions = list(questions_collection.find({"subject": subj}))
            questions_by_subject[subj] = questions
        return render_template("generer_quiz.html", subjects=subjects, questions_by_subject=questions_by_subject)

    # POST → créer le quiz
    selected_ids = request.form.getlist('selected_questions')
    quiz_title = request.form.get('quiz_title', 'Quiz sans titre')

    if not selected_ids:
        flash("Veuillez sélectionner au moins une question.")
        return redirect(url_for('acceder'))

    selected_questions = []
    for qid in selected_ids:
        q = questions_collection.find_one({"_id": ObjectId(qid)})
        if q:
            selected_questions.append({
                "subject": q['subject'],
                "question": q['question'],
                "all_responses": list(q['responses'].values()),
                "correct_responses": q['correct'].split(",")  # ex: "A,B"
            })

    questionnaires_collection.insert_one({
        "title": quiz_title,
        "questions": selected_questions
    })
    flash(f"Quiz '{quiz_title}' créé avec {len(selected_questions)} questions !")

    return render_template("visualiser_quiz.html", quiz_title=quiz_title, questions=selected_questions)

# ---- PAGE SELECTION DE QUESTIONS (filtres) ----
@app.route('/selection', methods=['POST'])
def selection():
    categories = request.form.getlist('categorie')
    nombre = request.form.get('nombre')

    if not categories or not nombre:
        flash("Veuillez choisir au moins une catégorie et un nombre de questions.")
        return redirect(url_for('acceder'))

    # Ici tu peux filtrer les questions depuis MongoDB et retourner le quiz filtré
    return redirect(url_for('acceder'))

if __name__ == '__main__':
    app.run(debug=True)

