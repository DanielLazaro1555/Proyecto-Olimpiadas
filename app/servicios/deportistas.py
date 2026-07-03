# deportistas.py

import database as db
from auth import roles_required
from core.errors import DomainError
from core.repositories.deportistas_repository import DeportistasRepository
from core.services.deportistas_service import DeportistasService
from flask import Blueprint, jsonify, request

deportistas_bp = Blueprint("deportistas", __name__, url_prefix="/deportistas")


@deportistas_bp.route("/inscribir", methods=["POST"])
@roles_required("admin", "operador")
def inscribir_deportista(current_user):
    """Inscribir un deportista en un equipo."""
    data = request.get_json() or {}
    id_equipo = data.get("id_equipo")
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    documento = data.get("documento")

    with db.get_db() as conn:
        service = DeportistasService(DeportistasRepository(conn))
        try:
            payload = service.register_athlete(id_equipo, nombre, apellido, documento)
            return jsonify(payload), 201
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


@deportistas_bp.route("/equipo/<int:id_equipo>", methods=["GET"])
def listar_deportistas_por_equipo(id_equipo):
    """
    Consulta pública (sin autenticación) de deportistas por equipo.
    """
    with db.get_db() as conn:
        service = DeportistasService(DeportistasRepository(conn))
        deportistas = service.list_team_athletes(id_equipo)
    return jsonify(deportistas), 200
