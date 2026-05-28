# database.py

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "olimpiadas.db")


def get_db():
    """Retorna una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Crea las tablas si no existen y siembra usuarios por defecto."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pais TEXT NOT NULL,
                deporte TEXT NOT NULL,
                nombre_equipo TEXT NOT NULL,
                UNIQUE(pais, deporte)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deportistas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                documento TEXT UNIQUE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inscripciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipo_id INTEGER NOT NULL,
                deportista_id INTEGER NOT NULL,
                FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
                FOREIGN KEY (deportista_id) REFERENCES deportistas(id) ON DELETE CASCADE,
                UNIQUE(equipo_id, deportista_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deporte TEXT NOT NULL,
                equipo_local_id INTEGER,
                equipo_visitante_id INTEGER,
                fecha TEXT,
                hora TEXT,
                resultado_local INTEGER,
                resultado_visitante INTEGER,
                FOREIGN KEY (equipo_local_id) REFERENCES equipos(id),
                FOREIGN KEY (equipo_visitante_id) REFERENCES equipos(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'visualizador'
            )
        """)

        conn.commit()

    _seed_usuarios()


def _seed_usuarios():
    """Crea usuarios por defecto si no existen."""
    try:
        import bcrypt
    except ImportError:
        print("⚠ bcrypt no instalado — ejecuta: pip install bcrypt")
        return

    usuarios_default = [
        ("admin", "admin123", "admin"),
        ("viewer", "viewer123", "visualizador"),
    ]

    with get_db() as conn:
        for username, password, rol in usuarios_default:
            existe = conn.execute(
                "SELECT id FROM usuarios WHERE username = ?", (username,)
            ).fetchone()
            if not existe:
                password_hash = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                conn.execute(
                    "INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                    (username, password_hash, rol),
                )
        conn.commit()
