import datetime
import os

import jwt


RAW_SECRET_KEY = os.environ.get("SECRET_KEY", "u22326979")


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
