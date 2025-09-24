import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, flash
from SQLite.add_user import add_users, register_user  # fonctions pour login et création

app = Flask(__name__)
app.secret_key = "une_clef_secrete"

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
            return redirect(url_for('quiz'))
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
        role_id = 2  # rôle étudiant par défaut

        if mot_de_passe != confirm_password:
            flash("Les mots de passe ne correspondent pas")
            return redirect(url_for('inscription'))

        success, message = register_user(nom_utilisateur, identifiant, mot_de_passe, role_id)
        flash(message)
        if success:
            return redirect(url_for('home'))
        return redirect(url_for('inscription'))

    return render_template('create.html')


# ---- PAGE QUIZ / DASHBOARD ----
@app.route('/quiz')
def quiz():
    return "Bienvenue dans le quiz !"


if __name__ == '__main__':
    app.run(debug=True)
