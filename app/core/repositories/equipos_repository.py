class EquiposRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def team_exists_by_region_and_sport(self, region, sport):
        self.cursor.execute(
            "SELECT id FROM equipos WHERE region = ? AND deporte = ?",
            (region, sport),
        )
        return self.cursor.fetchone() is not None

    def create_team(self, region, sport, team_name):
        self.cursor.execute(
            "INSERT INTO equipos (region, deporte, nombre_equipo) VALUES (?, ?, ?)",
            (region, sport, team_name),
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def list_teams(self):
        self.cursor.execute("SELECT id, region, deporte, nombre_equipo FROM equipos")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_team(self, team_id):
        self.cursor.execute("SELECT id FROM equipos WHERE id = ?", (team_id,))
        return self.cursor.fetchone()

    def team_has_matches(self, team_id):
        self.cursor.execute(
            "SELECT id FROM partidos WHERE equipo_local_id = ? OR equipo_visitante_id = ?",
            (team_id, team_id),
        )
        return self.cursor.fetchone() is not None

    def delete_team(self, team_id):
        self.cursor.execute("DELETE FROM equipos WHERE id = ?", (team_id,))
        self.connection.commit()
