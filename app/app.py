import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv

from models import (
    init_db, bcrypt,
    crear_usuario, obtener_usuario_por_email, obtener_usuario_por_id,
    verificar_password, guardar_voto, usuario_ya_voto, contar_votos
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, email):
        self.id = str(id)
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    data = obtener_usuario_por_id(int(user_id))
    if data:
        return User(data["id"], data["email"])
    return None

init_db()
PORT = int(os.getenv("PORT", "5000"))

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("encuesta"))
    return redirect(url_for("login"))

# ---------- Registro ----------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        if not email or not password:
            flash("Por favor, completa todos los campos.")
            return redirect(url_for("registro"))
        existente = obtener_usuario_por_email(email)
        if existente:
            flash("Ese correo ya está registrado.")
            return redirect(url_for("registro"))
        user_id = crear_usuario(email, password)
        user = User(user_id, email)
        login_user(user)
        flash("Registro exitoso. ¡Bienvenida/o!")
        return redirect(url_for("encuesta"))
    return render_template("registro.html")

# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        data = obtener_usuario_por_email(email)
        if not data or not verificar_password(password, data["password_hash"]):
            flash("Correo o contraseña incorrectos.")
            return redirect(url_for("login"))
        user = User(data["id"], data["email"])
        login_user(user)
        flash("Has iniciado sesión.")
        return redirect(url_for("encuesta"))
    return render_template("login.html")

# ---------- Logout ----------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.")
    return redirect(url_for("login"))

# (Rutas de encuesta y resultados en commits 6 y 7)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=os.getenv("FLASK_ENV") == "development")
    from flask_login import login_required

# ---------- Encuesta ----------
@app.route("/encuesta", methods=["GET", "POST"])
@login_required
def encuesta():
    opciones = ["Python", "JavaScript", "Java", "C#"]
    if request.method == "POST":
        if usuario_ya_voto(int(current_user.id)):
            flash("Ya votaste antes. Gracias.")
            return redirect(url_for("resultados"))
        opcion = request.form.get("opcion")
        if opcion not in opciones:
            flash("Elige una opción válida.")
            return redirect(url_for("encuesta"))
        guardar_voto(int(current_user.id), opcion)
        flash("¡Voto registrado!")
        return redirect(url_for("resultados"))
    ya_voto = usuario_ya_voto(int(current_user.id))
    return render_template("encuesta.html", opciones=opciones, ya_voto=ya_voto)
@app.route("/resultados")
@login_required
def resultados():
    datos = contar_votos()  # lista de (opcion, conteo)
    # Armar dict para mostrar siempre en el mismo orden
    opciones = ["Python", "JavaScript", "Java", "C#"]
    conteo = {op: 0 for op in opciones}
    for op, c in datos:
        if op in conteo:
            conteo[op] = c
    total = sum(conteo.values())
    return render_template("resultados.html", conteo=conteo, total=total)

