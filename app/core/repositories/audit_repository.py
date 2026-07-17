# audit_repository.py

class AuditRepository:
    def __init__(self, conn):
        self.conn = conn

    def create_audit(self, username, rol, metodo, ruta, payload, status_code):
        """Registra un evento de auditoría en la base de datos."""
        query = """
            INSERT INTO auditorias (username, rol, metodo, ruta, payload, status_code)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.conn.execute(
            query,
            (username, rol, metodo, ruta, payload, status_code)
        )
        self.conn.commit()

    def list_audits(self):
        """Lista todos los registros de auditoría ordenados por fecha y hora descendente."""
        query = """
            SELECT id, fecha_hora, username, rol, metodo, ruta, payload, status_code
            FROM auditorias
            ORDER BY id DESC
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
