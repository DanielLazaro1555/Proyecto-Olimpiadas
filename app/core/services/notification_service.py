# notification_service.py
import os
import smtplib
from email.mime.text import MIMEText

from core.errors import DomainError


class NotificationService:
    def __init__(self, repository):
        self.repository = repository

    def notify(self, tipo, destinatario, asunto, mensaje, canal="email"):
        """Envía (o simula) una notificación y deja registro persistente.

        Si SMTP_HOST/SMTP_USER/SMTP_PASS están configurados como variables de
        entorno, intenta un envío real por correo. Si no están configuradas,
        o si el envío falla, la notificación se registra igualmente con un
        estado que refleja lo ocurrido, para que quede trazabilidad completa.
        """
        estado = "simulado"

        if canal == "email" and destinatario and self._smtp_configured():
            try:
                self._send_email(destinatario, asunto, mensaje)
                estado = "enviado"
            except Exception:
                estado = "fallido"

        self.repository.create_notification(
            tipo=tipo,
            canal=canal,
            destinatario=destinatario,
            asunto=asunto,
            mensaje=mensaje,
            estado=estado,
        )
        return estado

    def list_notifications(self, current_user):
        if current_user.get("rol") != "admin":
            raise DomainError("Acceso denegado. Solo administradores pueden ver notificaciones.", 403)
        return self.repository.list_notifications()

    def _smtp_configured(self):
        return bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USER"))

    def _send_email(self, destinatario, asunto, mensaje):
        host = os.environ["SMTP_HOST"]
        port = int(os.environ.get("SMTP_PORT", "587"))
        user = os.environ["SMTP_USER"]
        password = os.environ.get("SMTP_PASS", "")

        msg = MIMEText(mensaje)
        msg["Subject"] = asunto
        msg["From"] = user
        msg["To"] = destinatario

        with smtplib.SMTP(host, port, timeout=5) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [destinatario], msg.as_string())
