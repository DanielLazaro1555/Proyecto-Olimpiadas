# reportes.py

import database as db
from core.repositories.partidos_repository import PartidosRepository
from core.services.partidos_service import PartidosService
from flask import Blueprint, jsonify, request

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@reportes_bp.route("/tabla/<string:deporte>", methods=["GET"])
def reporte_tabla(deporte):
    """Tabla de posiciones (alias de /partidos/tabla, expuesto como reporte)."""
    with db.get_db() as conn:
        service = PartidosService(PartidosRepository(conn))
        tabla = service.build_standings(deporte)
        return jsonify(tabla), 200


@reportes_bp.route("/goleadores/<string:deporte>", methods=["GET"])
def reporte_goleadores(deporte):
    """Devuelve el ranking de goleadores de un deporte."""
    limite = request.args.get("limite", default=10, type=int)
    limite = max(1, min(limite, 50))

    with db.get_db() as conn:
        service = PartidosService(PartidosRepository(conn))
        goleadores = service.get_top_scorers(deporte, limite)
        return jsonify(goleadores), 200


@reportes_bp.route("/estadisticas/<string:deporte>", methods=["GET"])
def reporte_estadisticas(deporte):
    """Estadísticas generales de un deporte: partidos jugados/pendientes, goles, promedio."""
    with db.get_db() as conn:
        service = PartidosService(PartidosRepository(conn))
        estadisticas = service.get_statistics(deporte)
        return jsonify(estadisticas), 200
