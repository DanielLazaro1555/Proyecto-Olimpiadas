# partidos.py

import database as db
from auth import roles_required
from core.errors import DomainError
from core.repositories.partidos_repository import PartidosRepository
from core.services.partidos_service import PartidosService
from flask import Blueprint, jsonify, request

partidos_bp = Blueprint("partidos", __name__, url_prefix="/partidos")


@partidos_bp.route("/resultado", methods=["POST"])
@roles_required("admin", "operador")
def registrar_resultado(current_user):
    """Registrar el resultado de un partido."""
    data = request.get_json()
    id_partido = data.get("id_partido") if data else None
    goles_local = data.get("goles_local") if data else None
    goles_visitante = data.get("goles_visitante") if data else None

    with db.get_db() as conn:
        service = PartidosService(PartidosRepository(conn))
        try:
            payload = service.register_result(id_partido, goles_local, goles_visitante)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


@partidos_bp.route("/tabla/<string:deporte>", methods=["GET"])
def obtener_tabla_posiciones(deporte):
    """Devuelve la tabla de posiciones ordenada por puntos, diferencia de goles, etc."""
    with db.get_db() as conn:
        service = PartidosService(PartidosRepository(conn))
        tabla = service.build_standings(deporte)
        return jsonify(tabla), 200
