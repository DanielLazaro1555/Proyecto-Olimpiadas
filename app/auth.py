# auth.py
# La autenticación HTTP se mantiene aquí como adaptador Flask.
# La lógica de negocio usa bcrypt en core/services/auth_service.py
# y la SECRET_KEY se resuelve desde os.environ en core/security.py.

from functools import wraps

import jwt
from flask import Blueprint, jsonify, request

import database as db
from core.errors import DomainError
from core.repositories.auth_repository import AuthRepository
from core.security import decode_token
from core.services.auth_service import AuthService
from servicios.notify import notificar_evento as _notificar_evento

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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
            current_user = decode_token(token)
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
                data = decode_token(token)
                if data["rol"] not in allowed_roles:
                    return jsonify({"error": "Permisos insuficientes"}), 403
            except Exception:
                return jsonify({"error": "Token inválido"}), 401
            return f(*args, **kwargs)
        return decorated
    return decorator


def roles_required(*allowed_roles):
    """Inyecta el usuario actual y valida roles permitidos en una sola capa."""
    def decorator(f):
        @token_required
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user["rol"] not in allowed_roles:
                return jsonify({"error": "Se requiere rol operador o administrador"}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator


# ─── Rutas públicas ───────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 400

    with db.get_db() as conn:
        service = AuthService(AuthRepository(conn))
        try:
            payload = service.login(username, password)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


# ─── Rutas protegidas (solo admin) ────────────────────────────────────────────

@auth_bp.route("/registro", methods=["POST"])
@token_required
def registrar(current_user):
    """Crea un nuevo usuario. Solo admins pueden registrar cuentas."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    rol = data.get("rol", "visualizador")

    with db.get_db() as conn:
        service = AuthService(AuthRepository(conn))
        try:
            payload = service.register_user(current_user, username, password, rol)
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code

        _notificar_evento(
            conn, "usuario_registrado",
            "Nuevo usuario creado",
            f"Se creó el usuario '{username}' con rol '{rol}'.",
        )
        return jsonify(payload), 201


@auth_bp.route("/usuarios", methods=["GET"])
@token_required
def listar_usuarios(current_user):
    """Lista todos los usuarios. Solo admins."""
    with db.get_db() as conn:
        service = AuthService(AuthRepository(conn))
        try:
            payload = service.list_users(current_user)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


@auth_bp.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
@token_required
def eliminar_usuario(current_user, usuario_id):
    """Elimina un usuario. Solo admins. No puede eliminarse a sí mismo."""
    with db.get_db() as conn:
        service = AuthService(AuthRepository(conn))
        try:
            payload = service.delete_user(current_user, usuario_id)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


@auth_bp.route("/auditoria", methods=["GET"])
@token_required
def listar_auditoria(current_user):
    """Lista el historial de auditoría. Solo admins."""
    with db.get_db() as conn:
        from core.repositories.audit_repository import AuditRepository
        from core.services.audit_service import AuditService
        service = AuditService(AuditRepository(conn))
        try:
            payload = service.list_audits(current_user)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code
