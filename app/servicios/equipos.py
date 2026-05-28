# equipos.py

import database as db
from auth import token_required  # Importamos el decorador de autenticación
from flask import Blueprint, jsonify, request

equipos_bp = Blueprint("equipos", __name__, url_prefix="/equipos")


@equipos_bp.route("/", methods=["POST"])
@token_required
def registrar_equipo(current_user):
    """Registrar un nuevo equipo. Solo admins."""
    if current_user["rol"] != "admin":
        return jsonify({"error": "Solo los administradores pueden registrar equipos"}), 403
    data = request.get_json()
    pais = data.get("pais")
    deporte = data.get("deporte")
    nombre_equipo = data.get("nombre_equipo")

    if not all([pais, deporte, nombre_equipo]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM equipos WHERE pais = ? AND deporte = ?", (pais, deporte)
        )
        if cursor.fetchone():
            return jsonify(
                {"error": "Ya existe un equipo de ese país en este deporte"}
            ), 409

        cursor.execute(
            "INSERT INTO equipos (pais, deporte, nombre_equipo) VALUES (?, ?, ?)",
            (pais, deporte, nombre_equipo),
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        return jsonify(
            {"mensaje": "Equipo registrado exitosamente", "id": nuevo_id}
        ), 201


@equipos_bp.route("/", methods=["GET"])
def consultar_equipos():
    """
    Consulta pública (sin autenticación) de todos los equipos.
    """
    with db.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, pais, deporte, nombre_equipo FROM equipos")
        equipos = [dict(row) for row in cursor.fetchall()]
    return jsonify(equipos), 200


@equipos_bp.route("/<int:equipo_id>", methods=["DELETE"])
@token_required
def eliminar_equipo(current_user, equipo_id):
    """Elimina un equipo por ID. Solo admins."""
    if current_user["rol"] != "admin":
        return jsonify({"error": "Solo los administradores pueden eliminar equipos"}), 403
    with db.get_db() as conn:
        cursor = conn.cursor()

        equipo = cursor.execute(
            "SELECT id FROM equipos WHERE id = ?", (equipo_id,)
        ).fetchone()
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404

        partido = cursor.execute(
            "SELECT id FROM partidos WHERE equipo_local_id = ? OR equipo_visitante_id = ?",
            (equipo_id, equipo_id),
        ).fetchone()
        if partido:
            return jsonify({"error": "No se puede eliminar un equipo con partidos asignados"}), 409

        cursor.execute("DELETE FROM equipos WHERE id = ?", (equipo_id,))
        conn.commit()

    return jsonify({"mensaje": f"Equipo {equipo_id} eliminado correctamente"}), 200
