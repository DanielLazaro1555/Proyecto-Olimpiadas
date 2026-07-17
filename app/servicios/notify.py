# notify.py
# Helper compartido para disparar notificaciones desde los blueprints de eventos
# (equipos, partidos, usuarios) sin acoplar la lógica de negocio al canal de envío.
import os

from core.repositories.notification_repository import NotificationRepository
from core.services.notification_service import NotificationService


def notificar_evento(conn, tipo, asunto, mensaje):
    """Dispara una notificación best-effort; nunca debe romper el flujo principal."""
    destinatario = os.environ.get("NOTIFY_EMAIL", "admin@olimpiadasperu.local")
    try:
        service = NotificationService(NotificationRepository(conn))
        service.notify(tipo, destinatario, asunto, mensaje)
    except Exception:
        pass
