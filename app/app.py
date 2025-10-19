import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
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

# ---- Clase User para Flask-Login (sin ORM) ----
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

# Inicializar DB al cargar la app
init_db()

# Puerto dinámico (nube) o 5000 local
PORT = int(os.getenv("PORT", "5000"))

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("encuesta"))
    return redirect(url_for("login"))

# (Rutas reales se agregan en commits siguientes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=os.getenv("FLASK_ENV") == "development")
