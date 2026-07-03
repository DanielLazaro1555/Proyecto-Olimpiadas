from core.errors import DomainError


class DeportistasService:
    def __init__(self, repository):
        self.repository = repository

    def register_athlete(self, team_id, nombre, apellido, documento):
        if not all([team_id, nombre, apellido, documento]):
            raise DomainError("Faltan campos requeridos", 400)

        if not self.repository.team_exists(team_id):
            raise DomainError("El equipo no existe", 404)

        athlete = self.repository.get_athlete_by_document(documento)
        athlete_id = athlete["id"] if athlete else self.repository.create_athlete(
            nombre,
            apellido,
            documento,
        )

        if self.repository.is_team_membership_registered(team_id, athlete_id):
            raise DomainError("El deportista ya está inscrito en este equipo", 409)

        self.repository.create_membership(team_id, athlete_id)
        return {
            "mensaje": "Deportista inscrito exitosamente",
            "id_deportista": athlete_id,
        }

    def list_team_athletes(self, team_id):
        return self.repository.list_team_athletes(team_id)
