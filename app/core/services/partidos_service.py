from core.errors import DomainError


class PartidosService:
    def __init__(self, repository):
        self.repository = repository

    def register_result(self, match_id, local_goals, visitor_goals):
        self._validate_result_payload(match_id, local_goals, visitor_goals)

        match = self.repository.get_match(match_id)
        if not match:
            raise DomainError("Partido no encontrado", 404)

        if match["resultado_local"] is not None or match["resultado_visitante"] is not None:
            raise DomainError(
                "Este partido ya tiene un resultado registrado. No se puede sobrescribir.",
                409,
            )

        self.repository.save_match_result(match_id, local_goals, visitor_goals)
        return {"mensaje": "Resultado registrado exitosamente", "id_partido": match_id}

    def build_standings(self, sport):
        teams = self.repository.list_teams_by_sport(sport)
        table = []

        for team in teams:
            stats = self._build_team_stats(sport, team)
            table.append(stats)

        table.sort(key=lambda row: (row["puntos"], row["dg"], row["gf"]), reverse=True)
        return table

    def _build_team_stats(self, sport, team):
        home_matches = self.repository.list_finished_home_matches(sport, team["id"])
        away_matches = self.repository.list_finished_away_matches(sport, team["id"])

        points = 0
        goals_for = 0
        goals_against = 0
        played = 0
        won = 0
        drawn = 0
        lost = 0

        for match in home_matches:
            gf = match["resultado_local"]
            gc = match["resultado_visitante"]
            goals_for += gf
            goals_against += gc
            played += 1
            if gf > gc:
                points += 3
                won += 1
            elif gf == gc:
                points += 1
                drawn += 1
            else:
                lost += 1

        for match in away_matches:
            gf = match["resultado_visitante"]
            gc = match["resultado_local"]
            goals_for += gf
            goals_against += gc
            played += 1
            if gf > gc:
                points += 3
                won += 1
            elif gf == gc:
                points += 1
                drawn += 1
            else:
                lost += 1

        return {
            "equipo_id": team["id"],
            "equipo_nombre": team["nombre_equipo"],
            "pj": played,
            "pg": won,
            "pe": drawn,
            "pp": lost,
            "gf": goals_for,
            "gc": goals_against,
            "dg": goals_for - goals_against,
            "puntos": points,
        }

    def _validate_result_payload(self, match_id, local_goals, visitor_goals):
        if match_id is None or local_goals is None or visitor_goals is None:
            raise DomainError(
                "Faltan campos: id_partido, goles_local, goles_visitante",
                400,
            )

        if not isinstance(local_goals, int) or not isinstance(visitor_goals, int):
            raise DomainError("Los goles deben ser números enteros", 400)

        if local_goals < 0 or visitor_goals < 0:
            raise DomainError("Los goles no pueden ser negativos", 400)

        if local_goals > 99 or visitor_goals > 99:
            raise DomainError("Valor de goles fuera de rango (máx. 99)", 400)
