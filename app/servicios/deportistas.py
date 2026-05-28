# deportistas.py

import database as db
from auth import token_required  # Importar el decorador
from flask import Blueprint, jsonify, request

deportistas_bp = Blueprint("deportistas", __name__, url_prefix="/deportistas")


@deportistas_bp.route("/inscribir", methods=["POST"])
@token_required
def inscribir_deportista(current_user):
    """Inscribir un deportista en un equipo. Solo admins."""
    if current_user["rol"] != "admin":
        return jsonify({"error": "Solo los administradores pueden inscribir deportistas"}), 403
    data = request.get_json()
    id_equipo = data.get("id_equipo")
    nombre = data.get("nombre")
    apellido = data.get("apellido")
    documento = data.get("documento")

    if not all([id_equipo, nombre, apellido, documento]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM equipos WHERE id = ?", (id_equipo,))
        if not cursor.fetchone():
            return jsonify({"error": "El equipo no existe"}), 404

        cursor.execute("SELECT id FROM deportistas WHERE documento = ?", (documento,))
        deportista = cursor.fetchone()
        if deportista:
            id_deportista = deportista["id"]
        else:
            cursor.execute(
                "INSERT INTO deportistas (nombre, apellido, documento) VALUES (?, ?, ?)",
                (nombre, apellido, documento),
            )
            id_deportista = cursor.lastrowid

        cursor.execute(
            "SELECT id FROM inscripciones WHERE equipo_id = ? AND deportista_id = ?",
            (id_equipo, id_deportista),
        )
        if cursor.fetchone():
            return jsonify(
                {"error": "El deportista ya está inscrito en este equipo"}
            ), 409

        cursor.execute(
            "INSERT INTO inscripciones (equipo_id, deportista_id) VALUES (?, ?)",
            (id_equipo, id_deportista),
        )
        conn.commit()
        return jsonify(
            {
                "mensaje": "Deportista inscrito exitosamente",
                "id_deportista": id_deportista,
            }
        ), 201


@deportistas_bp.route("/equipo/<int:id_equipo>", methods=["GET"])
def listar_deportistas_por_equipo(id_equipo):
    """
    Consulta pública (sin autenticación) de deportistas por equipo.
    """
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.nombre, d.apellido, d.documento
            FROM deportistas d
            JOIN inscripciones i ON d.id = i.deportista_id
            WHERE i.equipo_id = ?
        """,
            (id_equipo,),
        )
        deportistas = [dict(row) for row in cursor.fetchall()]
    return jsonify(deportistas), 200
