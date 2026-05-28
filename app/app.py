# app.py
import database as db
from auth import auth_bp
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from servicios import deportistas, equipos, fixture, partidos

app = Flask(__name__)
CORS(app)

app.register_blueprint(equipos.equipos_bp)
app.register_blueprint(deportistas.deportistas_bp)
app.register_blueprint(fixture.fixture_bp)
app.register_blueprint(partidos.partidos_bp)
app.register_blueprint(auth_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método no permitido"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
