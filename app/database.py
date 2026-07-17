# database.py

import os
import sqlite3

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "olimpiadas.db")


def get_db_path():
    return os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)


def get_db():
    """Retorna una conexión a la base de datos."""
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
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
                region TEXT NOT NULL,
                deporte TEXT NOT NULL,
                nombre_equipo TEXT NOT NULL,
                UNIQUE(region, deporte)
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT DEFAULT (datetime('now', 'localtime')),
                username TEXT,
                rol TEXT,
                metodo TEXT NOT NULL,
                ruta TEXT NOT NULL,
                payload TEXT,
                status_code INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partido_id INTEGER NOT NULL,
                deportista_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE,
                FOREIGN KEY (deportista_id) REFERENCES deportistas(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT DEFAULT (datetime('now', 'localtime')),
                tipo TEXT NOT NULL,
                canal TEXT NOT NULL,
                destinatario TEXT,
                asunto TEXT,
                mensaje TEXT,
                estado TEXT NOT NULL DEFAULT 'simulado'
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
        ("admin",    "admin123",    "admin"),
        ("operador", "operador123", "operador"),
        ("viewer",   "viewer123",   "visualizador"),
    ]

    with get_db() as conn:
        for username, password, rol in usuarios_default:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            conn.execute(
                """
                INSERT OR IGNORE INTO usuarios (username, password_hash, rol)
                VALUES (?, ?, ?)
                """,
                (username, password_hash, rol),
            )
        conn.commit()
