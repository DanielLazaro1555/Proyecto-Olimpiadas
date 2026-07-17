# audit_service.py
from core.errors import DomainError

class AuditService:
    def __init__(self, repository):
        self.repository = repository

    def create_audit(self, username, rol, metodo, ruta, payload, status_code):
        """Registra un evento de auditoría."""
        # Limitar longitud del payload para evitar sobrecarga en BD
        if payload and len(payload) > 1000:
            payload = payload[:997] + "..."

        self.repository.create_audit(
            username=username,
            rol=rol,
            metodo=metodo,
            ruta=ruta,
            payload=payload,
            status_code=status_code
        )

    def list_audits(self, current_user):
        """Devuelve el historial de auditoría (solo para administradores)."""
        if current_user.get("rol") != "admin":
            raise DomainError("Acceso denegado. Solo administradores pueden ver auditoría.", 403)
        return self.repository.list_audits()
