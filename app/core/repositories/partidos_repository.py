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

    def get_match_with_teams(self, match_id):
        self.cursor.execute(
            """
            SELECT id, deporte, equipo_local_id, equipo_visitante_id,
                   resultado_local, resultado_visitante
            FROM partidos
            WHERE id = ?
            """,
            (match_id,),
        )
        return self.cursor.fetchone()

    def is_athlete_in_team(self, athlete_id, team_id):
        self.cursor.execute(
            "SELECT id FROM inscripciones WHERE equipo_id = ? AND deportista_id = ?",
            (team_id, athlete_id),
        )
        return self.cursor.fetchone() is not None

    def save_goal_scorers(self, match_id, scorer_rows):
        self.cursor.executemany(
            "INSERT INTO goles (partido_id, deportista_id, cantidad) VALUES (?, ?, ?)",
            [(match_id, row["deportista_id"], row["goles"]) for row in scorer_rows],
        )
        self.connection.commit()

    def get_top_scorers(self, sport, limit):
        self.cursor.execute(
            """
            SELECT d.id AS deportista_id, d.nombre, d.apellido,
                   eq.nombre_equipo AS equipo_nombre, SUM(g.cantidad) AS goles
            FROM goles g
            JOIN partidos p ON g.partido_id = p.id
            JOIN deportistas d ON g.deportista_id = d.id
            JOIN inscripciones i ON i.deportista_id = d.id
            JOIN equipos eq ON eq.id = i.equipo_id AND eq.deporte = p.deporte COLLATE NOCASE
            WHERE p.deporte = ? COLLATE NOCASE
            GROUP BY d.id
            ORDER BY goles DESC, d.apellido ASC
            LIMIT ?
            """,
            (sport, limit),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_match_counts(self, sport):
        self.cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN resultado_local IS NOT NULL THEN 1 ELSE 0 END) AS jugados,
                SUM(CASE WHEN resultado_local IS NULL THEN 1 ELSE 0 END) AS pendientes,
                SUM(CASE WHEN resultado_local IS NOT NULL
                    THEN resultado_local + resultado_visitante ELSE 0 END) AS total_goles
            FROM partidos
            WHERE deporte = ? COLLATE NOCASE
            """,
            (sport,),
        )
        return dict(self.cursor.fetchone())

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
