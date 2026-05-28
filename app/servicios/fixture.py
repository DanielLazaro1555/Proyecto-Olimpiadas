# fixture.py - Servicio para generar y consultar fixtures de partidos con autenticación

import random
from datetime import datetime, timedelta

import database as db
from auth import token_required  # Importamos el decorador
from flask import Blueprint, jsonify

fixture_bp = Blueprint("fixture", __name__, url_prefix="/fixture")


@fixture_bp.route("/generar/<string:deporte>", methods=["POST"])
@token_required
def generar_fixture(current_user, deporte):
    """Genera enfrentamientos para un deporte. Solo admins."""
    if current_user["rol"] not in ("admin", "operador"):
        return jsonify({"error": "Se requiere rol operador o administrador"}), 403
    with db.get_db() as conn:
        cursor = conn.cursor()

        # Contar equipos inscritos en el deporte (case-insensitive)
        cursor.execute(
            "SELECT id, nombre_equipo FROM equipos WHERE deporte = ? COLLATE NOCASE", (deporte,)
        )
        equipos = cursor.fetchall()

        if len(equipos) < 2:
            return jsonify(
                {
                    "error": f"Se necesitan al menos 2 equipos para generar fixture. Actualmente hay {len(equipos)}."
                }
            ), 400

        # Verificar si ya existe un fixture para este deporte
        cursor.execute("SELECT id FROM partidos WHERE deporte = ? COLLATE NOCASE LIMIT 1", (deporte,))
        if cursor.fetchone():
            return jsonify(
                {
                    "error": "Ya existe un fixture para este deporte. Elimina los partidos existentes si deseas regenerar."
                }
            ), 409

        # Generar todos los enfrentamientos (todos contra todos, una sola ronda)
        partidos = []
        for i in range(len(equipos)):
            for j in range(i + 1, len(equipos)):
                partidos.append((equipos[i]["id"], equipos[j]["id"]))

        random.shuffle(partidos)

        fecha_base = datetime.now() + timedelta(days=1)
        fecha_base = fecha_base.replace(hour=15, minute=0, second=0, microsecond=0)
        partidos_guardados = []

        for idx, (local_id, visitante_id) in enumerate(partidos):
            fecha_partido = fecha_base + timedelta(days=idx * 2)
            cursor.execute(
                """
                INSERT INTO partidos (deporte, equipo_local_id, equipo_visitante_id, fecha, hora)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    deporte,
                    local_id,
                    visitante_id,
                    fecha_partido.strftime("%Y-%m-%d"),
                    fecha_partido.strftime("%H:%M"),
                ),
            )
            partidos_guardados.append(
                {
                    "id": cursor.lastrowid,
                    "local": next(
                        e["nombre_equipo"] for e in equipos if e["id"] == local_id
                    ),
                    "visitante": next(
                        e["nombre_equipo"] for e in equipos if e["id"] == visitante_id
                    ),
                    "fecha": fecha_partido.strftime("%Y-%m-%d"),
                    "hora": fecha_partido.strftime("%H:%M"),
                }
            )

        conn.commit()
        return jsonify(
            {
                "mensaje": f"Fixture generado exitosamente para {deporte}",
                "deporte": deporte,
                "total_partidos": len(partidos_guardados),
                "partidos": partidos_guardados,
            }
        ), 201


@fixture_bp.route("/consultar/<string:deporte>", methods=["GET"])
def consultar_fixture(deporte):
    """
    Consultar el fixture (lista de partidos) de un deporte.
    Público (sin autenticación).
    """
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.id, p.fecha, p.hora,
                   eq_local.nombre_equipo as local,
                   eq_visit.nombre_equipo as visitante,
                   p.resultado_local, p.resultado_visitante
            FROM partidos p
            JOIN equipos eq_local ON p.equipo_local_id = eq_local.id
            JOIN equipos eq_visit ON p.equipo_visitante_id = eq_visit.id
            WHERE p.deporte = ? COLLATE NOCASE
            ORDER BY p.fecha, p.hora
        """,
            (deporte,),
        )
        partidos = [dict(row) for row in cursor.fetchall()]
    return jsonify(partidos), 200


@fixture_bp.route("/eliminar/<string:deporte>", methods=["DELETE"])
@token_required
def eliminar_fixture(current_user, deporte):
    """Eliminar partidos de un deporte para regenerar. Solo operador y admin."""
    if current_user["rol"] not in ("admin", "operador"):
        return jsonify({"error": "Se requiere rol operador o administrador"}), 403
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM partidos WHERE deporte = ?", (deporte,))
        conn.commit()
        eliminados = cursor.rowcount
    return jsonify(
        {"mensaje": f"Se eliminaron {eliminados} partidos del deporte {deporte}"}
    ), 200
