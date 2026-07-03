import database as db
from auth import roles_required
from core.errors import DomainError
from core.repositories.fixture_repository import FixtureRepository
from core.services.fixture_service import FixtureService
from flask import Blueprint, jsonify

fixture_bp = Blueprint("fixture", __name__, url_prefix="/fixture")


@fixture_bp.route("/generar/<string:deporte>", methods=["POST"])
@roles_required("admin", "operador")
def generar_fixture(current_user, deporte):
    """Genera el calendario para un deporte."""
    with db.get_db() as conn:
        service = FixtureService(FixtureRepository(conn))
        try:
            payload = service.generate_schedule(deporte)
            return jsonify(payload), 201
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code


@fixture_bp.route("/consultar/<string:deporte>", methods=["GET"])
def consultar_fixture(deporte):
    """
    Consultar el calendario (lista de partidos) de un deporte.
    Público (sin autenticación).
    """
    with db.get_db() as conn:
        service = FixtureService(FixtureRepository(conn))
        partidos = service.get_schedule(deporte)
    return jsonify(partidos), 200


@fixture_bp.route("/eliminar/<string:deporte>", methods=["DELETE"])
@roles_required("admin", "operador")
def eliminar_fixture(current_user, deporte):
    """Eliminar el calendario de un deporte para regenerarlo."""
    with db.get_db() as conn:
        service = FixtureService(FixtureRepository(conn))
        payload = service.delete_schedule(deporte)
    return jsonify(payload), 200
