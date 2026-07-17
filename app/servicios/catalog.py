# catalog.py
from flask import Blueprint, jsonify, current_app

catalog_bp = Blueprint("catalog", __name__, url_prefix="/catalog")

@catalog_bp.route("/", methods=["GET"])
def get_service_catalog():
    """
    Retorna el catálogo de servicios (registro UDDI simplificado)
    con las rutas, métodos soportados y control de acceso.
    """
    servicios = [
        {
            "nombre": "Servicio de Autenticación",
            "descripcion": "Gestión de acceso al sistema (JWT y bcrypt) y usuarios",
            "prefijo": "/auth",
            "endpoints": [
                {"ruta": "/auth/login", "metodos": ["POST"], "descripcion": "Autentica al usuario y retorna token JWT", "roles_permitidos": ["publico"]},
                {"ruta": "/auth/registro", "metodos": ["POST"], "descripcion": "Crea una cuenta nueva (solo admin)", "roles_permitidos": ["admin"]},
                {"ruta": "/auth/usuarios", "metodos": ["GET"], "descripcion": "Lista todos los usuarios del sistema (solo admin)", "roles_permitidos": ["admin"]},
                {"ruta": "/auth/usuarios/<id>", "metodos": ["DELETE"], "descripcion": "Elimina un usuario (solo admin)", "roles_permitidos": ["admin"]},
                {"ruta": "/auth/auditoria", "metodos": ["GET"], "descripcion": "Consulta el historial de auditoría del sistema (solo admin)", "roles_permitidos": ["admin"]}
            ]
        },
        {
            "nombre": "Servicio de Equipos",
            "descripcion": "Gestión de equipos participantes por región",
            "prefijo": "/equipos",
            "endpoints": [
                {"ruta": "/equipos/", "metodos": ["GET"], "descripcion": "Devuelve el listado completo de equipos", "roles_permitidos": ["publico"]},
                {"ruta": "/equipos/", "metodos": ["POST"], "descripcion": "Registra un equipo con validación de región (admin/operador)", "roles_permitidos": ["admin", "operador"]},
                {"ruta": "/equipos/<id>", "metodos": ["DELETE"], "descripcion": "Elimina un equipo si no tiene partidos (admin/operador)", "roles_permitidos": ["admin", "operador"]}
            ]
        },
        {
            "nombre": "Servicio de Deportistas",
            "descripcion": "Administración de inscripción de deportistas en equipos",
            "prefijo": "/deportistas",
            "endpoints": [
                {"ruta": "/deportistas/equipo/<id>", "metodos": ["GET"], "descripcion": "Lista los deportistas de un equipo", "roles_permitidos": ["publico"]},
                {"ruta": "/deportistas/inscribir", "metodos": ["POST"], "descripcion": "Inscribe un deportista validando duplicados (admin/operador)", "roles_permitidos": ["admin", "operador"]}
            ]
        },
        {
            "nombre": "Servicio de Fixture",
            "descripcion": "Genera el calendario de enfrentamientos aleatorios por deporte",
            "prefijo": "/fixture",
            "endpoints": [
                {"ruta": "/fixture/generar/<deporte>", "metodos": ["POST"], "descripcion": "Crea emparejamientos aleatorios con fechas (mínimo 2 equipos, admin/operador)", "roles_permitidos": ["admin", "operador"]},
                {"ruta": "/fixture/eliminar/<deporte>", "metodos": ["DELETE"], "descripcion": "Elimina el calendario de un deporte (admin/operador)", "roles_permitidos": ["admin", "operador"]},
                {"ruta": "/fixture/consultar/<deporte>", "metodos": ["GET"], "descripcion": "Devuelve el calendario de partidos por deporte", "roles_permitidos": ["publico"]}
            ]
        },
        {
            "nombre": "Servicio de Partidos y Clasificación",
            "descripcion": "Gestión de resultados de partidos y tabla de posiciones",
            "prefijo": "/partidos",
            "endpoints": [
                {"ruta": "/partidos/resultado", "metodos": ["POST"], "descripcion": "Registra el resultado de un partido (no sobrescribible, admin/operador)", "roles_permitidos": ["admin", "operador"]},
                {"ruta": "/partidos/tabla/<deporte>", "metodos": ["GET"], "descripcion": "Calcula y devuelve la tabla de posiciones por deporte", "roles_permitidos": ["publico"]}
            ]
        },
        {
            "nombre": "Servicio de Reportes",
            "descripcion": "Reportes públicos de tabla de posiciones, goleadores y estadísticas por deporte",
            "prefijo": "/reportes",
            "endpoints": [
                {"ruta": "/reportes/tabla/<deporte>", "metodos": ["GET"], "descripcion": "Tabla de posiciones (alias de /partidos/tabla)", "roles_permitidos": ["publico"]},
                {"ruta": "/reportes/goleadores/<deporte>", "metodos": ["GET"], "descripcion": "Ranking de goleadores (parámetro opcional ?limite=)", "roles_permitidos": ["publico"]},
                {"ruta": "/reportes/estadisticas/<deporte>", "metodos": ["GET"], "descripcion": "Estadísticas generales: partidos, goles, promedio, equipo líder", "roles_permitidos": ["publico"]}
            ]
        },
        {
            "nombre": "Servicio de Notificaciones",
            "descripcion": "Historial de notificaciones (correo) disparadas por eventos del sistema",
            "prefijo": "/notificaciones",
            "endpoints": [
                {"ruta": "/notificaciones/", "metodos": ["GET"], "descripcion": "Lista el historial de notificaciones enviadas/simuladas (solo admin)", "roles_permitidos": ["admin"]}
            ]
        },
        {
            "nombre": "Servicio Catálogo (UDDI)",
            "descripcion": "Mecanismo de autodescubrimiento y registro de servicios",
            "prefijo": "/catalog",
            "endpoints": [
                {"ruta": "/catalog/", "metodos": ["GET"], "descripcion": "Obtiene la lista de todos los servicios y sus contratos", "roles_permitidos": ["publico"]}
            ]
        }
    ]
    
    return jsonify({
        "status": "online",
        "descripcion": "Registro Interno de Servicios (Catálogo UDDI) — Olimpiadas Perú",
        "servicios": servicios
    }), 200
