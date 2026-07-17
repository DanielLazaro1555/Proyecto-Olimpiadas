# notification_repository.py

class NotificationRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_notification(self, tipo, canal, destinatario, asunto, mensaje, estado):
        query = """
            INSERT INTO notificaciones (tipo, canal, destinatario, asunto, mensaje, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(
            query,
            (tipo, canal, destinatario, asunto, mensaje, estado)
        )
        self.conn.commit()

    def list_notifications(self):
        query = """
            SELECT id, fecha_hora, tipo, canal, destinatario, asunto, mensaje, estado
            FROM notificaciones
            ORDER BY id DESC
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
