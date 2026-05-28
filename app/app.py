# app.py
import database as db
from auth import auth_bp  # Importar el nuevo blueprint
from flask import Flask, render_template
from flask_cors import CORS
from servicios import deportistas, equipos, fixture, partidos

app = Flask(__name__)
CORS(app)

app.register_blueprint(equipos.equipos_bp)
app.register_blueprint(deportistas.deportistas_bp)
app.register_blueprint(fixture.fixture_bp)
app.register_blueprint(partidos.partidos_bp)
app.register_blueprint(auth_bp)  # Registrar autenticación


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login_page():
    return render_template("login.html")


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=5000)
