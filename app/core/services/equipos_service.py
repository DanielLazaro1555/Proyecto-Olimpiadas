from core.errors import DomainError


class EquiposService:
    def __init__(self, repository):
        self.repository = repository

    def create_team(self, region, sport, team_name):
        if not all([region, sport, team_name]):
            raise DomainError("Faltan campos requeridos", 400)

        if self.repository.team_exists_by_region_and_sport(region, sport):
            raise DomainError("Ya existe un equipo de esa región en este deporte", 409)

        team_id = self.repository.create_team(region, sport, team_name)
        return {"mensaje": "Equipo registrado exitosamente", "id": team_id}

    def list_teams(self):
        return self.repository.list_teams()

    def delete_team(self, team_id):
        if not self.repository.get_team(team_id):
            raise DomainError("Equipo no encontrado", 404)

        if self.repository.team_has_matches(team_id):
            raise DomainError("No se puede eliminar un equipo con partidos asignados", 409)

        self.repository.delete_team(team_id)
        return {"mensaje": f"Equipo {team_id} eliminado correctamente"}
