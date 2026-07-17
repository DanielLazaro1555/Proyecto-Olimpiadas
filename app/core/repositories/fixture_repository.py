import random
from datetime import datetime, timedelta


class FixtureRepository:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def list_teams_by_sport(self, sport):
        self.cursor.execute(
            "SELECT id, nombre_equipo FROM equipos WHERE deporte = ? COLLATE NOCASE",
            (sport,),
        )
        return self.cursor.fetchall()

    def sport_has_schedule(self, sport):
        self.cursor.execute(
            "SELECT id FROM partidos WHERE deporte = ? COLLATE NOCASE LIMIT 1",
            (sport,),
        )
        return self.cursor.fetchone() is not None

    def create_schedule(self, sport, teams):
        matchups = []
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                matchups.append((teams[i]["id"], teams[j]["id"]))

        random.shuffle(matchups)

        base_date = datetime.now() + timedelta(days=1)
        base_date = base_date.replace(hour=15, minute=0, second=0, microsecond=0)
        saved_matches = []

        for idx, (local_id, visitor_id) in enumerate(matchups):
            match_date = base_date + timedelta(days=idx * 2)
            self.cursor.execute(
                """
                INSERT INTO partidos (deporte, equipo_local_id, equipo_visitante_id, fecha, hora)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    sport,
                    local_id,
                    visitor_id,
                    match_date.strftime("%Y-%m-%d"),
                    match_date.strftime("%H:%M"),
                ),
            )
            saved_matches.append(
                {
                    "id": self.cursor.lastrowid,
                    "local": next(team["nombre_equipo"] for team in teams if team["id"] == local_id),
                    "visitante": next(
                        team["nombre_equipo"] for team in teams if team["id"] == visitor_id
                    ),
                    "fecha": match_date.strftime("%Y-%m-%d"),
                    "hora": match_date.strftime("%H:%M"),
                }
            )

        self.connection.commit()
        return saved_matches

    def list_schedule(self, sport):
        self.cursor.execute(
            """
            SELECT p.id, p.fecha, p.hora,
                   p.equipo_local_id, p.equipo_visitante_id,
                   eq_local.nombre_equipo as local,
                   eq_visit.nombre_equipo as visitante,
                   p.resultado_local, p.resultado_visitante
            FROM partidos p
            JOIN equipos eq_local ON p.equipo_local_id = eq_local.id
            JOIN equipos eq_visit ON p.equipo_visitante_id = eq_visit.id
            WHERE p.deporte = ? COLLATE NOCASE
            ORDER BY p.fecha, p.hora
            """,
            (sport,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_schedule(self, sport):
        self.cursor.execute("DELETE FROM partidos WHERE deporte = ?", (sport,))
        self.connection.commit()
        return self.cursor.rowcount
