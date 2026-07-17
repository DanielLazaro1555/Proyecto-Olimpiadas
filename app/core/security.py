import datetime
import os
import secrets

import jwt


def _resolve_raw_secret_key():
    """Resuelve la clave de firma JWT desde el entorno.

    No hay un valor por defecto hardcodeado: un secreto fijo y conocido en el
    código fuente permitiría forjar tokens (incluido rol=admin) contra
    cualquier despliegue que olvide definir SECRET_KEY. Si la variable no
    está configurada, se genera una clave aleatoria por proceso — esto
    invalida las sesiones existentes al reiniciar, lo cual es preferible a
    un secreto predecible.
    """
    raw = os.environ.get("SECRET_KEY")
    if not raw:
        print(
            "AVISO: SECRET_KEY no está configurada en el entorno. Se generó una "
            "clave aleatoria solo para esta ejecución (los tokens emitidos no "
            "sobrevivirán a un reinicio). Define SECRET_KEY en producción — ver "
            "app/.env.example."
        )
        raw = secrets.token_hex(32)
    return raw


RAW_SECRET_KEY = _resolve_raw_secret_key()


def get_secret_key():
    """Extiende claves cortas para evitar advertencias de HMAC inseguro."""
    if len(RAW_SECRET_KEY) >= 32:
        return RAW_SECRET_KEY
    repeats = (32 // len(RAW_SECRET_KEY)) + 1
    return (RAW_SECRET_KEY * repeats)[:32]


SECRET_KEY = get_secret_key()


def build_token(payload, expires_in_hours=24):
    token_payload = {
        **payload,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=expires_in_hours),
    }
    return jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
