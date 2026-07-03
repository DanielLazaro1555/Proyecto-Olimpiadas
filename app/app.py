# app.py
import os

import database as db
from auth import auth_bp
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from servicios import deportistas, equipos, fixture, partidos

def register_blueprints(app):
    app.register_blueprint(equipos.equipos_bp)
    app.register_blueprint(deportistas.deportistas_bp)
    app.register_blueprint(fixture.fixture_bp)
    app.register_blueprint(partidos.partidos_bp)
    app.register_blueprint(auth_bp)


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")


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


def create_app():
    app = Flask(__name__)
    CORS(app)

    register_blueprints(app)
    register_routes(app)
    register_error_handlers(app)
    db.init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
