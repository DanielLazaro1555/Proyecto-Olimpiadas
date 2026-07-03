class PartidosRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def get_match(self, match_id):
        self.cursor.execute(
            """
            SELECT id, deporte, resultado_local, resultado_visitante
            FROM partidos
            WHERE id = ?
            """,
            (match_id,),
        )
        return self.cursor.fetchone()

    def save_match_result(self, match_id, local_goals, visitor_goals):
        self.cursor.execute(
            """
            UPDATE partidos
            SET resultado_local = ?, resultado_visitante = ?
            WHERE id = ?
            """,
            (local_goals, visitor_goals, match_id),
        )
        self.connection.commit()

    def list_teams_by_sport(self, sport):
        self.cursor.execute(
            "SELECT id, nombre_equipo FROM equipos WHERE deporte = ? COLLATE NOCASE",
            (sport,),
        )
        return self.cursor.fetchall()

    def list_finished_home_matches(self, sport, team_id):
        self.cursor.execute(
            """
            SELECT resultado_local, resultado_visitante
            FROM partidos
            WHERE deporte = ?
              AND equipo_local_id = ?
              AND resultado_local IS NOT NULL
            """,
            (sport, team_id),
        )
        return self.cursor.fetchall()

    def list_finished_away_matches(self, sport, team_id):
        self.cursor.execute(
            """
            SELECT resultado_local, resultado_visitante
            FROM partidos
            WHERE deporte = ?
              AND equipo_visitante_id = ?
              AND resultado_visitante IS NOT NULL
            """,
            (sport, team_id),
        )
        return self.cursor.fetchall()
