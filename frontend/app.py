
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, flash
from SQLite.add_user import add_users

app = Flask(__name__)
app.secret_key = "une_clef_secrete"

@app.route('/')
def home():
    return render_template('index.html')  # page contenant ton formulaire login

@app.route('/login', methods=['POST'])
def login():
    identifiant = request.form.get('identif')  # name="identif" dans ton <input>
    mdp = request.form.get('password')        # name="password" dans ton <input>

    # rôle par défaut (ex : 1 = enseignant)
    role_id = 1

    # on passe l'identifiant aussi comme nom_utilisateur
    success, message = add_users(identifiant, identifiant, mdp, role_id)

    flash(message)
    if success:
        # ici tu peux faire ce que tu veux (redirection vers tableau de bord)
        return redirect(url_for('Quiz'))
    else:
        # si mot de passe incorrect ou compte inexistant on revient à l'accueil
        return redirect(url_for('home'))

@app.route('/quiz')
def quiz():
    return "Bienvenue ! "

if __name__ == '__main__':
    app.run(debug=True)
