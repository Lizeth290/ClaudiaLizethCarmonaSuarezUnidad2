import os
import time
import psycopg2
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection(retries=10, delay=3):
    last_err = None
    for _ in range(retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = True
            return conn
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise last_err

def init_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS votos (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                opcion TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE (user_id) -- un voto por usuario
            );
        """)
    conn.close()

# ---- Funciones de usuarios ----
def crear_usuario(email: str, password: str):
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO usuarios (email, password_hash) VALUES (%s, %s) RETURNING id;",
                    (email, password_hash))
        row = cur.fetchone()
    conn.close()
    return row[0]

def obtener_usuario_por_email(email: str):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, email, password_hash FROM usuarios WHERE email = %s;", (email,))
        row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "email": row[1], "password_hash": row[2]}
    return None

def obtener_usuario_por_id(user_id: int):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, email, password_hash FROM usuarios WHERE id = %s;", (user_id,))
        row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "email": row[1], "password_hash": row[2]}
    return None

def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.check_password_hash(password_hash, password)

# ---- Funciones de votos ----
def guardar_voto(user_id: int, opcion: str):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO votos (user_id, opcion) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING;",
                    (user_id, opcion))
    conn.close()

def usuario_ya_voto(user_id: int) -> bool:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM votos WHERE user_id = %s;", (user_id,))
        existe = cur.fetchone() is not None
    conn.close()
    return existe

def contar_votos():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT opcion, COUNT(*) FROM votos GROUP BY opcion ORDER BY COUNT(*) DESC;")
        filas = cur.fetchall()
    conn.close()
    return filas
