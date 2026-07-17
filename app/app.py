# app.py
import os
import json

import database as db
from auth import auth_bp
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from servicios import deportistas, equipos, fixture, partidos

def register_blueprints(app):
    app.register_blueprint(equipos.equipos_bp)
    app.register_blueprint(deportistas.deportistas_bp)
    app.register_blueprint(fixture.fixture_bp)
    app.register_blueprint(partidos.partidos_bp)
    app.register_blueprint(auth_bp)
    from servicios.catalog import catalog_bp
    app.register_blueprint(catalog_bp)
    from servicios.reportes import reportes_bp
    app.register_blueprint(reportes_bp)
    from servicios.notificaciones import notificaciones_bp
    app.register_blueprint(notificaciones_bp)


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/docs")
    def api_docs():
        return render_template("docs.html")


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Error interno del servidor"}), 500


def register_middleware(app):
    @app.after_request
    def audit_log(response):
        if request.method in ("POST", "DELETE") and any(
            request.path.startswith(prefix)
            for prefix in ("/auth", "/equipos", "/deportistas", "/partidos", "/fixture")
        ):
            if request.path == "/auth/auditoria":
                return response

            username = "Anonimo"
            rol = "Publico"
            auth_header = request.headers.get("Authorization", "")
            token = auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
            if token:
                try:
                    from core.security import decode_token
                    data = decode_token(token)
                    username = data.get("username", "Anonimo")
                    rol = data.get("rol", "Publico")
                except Exception:
                    pass
            elif request.path == "/auth/login" and response.status_code == 200:
                try:
                    req_data = request.get_json(silent=True) or {}
                    username = req_data.get("username", "Anonimo")
                    res_data = response.get_json() or {}
                    rol = res_data.get("rol", "Publico")
                except Exception:
                    pass

            payload_str = ""
            if request.is_json:
                try:
                    req_data = request.get_json(silent=True) or {}
                    censored_data = dict(req_data)
                    if "password" in censored_data:
                        censored_data["password"] = "******"
                    payload_str = json.dumps(censored_data)
                except Exception:
                    pass

            try:
                from core.repositories.audit_repository import AuditRepository
                from core.services.audit_service import AuditService
                with db.get_db() as conn:
                    service = AuditService(AuditRepository(conn))
                    service.create_audit(
                        username=username,
                        rol=rol,
                        metodo=request.method,
                        ruta=request.path,
                        payload=payload_str,
                        status_code=response.status_code
                    )
            except Exception as e:
                app.logger.error(f"Error escribiendo auditoria: {e}")
        return response


def create_app():
    app = Flask(__name__)
    CORS(app)

    register_blueprints(app)
    register_routes(app)
    register_error_handlers(app)
    register_middleware(app)
    db.init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
