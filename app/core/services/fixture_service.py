from core.errors import DomainError


class FixtureService:
    def __init__(self, repository):
        self.repository = repository

    def generate_schedule(self, sport):
        teams = self.repository.list_teams_by_sport(sport)
        if len(teams) < 2:
            raise DomainError(
                f"Se necesitan al menos 2 equipos para generar el calendario. Actualmente hay {len(teams)}.",
                400,
            )

        if self.repository.sport_has_schedule(sport):
            raise DomainError(
                "Ya existe un calendario para este deporte. Elimina los partidos existentes si deseas generarlo de nuevo.",
                409,
            )

        matches = self.repository.create_schedule(sport, teams)
        return {
            "mensaje": f"Calendario generado exitosamente para {sport}",
            "deporte": sport,
            "total_partidos": len(matches),
            "partidos": matches,
        }

    def get_schedule(self, sport):
        return self.repository.list_schedule(sport)

    def delete_schedule(self, sport):
        deleted = self.repository.delete_schedule(sport)
        return {"mensaje": f"Se eliminaron {deleted} partidos del deporte {sport}"}
