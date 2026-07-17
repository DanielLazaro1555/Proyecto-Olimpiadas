# notificaciones.py

import database as db
from auth import roles_required
from core.errors import DomainError
from core.repositories.notification_repository import NotificationRepository
from core.services.notification_service import NotificationService
from flask import Blueprint, jsonify

notificaciones_bp = Blueprint("notificaciones", __name__, url_prefix="/notificaciones")


@notificaciones_bp.route("/", methods=["GET"])
@roles_required("admin")
def listar_notificaciones(current_user):
    """Lista el historial de notificaciones enviadas/simuladas. Solo admins."""
    with db.get_db() as conn:
        service = NotificationService(NotificationRepository(conn))
        try:
            payload = service.list_notifications(current_user)
            return jsonify(payload), 200
        except DomainError as error:
            return jsonify({"error": error.message}), error.status_code
