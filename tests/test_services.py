import sqlite3
import sys
import unittest
from pathlib import Path

import bcrypt

APP_DIR = Path(__file__).resolve().parents[1] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from core.errors import DomainError
from core.security import decode_token
from core.services.auth_service import AuthService
from core.services.equipos_service import EquiposService
from core.services.fixture_service import FixtureService
from core.services.partidos_service import PartidosService


class FakeAuthRepository:
    def __init__(self):
        admin_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode("utf-8")
        self.users = {
            "admin": {
                "id": 1,
                "username": "admin",
                "password_hash": admin_hash,
                "rol": "admin",
            }
        }
        self.created = []

    def get_user_by_username(self, username):
        return self.users.get(username)

    def create_user(self, username, password_hash, role):
        if username in self.users:
            raise sqlite3.IntegrityError("duplicate")
        self.users[username] = {
            "id": len(self.users) + 1,
            "username": username,
            "password_hash": password_hash,
            "rol": role,
        }
        self.created.append(username)

    def list_users(self):
        return [
            {"id": user["id"], "username": user["username"], "rol": user["rol"]}
            for user in self.users.values()
        ]

    def get_user_by_id(self, user_id):
        return next((user for user in self.users.values() if user["id"] == user_id), None)

    def delete_user(self, user_id):
        username = next(
            key for key, value in self.users.items() if value["id"] == user_id
        )
        del self.users[username]

    def is_duplicate_username_error(self, error):
        return isinstance(error, sqlite3.IntegrityError)


class FakeEquiposRepository:
    def __init__(self):
        self.by_region_sport = set()
        self.teams = []

    def team_exists_by_region_and_sport(self, region, sport):
        return (region, sport) in self.by_region_sport

    def create_team(self, region, sport, team_name):
        team_id = len(self.teams) + 1
        self.by_region_sport.add((region, sport))
        self.teams.append(
            {"id": team_id, "region": region, "deporte": sport, "nombre_equipo": team_name}
        )
        return team_id

    def list_teams(self):
        return self.teams

    def get_team(self, team_id):
        return next((team for team in self.teams if team["id"] == team_id), None)

    def team_has_matches(self, team_id):
        return False

    def delete_team(self, team_id):
        self.teams = [team for team in self.teams if team["id"] != team_id]


class FakeFixtureRepository:
    def __init__(self, teams=None, has_schedule=False):
        self.teams = teams or []
        self.has_schedule_flag = has_schedule

    def list_teams_by_sport(self, sport):
        return self.teams

    def sport_has_schedule(self, sport):
        return self.has_schedule_flag

    def create_schedule(self, sport, teams):
        return [{"id": 1, "local": teams[0]["nombre_equipo"], "visitante": teams[1]["nombre_equipo"], "fecha": "2026-07-03", "hora": "15:00"}]

    def list_schedule(self, sport):
        return []

    def delete_schedule(self, sport):
        return 0


class FakePartidosRepository:
    def __init__(self, match=None, teams=None, home=None, away=None, rosters=None):
        self.match = match
        self.teams = teams or []
        self.home = home or {}
        self.away = away or {}
        self.rosters = rosters or {}
        self.saved = None
        self.saved_scorers = None

    def get_match(self, match_id):
        return self.match

    def get_match_with_teams(self, match_id):
        return self.match

    def save_match_result(self, match_id, local_goals, visitor_goals):
        self.saved = (match_id, local_goals, visitor_goals)

    def list_teams_by_sport(self, sport):
        return self.teams

    def list_finished_home_matches(self, sport, team_id):
        return self.home.get(team_id, [])

    def list_finished_away_matches(self, sport, team_id):
        return self.away.get(team_id, [])

    def is_athlete_in_team(self, athlete_id, team_id):
        return athlete_id in self.rosters.get(team_id, [])

    def save_goal_scorers(self, match_id, scorer_rows):
        self.saved_scorers = scorer_rows

    def get_top_scorers(self, sport, limit):
        return []

    def get_match_counts(self, sport):
        return {"total": 0, "jugados": 0, "pendientes": 0, "total_goles": 0}


