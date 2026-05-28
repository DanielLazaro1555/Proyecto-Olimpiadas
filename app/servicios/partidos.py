# partidos.py

import database as db
from auth import token_required  # solo necesitas token_required para esta ruta
from flask import Blueprint, jsonify, request

partidos_bp = Blueprint("partidos", __name__, url_prefix="/partidos")


@partidos_bp.route("/resultado", methods=["POST"])
@token_required
def registrar_resultado(current_user):
    """Registrar el resultado de un partido. Solo admins."""
    if current_user["rol"] not in ("admin", "operador"):
        return jsonify({"error": "Se requiere rol operador o administrador"}), 403
    data = request.get_json()
    id_partido = data.get("id_partido")
    goles_local = data.get("goles_local")
    goles_visitante = data.get("goles_visitante")

    if not all([id_partido, goles_local is not None, goles_visitante is not None]):
        return jsonify(
            {
                "error": "Faltan campos requeridos: id_partido, goles_local, goles_visitante"
            }
        ), 400

    with db.get_db() as conn:
        cursor = conn.cursor()

        # Verificar si el partido existe
        cursor.execute(
            "SELECT id, resultado_local, resultado_visitante FROM partidos WHERE id = ?",
            (id_partido,),
        )
        partido = cursor.fetchone()
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        # Verificar si ya tiene resultado
        if (
            partido["resultado_local"] is not None
            or partido["resultado_visitante"] is not None
        ):
            return jsonify(
                {
                    "error": "Este partido ya tiene un resultado registrado. No se puede sobrescribir."
                }
            ), 409

        # Actualizar el resultado
        cursor.execute(
            "UPDATE partidos SET resultado_local = ?, resultado_visitante = ? WHERE id = ?",
            (goles_local, goles_visitante, id_partido),
        )
        conn.commit()

        # Actualizar tabla de posiciones (llamada interna)
        cursor.execute("SELECT deporte FROM partidos WHERE id = ?", (id_partido,))
        deporte = cursor.fetchone()["deporte"]
        actualizar_tabla_posiciones(deporte)

        return jsonify(
            {"mensaje": "Resultado registrado exitosamente", "id_partido": id_partido}
        ), 200


@partidos_bp.route("/tabla/<string:deporte>", methods=["GET"])
def obtener_tabla_posiciones(deporte):
    """Devuelve la tabla de posiciones ordenada por puntos, diferencia de goles, etc."""
    with db.get_db() as conn:
        cursor = conn.cursor()

        # Obtener todos los equipos del deporte
        cursor.execute(
            "SELECT id, nombre_equipo FROM equipos WHERE deporte = ?", (deporte,)
        )
        equipos = cursor.fetchall()

        tabla = []
        for equipo in equipos:
            # Partidos como local
            cursor.execute(
                """
                SELECT resultado_local, resultado_visitante FROM partidos
                WHERE deporte = ? AND equipo_local_id = ? AND resultado_local IS NOT NULL
            """,
                (deporte, equipo["id"]),
            )
            locales = cursor.fetchall()

            # Partidos como visitante
            cursor.execute(
                """
                SELECT resultado_local, resultado_visitante FROM partidos
                WHERE deporte = ? AND equipo_visitante_id = ? AND resultado_visitante IS NOT NULL
            """,
                (deporte, equipo["id"]),
            )
            visitantes = cursor.fetchall()

            # Calcular estadísticas
            puntos = 0
            goles_favor = 0
            goles_contra = 0
            partidos_jugados = 0
            ganados = 0
            empatados = 0
            perdidos = 0

            for p in locales:
                gf = p["resultado_local"]
                gc = p["resultado_visitante"]
                goles_favor += gf
                goles_contra += gc
                partidos_jugados += 1
                if gf > gc:
                    puntos += 3
                    ganados += 1
                elif gf == gc:
                    puntos += 1
                    empatados += 1
                else:
                    perdidos += 1

            for p in visitantes:
                gf = p["resultado_visitante"]
                gc = p["resultado_local"]
                goles_favor += gf
                goles_contra += gc
                partidos_jugados += 1
                if gf > gc:
                    puntos += 3
                    ganados += 1
                elif gf == gc:
                    puntos += 1
                    empatados += 1
                else:
                    perdidos += 1

            diferencia_goles = goles_favor - goles_contra

            tabla.append(
                {
                    "equipo_id": equipo["id"],
                    "equipo_nombre": equipo["nombre_equipo"],
                    "pj": partidos_jugados,
                    "pg": ganados,
                    "pe": empatados,
                    "pp": perdidos,
                    "gf": goles_favor,
                    "gc": goles_contra,
                    "dg": diferencia_goles,
                    "puntos": puntos,
                }
            )

        # Ordenar: puntos (desc), diferencia de goles (desc), goles a favor (desc)
        tabla.sort(key=lambda x: (x["puntos"], x["dg"], x["gf"]), reverse=True)

        return jsonify(tabla), 200


def actualizar_tabla_posiciones(deporte):
    """
    Función interna para recalcular la tabla de posiciones.
    No es necesario devolver nada, solo se ejecuta después de cada resultado.
    """
    print(f"Tabla de posiciones actualizada para el deporte: {deporte}")
    return
