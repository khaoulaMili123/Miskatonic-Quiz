from flask import Flask, request, render_template_string, redirect, url_for, flash
import sqlite3
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "secret_key_for_flash_messages"

# Chemin de la base SQLite
sqlite_path = "./data/users.db.sqlite"

# Crée le dossier si nécessaire
os.makedirs("./data", exist_ok=True)

# Création de la table si elle n'existe pas
def init_db():
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT NOT NULL,
            identifiant TEXT NOT NULL UNIQUE,
            mot_de_passe BLOB NOT NULL,
            role_id INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Fonction pour ajouter un utilisateur
def add_user(nom_utilisateur, identifiant, mot_de_passe, role_id):
    hashed_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO utilisateurs (nom_utilisateur, identifiant, mot_de_passe, role_id) VALUES (?, ?, ?, ?)",
        (nom_utilisateur, identifiant, hashed_password, role_id)
    )
    conn.commit()
    conn.close()

# Page web pour ajouter un utilisateur
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nom = request.form.get("nom")
        identifiant = request.form.get("identifiant")
        mdp = request.form.get("mot_de_passe")
        role = int(request.form.get("role_id"))
        try:
            add_user(nom, identifiant, mdp, role)
            flash(f"Utilisateur {nom} ajouté avec succès.", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash("L'identifiant existe déjà.", "danger")

    # Formulaire simple HTML
    html = """
    <!doctype html>
    <title>Ajouter un utilisateur</title>
    <h1>Ajouter un utilisateur</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
        {% for category, message in messages %}
          <li style="color: {% if category=='success' %}green{% else %}red{% endif %};">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method="post">
      Nom complet: <input type="text" name="nom" required><br>
      Identifiant: <input type="text" name="identifiant" required><br>
      Mot de passe: <input type="password" name="mot_de_passe" required><br>
      Role ID: <select name="role_id">
        <option value="1">Enseignant</option>
        <option value="2">Etudiant</option>
        <option value="3">Administrateur</option>
      </select><br>
      <input type="submit" value="Ajouter">
    </form>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)