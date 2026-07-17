from core.errors import DomainError


class PartidosService:
    def __init__(self, repository):
        self.repository = repository

    def register_result(self, match_id, local_goals, visitor_goals,
                         goleadores_local=None, goleadores_visitante=None):
        self._validate_result_payload(match_id, local_goals, visitor_goals)

        match = self.repository.get_match_with_teams(match_id)
        if not match:
            raise DomainError("Partido no encontrado", 404)

        if match["resultado_local"] is not None or match["resultado_visitante"] is not None:
            raise DomainError(
                "Este partido ya tiene un resultado registrado. No se puede sobrescribir.",
                409,
            )

        scorer_rows = self._validate_scorers(
            match, local_goals, visitor_goals, goleadores_local, goleadores_visitante
        )

        self.repository.save_match_result(match_id, local_goals, visitor_goals)
        if scorer_rows:
            self.repository.save_goal_scorers(match_id, scorer_rows)

        return {"mensaje": "Resultado registrado exitosamente", "id_partido": match_id}

    def get_top_scorers(self, sport, limit=10):
        return self.repository.get_top_scorers(sport, limit)

    def get_statistics(self, sport):
        counts = self.repository.get_match_counts(sport)
        jugados = counts["jugados"] or 0
        total_goles = counts["total_goles"] or 0
        promedio = round(total_goles / jugados, 2) if jugados else 0

        standings = self.build_standings(sport)
        equipo_mas_goleador = standings[0]["equipo_nombre"] if standings else None

        return {
            "deporte": sport,
            "partidos_totales": counts["total"] or 0,
            "partidos_jugados": jugados,
            "partidos_pendientes": counts["pendientes"] or 0,
            "total_goles": total_goles,
            "promedio_goles_por_partido": promedio,
            "equipo_lider": equipo_mas_goleador,
        }

    def _validate_scorers(self, match, local_goals, visitor_goals,
                           goleadores_local, goleadores_visitante):
        if not goleadores_local and not goleadores_visitante:
            return []

        rows = []
        rows += self._validate_team_scorers(
            goleadores_local or [], match["equipo_local_id"], local_goals, "local"
        )
        rows += self._validate_team_scorers(
            goleadores_visitante or [], match["equipo_visitante_id"], visitor_goals, "visitante"
        )
        return rows

    def _validate_team_scorers(self, scorers, team_id, expected_goals, lado):
        rows = []
        suma = 0
        for entry in scorers:
            deportista_id = entry.get("deportista_id")
            goles = entry.get("goles")

            if not isinstance(deportista_id, int) or not isinstance(goles, int):
                raise DomainError(f"Goleador inválido en el equipo {lado}", 400)
            if goles <= 0:
                raise DomainError(f"Los goles del goleador deben ser mayores a 0 ({lado})", 400)
            if not self.repository.is_athlete_in_team(deportista_id, team_id):
                raise DomainError(
                    f"El deportista {deportista_id} no pertenece al equipo {lado}", 400
                )

            suma += goles
            rows.append({"deportista_id": deportista_id, "goles": goles})

        if scorers and suma != expected_goals:
            raise DomainError(
                f"La suma de goles de goleadores ({suma}) no coincide con el resultado {lado} ({expected_goals})",
                400,
            )
        return rows

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
