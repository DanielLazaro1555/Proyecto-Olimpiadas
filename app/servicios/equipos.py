# equipos.py

import database as db
from auth import roles_required
from core.errors import DomainError
from core.repositories.equipos_repository import EquiposRepository
from core.services.equipos_service import EquiposService
from flask import Blueprint, jsonify, request

equipos_bp = Blueprint("equipos", __name__, url_prefix="/equipos")


@equipos_bp.route("/", methods=["POST"])
@roles_required("admin", "operador")
def registrar_equipo(current_user):
    """Registrar un nuevo equipo."""
    data = request.get_json() or {}
    region = data.get("region")
    deporte = data.get("deporte")
    nombre_equipo = data.get("nombre_equipo")

    with db.get_db() as conn:
        service = EquiposService(EquiposRepository(conn))
        try:
            payload = service.create_team(region, deporte, nombre_equipo)
            return jsonify(payload), 201
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


@equipos_bp.route("/", methods=["GET"])
def consultar_equipos():
    """
    Consulta pública (sin autenticación) de todos los equipos.
    """
    with db.get_db() as conn:
        service = EquiposService(EquiposRepository(conn))
        equipos = service.list_teams()
    return jsonify(equipos), 200


@equipos_bp.route("/<int:equipo_id>", methods=["DELETE"])
@roles_required("admin", "operador")
def eliminar_equipo(current_user, equipo_id):
    """Elimina un equipo por ID."""
    with db.get_db() as conn:
        service = EquiposService(EquiposRepository(conn))
        try:
            payload = service.delete_team(equipo_id)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code