class ServicesTestCase(unittest.TestCase):
    def test_auth_login_returns_valid_token(self):
        repo = FakeAuthRepository()
        service = AuthService(repo)

        payload = service.login("admin", "admin123")

        decoded = decode_token(payload["token"])
        self.assertEqual(payload["rol"], "admin")
        self.assertEqual(decoded["username"], "admin")

    def test_auth_register_requires_admin(self):
        repo = FakeAuthRepository()
        service = AuthService(repo)

        with self.assertRaises(DomainError) as error:
            service.register_user(
                {"rol": "operador"},
                "nuevo",
                "password1",
                "visualizador",
            )

        self.assertEqual(error.exception.status_code, 403)

    def test_create_team_detects_duplicate(self):
        repo = FakeEquiposRepository()
        repo.by_region_sport.add(("Lima", "Futbol"))
        service = EquiposService(repo)

        with self.assertRaises(DomainError) as error:
            service.create_team("Lima", "Futbol", "Equipo 1")

        self.assertEqual(error.exception.status_code, 409)

    def test_generate_schedule_requires_two_teams(self):
        service = FixtureService(FakeFixtureRepository(teams=[]))

        with self.assertRaises(DomainError) as error:
            service.generate_schedule("Futbol")

        self.assertEqual(error.exception.status_code, 400)

    def test_register_result_rejects_existing_score(self):
        repo = FakePartidosRepository(
            match={"id": 1, "deporte": "Futbol", "resultado_local": 1, "resultado_visitante": 0}
        )
        service = PartidosService(repo)

        with self.assertRaises(DomainError) as error:
            service.register_result(1, 2, 1)

        self.assertEqual(error.exception.status_code, 409)

    def test_register_result_with_valid_scorers_saves_goals(self):
        repo = FakePartidosRepository(
            match={
                "id": 1, "deporte": "Futbol",
                "equipo_local_id": 10, "equipo_visitante_id": 20,
                "resultado_local": None, "resultado_visitante": None,
            },
            rosters={10: [101, 102], 20: [201]},
        )
        service = PartidosService(repo)

        service.register_result(
            1, 2, 1,
            goleadores_local=[{"deportista_id": 101, "goles": 2}],
            goleadores_visitante=[{"deportista_id": 201, "goles": 1}],
        )

        self.assertEqual(repo.saved, (1, 2, 1))
        self.assertEqual(len(repo.saved_scorers), 2)

    def test_register_result_rejects_scorer_not_in_team(self):
        repo = FakePartidosRepository(
            match={
                "id": 1, "deporte": "Futbol",
                "equipo_local_id": 10, "equipo_visitante_id": 20,
                "resultado_local": None, "resultado_visitante": None,
            },
            rosters={10: [101], 20: [201]},
        )
        service = PartidosService(repo)

        with self.assertRaises(DomainError) as error:
            service.register_result(
                1, 1, 0,
                goleadores_local=[{"deportista_id": 999, "goles": 1}],
            )

        self.assertEqual(error.exception.status_code, 400)

    def test_register_result_rejects_goal_sum_mismatch(self):
        repo = FakePartidosRepository(
            match={
                "id": 1, "deporte": "Futbol",
                "equipo_local_id": 10, "equipo_visitante_id": 20,
                "resultado_local": None, "resultado_visitante": None,
            },
            rosters={10: [101], 20: [201]},
        )
        service = PartidosService(repo)

        with self.assertRaises(DomainError) as error:
            service.register_result(
                1, 3, 0,
                goleadores_local=[{"deportista_id": 101, "goles": 1}],
            )

        self.assertEqual(error.exception.status_code, 400)

    def test_get_statistics_computes_average_goals(self):
        repo = FakePartidosRepository()
        repo.get_match_counts = lambda sport: {
            "total": 4, "jugados": 2, "pendientes": 2, "total_goles": 5
        }
        service = PartidosService(repo)

        stats = service.get_statistics("Futbol")

        self.assertEqual(stats["partidos_jugados"], 2)
        self.assertEqual(stats["promedio_goles_por_partido"], 2.5)

    def test_build_standings_sorts_by_points(self):
        repo = FakePartidosRepository(
            teams=[
                {"id": 1, "nombre_equipo": "A"},
                {"id": 2, "nombre_equipo": "B"},
            ],
            home={1: [{"resultado_local": 2, "resultado_visitante": 0}]},
            away={2: [{"resultado_local": 2, "resultado_visitante": 0}]},
        )
        service = PartidosService(repo)

        table = service.build_standings("Futbol")

        self.assertEqual(table[0]["equipo_nombre"], "A")
        self.assertEqual(table[0]["puntos"], 3)
