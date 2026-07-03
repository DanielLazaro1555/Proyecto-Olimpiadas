class DeportistasRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def team_exists(self, team_id):
        self.cursor.execute("SELECT id FROM equipos WHERE id = ?", (team_id,))
        return self.cursor.fetchone() is not None

    def get_athlete_by_document(self, document):
        self.cursor.execute("SELECT id FROM deportistas WHERE documento = ?", (document,))
        return self.cursor.fetchone()

    def create_athlete(self, nombre, apellido, documento):
        self.cursor.execute(
            "INSERT INTO deportistas (nombre, apellido, documento) VALUES (?, ?, ?)",
            (nombre, apellido, documento),
        )
        return self.cursor.lastrowid

    def is_team_membership_registered(self, team_id, athlete_id):
        self.cursor.execute(
            "SELECT id FROM inscripciones WHERE equipo_id = ? AND deportista_id = ?",
            (team_id, athlete_id),
        )
        return self.cursor.fetchone() is not None

    def create_membership(self, team_id, athlete_id):
        self.cursor.execute(
            "INSERT INTO inscripciones (equipo_id, deportista_id) VALUES (?, ?)",
            (team_id, athlete_id),
        )
        self.connection.commit()

    def list_team_athletes(self, team_id):
        self.cursor.execute(
            """
            SELECT d.id, d.nombre, d.apellido, d.documento
            FROM deportistas d
            JOIN inscripciones i ON d.id = i.deportista_id
            WHERE i.equipo_id = ?
            """,
            (team_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]
