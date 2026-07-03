import re

import bcrypt

from core.errors import DomainError
from core.security import build_token


class AuthService:
    def __init__(self, repository):
        self.repository = repository

    def login(self, username, password):
        if not username or not password:
            raise DomainError("Usuario y contraseña requeridos", 400)

        user = self.repository.get_user_by_username(username)
        if not user or not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        ):
            raise DomainError("Credenciales inválidas", 401)

        token = build_token(
            {
                "user_id": user["id"],
                "username": user["username"],
                "rol": user["rol"],
            }
        )

        return {"token": token, "rol": user["rol"], "username": user["username"]}

    def register_user(self, current_user, username, password, role):
        if current_user["rol"] != "admin":
            raise DomainError("Solo los administradores pueden registrar usuarios", 403)
        if not username or not password:
            raise DomainError("Usuario y contraseña requeridos", 400)
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", username):
            raise DomainError(
                "Usuario: 3-30 caracteres, solo letras, números y guión bajo",
                400,
            )
        if len(password) < 6:
            raise DomainError("La contraseña debe tener al menos 6 caracteres", 400)
        if role not in ("admin", "operador", "visualizador"):
            raise DomainError("Rol inválido", 400)

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        try:
            self.repository.create_user(username, password_hash, role)
        except Exception as error:
            if self.repository.is_duplicate_username_error(error):
                raise DomainError("El nombre de usuario ya existe", 409) from error
            raise

        return {"mensaje": f"Usuario '{username}' registrado exitosamente"}

    def list_users(self, current_user):
        if current_user["rol"] != "admin":
            raise DomainError("Permisos insuficientes", 403)
        return self.repository.list_users()

    def delete_user(self, current_user, user_id):
        if current_user["rol"] != "admin":
            raise DomainError("Permisos insuficientes", 403)
        if current_user["user_id"] == user_id:
            raise DomainError("No puedes eliminar tu propia cuenta", 409)
        if not self.repository.get_user_by_id(user_id):
            raise DomainError("Usuario no encontrado", 404)

        self.repository.delete_user(user_id)
        return {"mensaje": "Usuario eliminado correctamente"}
