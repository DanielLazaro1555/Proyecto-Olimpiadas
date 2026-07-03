import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from app import create_app


class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.original_database_path = os.environ.get("DATABASE_PATH")
        self.test_db_path = os.path.join(self.tmpdir.name, "test_olimpiadas.db")
        os.environ["DATABASE_PATH"] = self.test_db_path

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        if self.original_database_path is None:
            os.environ.pop("DATABASE_PATH", None)
        else:
            os.environ["DATABASE_PATH"] = self.original_database_path
        self.tmpdir.cleanup()

    def login(self, username="admin", password="admin123"):
        response = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        return response.get_json()["token"]

    def auth_headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_login_returns_admin_user(self):
        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["rol"], "admin")
        self.assertEqual(payload["username"], "admin")
        self.assertIn("token", payload)

    def test_register_team_and_list_it(self):
        token = self.login()

        create_response = self.client.post(
            "/equipos/",
            json={
                "region": "Lima",
                "deporte": "Futbol",
                "nombre_equipo": "Los Halcones",
            },
            headers=self.auth_headers(token),
        )
        self.assertEqual(create_response.status_code, 201)

        list_response = self.client.get("/equipos/")
        self.assertEqual(list_response.status_code, 200)
        equipos = list_response.get_json()
        self.assertEqual(len(equipos), 1)
        self.assertEqual(equipos[0]["nombre_equipo"], "Los Halcones")

    def test_generate_schedule_returns_created_matches(self):
        token = self.login()
        headers = self.auth_headers(token)

        for region, nombre in [("Lima", "Los Halcones"), ("Cusco", "Los Puma")]:
            response = self.client.post(
                "/equipos/",
                json={
                    "region": region,
                    "deporte": "Futbol",
                    "nombre_equipo": nombre,
                },
                headers=headers,
            )
            self.assertEqual(response.status_code, 201)

        fixture_response = self.client.post(
            "/fixture/generar/Futbol",
            headers=headers,
        )

        self.assertEqual(fixture_response.status_code, 201)
        payload = fixture_response.get_json()
        self.assertEqual(payload["deporte"], "Futbol")
        self.assertEqual(payload["total_partidos"], 1)
        self.assertEqual(len(payload["partidos"]), 1)

    def test_register_result_and_fetch_standings(self):
        token = self.login()
        headers = self.auth_headers(token)

        for region, nombre in [("Lima", "Los Halcones"), ("Cusco", "Los Puma")]:
            response = self.client.post(
                "/equipos/",
                json={
                    "region": region,
                    "deporte": "Futbol",
                    "nombre_equipo": nombre,
                },
                headers=headers,
            )
            self.assertEqual(response.status_code, 201)

        fixture_response = self.client.post(
            "/fixture/generar/Futbol",
            headers=headers,
        )
        partido_id = fixture_response.get_json()["partidos"][0]["id"]

        result_response = self.client.post(
            "/partidos/resultado",
            json={
                "id_partido": partido_id,
                "goles_local": 3,
                "goles_visitante": 1,
            },
            headers=headers,
        )
        self.assertEqual(result_response.status_code, 200)

        standings_response = self.client.get("/partidos/tabla/Futbol")
        self.assertEqual(standings_response.status_code, 200)
        tabla = standings_response.get_json()
        self.assertEqual(len(tabla), 2)
        self.assertEqual(tabla[0]["puntos"], 3)
        self.assertEqual(tabla[1]["puntos"], 0)

    def test_register_user_requires_admin(self):
        token = self.login("operador", "operador123")

        response = self.client.post(
            "/auth/registro",
            json={
                "username": "nuevo_usuario",
                "password": "clave123",
                "rol": "visualizador",
            },
            headers=self.auth_headers(token),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json()["error"],
            "Solo los administradores pueden registrar usuarios",
        )
