# auth.py

import datetime
import os
from functools import wraps

import bcrypt
import jwt
from flask import Blueprint, jsonify, request

import database as db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

SECRET_KEY = os.environ.get("SECRET_KEY", "cambia_esta_clave_en_produccion")


# ─── Decoradores ──────────────────────────────────────────────────────────────

def token_required(f):
    """Protege una ruta verificando el JWT en el header Authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
        if not token:
            return jsonify({"error": "Token requerido"}), 401
        try:
            current_user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Sesión expirada, inicia sesión nuevamente"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def role_required(allowed_roles):
    """Verifica que el usuario tenga uno de los roles permitidos."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
            if not token:
                return jsonify({"error": "Token requerido"}), 401
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                if data["rol"] not in allowed_roles:
                    return jsonify({"error": "Permisos insuficientes"}), 403
            except Exception:
                return jsonify({"error": "Token inválido"}), 401
            return f(*args, **kwargs)
        return decorated
    return decorator


# ─── Rutas públicas ───────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    with db.get_db() as conn:
        user = conn.execute(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        ).fetchone()

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = jwt.encode(
        {
            "user_id": user["id"],
            "username": user["username"],
            "rol": user["rol"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "rol": user["rol"], "username": user["username"]}), 200


# ─── Rutas protegidas (solo admin) ────────────────────────────────────────────

@auth_bp.route("/registro", methods=["POST"])
@token_required
def registrar(current_user):
    """Crea un nuevo usuario. Solo admins pueden registrar cuentas."""
    if current_user["rol"] != "admin":
        return jsonify({"error": "Solo los administradores pueden registrar usuarios"}), 403

    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    rol = data.get("rol", "visualizador")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    if rol not in ("admin", "visualizador"):
        return jsonify({"error": "Rol inválido"}), 400

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        with db.get_db() as conn:
            conn.execute(
                "INSERT INTO usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                (username, password_hash, rol),
            )
            conn.commit()
        return jsonify({"mensaje": f"Usuario '{username}' registrado exitosamente"}), 201
    except Exception:
        return jsonify({"error": "El nombre de usuario ya existe"}), 409


@auth_bp.route("/usuarios", methods=["GET"])
@token_required
def listar_usuarios(current_user):
    """Lista todos los usuarios. Solo admins."""
    if current_user["rol"] != "admin":
        return jsonify({"error": "Permisos insuficientes"}), 403
    with db.get_db() as conn:
        usuarios = conn.execute(
            "SELECT id, username, rol FROM usuarios ORDER BY id"
        ).fetchall()
    return jsonify([dict(u) for u in usuarios]), 200


@auth_bp.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
@token_required
def eliminar_usuario(current_user, usuario_id):
    """Elimina un usuario. Solo admins. No puede eliminarse a sí mismo."""
    if current_user["rol"] != "admin":
        return jsonify({"error": "Permisos insuficientes"}), 403
    if current_user["user_id"] == usuario_id:
        return jsonify({"error": "No puedes eliminar tu propia cuenta"}), 409
    with db.get_db() as conn:
        existe = conn.execute(
            "SELECT id FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        if not existe:
            return jsonify({"error": "Usuario no encontrado"}), 404
        conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
    return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
