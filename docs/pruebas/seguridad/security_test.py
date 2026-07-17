#!/usr/bin/env python3
"""Pruebas de seguridad estilo OWASP para el Sistema Olimpiadas Perú.

Alternativa a OWASP ZAP (no instalado en este entorno) usando la librería
estándar de Python + PyJWT (ya es dependencia del proyecto, ver
app/requirements.txt). No es un escaneo automatizado exhaustivo como ZAP,
sino un conjunto de pruebas dirigidas a los puntos de riesgo típicos de una
API REST con autenticación JWT: SQLi, bypass de autenticación, IDOR /
escalación de privilegios, cabeceras de seguridad, CORS y fuerza bruta.

Uso:
    python security_test.py --base-url http://127.0.0.1:5000

Cada hallazgo real se agrega a `FINDINGS` y se vuelca a JSON al final para
que el informe (INFORME_SEGURIDAD.md) los referencie sin fabricar datos.
"""
import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt

FINDINGS = []


def add_finding(titulo, severidad, descripcion, evidencia):
    FINDINGS.append({
        "titulo": titulo,
        "severidad": severidad,
        "descripcion": descripcion,
        "evidencia": evidencia,
    })
    print(f"[{severidad}] {titulo}")
    print(f"    {descripcion}")
    print(f"    Evidencia: {evidencia}\n")


def call(method, url, body=None, headers=None, timeout=10):
    all_headers = {"Content-Type": "application/json"}
    if headers:
        all_headers.update(headers)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=all_headers, method=method)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            text = res.read().decode("utf-8", errors="replace")
            status = res.status
    except urllib.error.HTTPError as err:
        text = err.read().decode("utf-8", errors="replace")
        status = err.code
    elapsed_ms = (time.perf_counter() - start) * 1000
    try:
        parsed = json.loads(text) if text else None
    except json.JSONDecodeError:
        parsed = None
    return status, parsed, text, elapsed_ms


def login(base, username, password):
    status, data, _, _ = call("POST", f"{base}/auth/login", {"username": username, "password": password})
    return data.get("token") if status == 200 and data else None


# ── 1. Cabeceras de seguridad ────────────────────────────────────────────

def check_security_headers(base):
    req = urllib.request.Request(f"{base}/equipos/", method="GET")
    with urllib.request.urlopen(req, timeout=10) as res:
        headers = dict(res.headers.items())

    esperadas = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Content-Security-Policy",
        "Strict-Transport-Security",
    ]
    faltantes = [h for h in esperadas if h not in headers]
    if faltantes:
        add_finding(
            "Faltan cabeceras de seguridad HTTP",
            "MEDIA",
            "La API no envía cabeceras que mitigan clickjacking (X-Frame-Options), "
            "MIME-sniffing (X-Content-Type-Options), inyección de contenido "
            "(Content-Security-Policy) ni fuerza HTTPS (HSTS). Como es una API "
            "consumida por el propio frontend servido por el mismo Flask, el riesgo "
            "es moderado, pero conviene añadirlas (p. ej. con flask-talisman).",
            f"Cabeceras ausentes en GET /equipos/: {faltantes}. "
            f"Cabeceras presentes: {sorted(headers.keys())}",
        )
    else:
        print("[OK] Todas las cabeceras de seguridad esperadas están presentes.\n")


# ── 2. CORS ───────────────────────────────────────────────────────────────

def check_cors(base):
    req = urllib.request.Request(
        f"{base}/equipos/", method="GET",
        headers={"Origin": "https://sitio-atacante-e2e.example"},
    )
    with urllib.request.urlopen(req, timeout=10) as res:
        acao = res.headers.get("Access-Control-Allow-Origin")

    if acao in ("*",) or acao == "https://sitio-atacante-e2e.example":
        add_finding(
            "CORS sin restricción de origen (Access-Control-Allow-Origin abierto)",
            "MEDIA",
            "flask-cors está configurado como CORS(app) sin restricciones "
            "(app/app.py), por lo que cualquier origen puede leer las respuestas "
            "de la API vía JavaScript, incluyendo endpoints protegidos si el "
            "atacante consigue un token por otra vía (p. ej. XSS). Se recomienda "
            "restringir origins a los dominios conocidos del frontend.",
            f"Origin enviado: https://sitio-atacante-e2e.example -> "
            f"Access-Control-Allow-Origin recibido: {acao}",
        )
    else:
        print(f"[OK] CORS no refleja orígenes arbitrarios (recibido: {acao}).\n")


# ── 3. Inyección SQL ─────────────────────────────────────────────────────

def check_sql_injection(base, token):
    payloads_login = [
        ("admin' OR '1'='1", "x"),
        ("admin'--", "x"),
        ("admin\"OR\"\"=\"", "x"),
    ]
    bypassed = []
    for user, pwd in payloads_login:
        status, data, _, _ = call("POST", f"{base}/auth/login", {"username": user, "password": pwd})
        if status == 200:
            bypassed.append((user, pwd))

    if bypassed:
        add_finding(
            "Bypass de autenticación vía inyección SQL en /auth/login",
            "CRITICA",
            "Es posible iniciar sesión sin credenciales válidas usando payloads de "
            "inyección SQL clásicos en el campo username.",
            f"Payloads exitosos: {bypassed}",
        )
    else:
        print("[OK] /auth/login no es vulnerable a los payloads de SQLi probados "
              "(usa consultas parametrizadas).\n")

    # Inyección en parámetro de ruta (deporte)
    payload_ruta = "Fútbol' OR '1'='1"
    status, data, text, _ = call(
        "GET", f"{base}/partidos/tabla/{urllib.parse.quote(payload_ruta)}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if status >= 500:
        add_finding(
            "Error de servidor (500) ante payload de SQLi en parámetro de ruta",
            "ALTA",
            "Un error 500 puede indicar que la consulta no está parametrizada y "
            "podría filtrar detalles internos (stack trace) o ser explotable.",
            f"GET /partidos/tabla/{payload_ruta} -> status {status}, body: {text[:300]}",
        )
    else:
        print(f"[OK] /partidos/tabla/<deporte> maneja el payload de SQLi sin error "
              f"de servidor (status {status}).\n")

    # Inyección en cuerpo JSON (nombre_equipo) — debe guardarse literal, no ejecutarse
    payload_body = "'; DROP TABLE equipos; --"
    status, data, _, _ = call(
        "POST", f"{base}/equipos/",
        {"region": f"SQLiTest-{time.time_ns()}", "deporte": "PruebaSeguridad", "nombre_equipo": payload_body},
        headers={"Authorization": f"Bearer {token}"},
    )
    status_after, data_after, _, _ = call("GET", f"{base}/equipos/")
    if status_after != 200 or not isinstance(data_after, list):
        add_finding(
            "Posible ejecución de SQL arbitrario vía nombre_equipo",
            "CRITICA",
            "Tras insertar un nombre_equipo con un payload de SQLi tipo DROP TABLE, "
            "la tabla equipos dejó de responder correctamente.",
            f"POST /equipos/ status={status}; GET /equipos/ posterior: status={status_after}",
        )
    else:
        print("[OK] La tabla 'equipos' sigue intacta tras insertar un payload de "
              "SQLi como texto (se guarda literal, no se ejecuta).\n")


# ── 4. Bypass de autenticación / forjado de JWT ─────────────────────────

def check_auth_bypass(base):
    # 4a. Sin token
    status, _, _, _ = call("GET", f"{base}/auth/usuarios")
    if status != 401:
        add_finding(
            "Endpoint protegido accesible sin token",
            "CRITICA",
            "GET /auth/usuarios debería exigir autenticación.",
            f"Status obtenido sin Authorization header: {status}",
        )
    else:
        print("[OK] /auth/usuarios exige token (401 sin Authorization).\n")

    # 4b. Token con alg=none
    try:
        forged_none = jwt.encode(
            {"user_id": 1, "username": "admin", "rol": "admin"}, key=None, algorithm="none"
        )
        status, _, _, _ = call(
            "GET", f"{base}/auth/usuarios", headers={"Authorization": f"Bearer {forged_none}"}
        )
        if status == 200:
            add_finding(
                "Bypass de autenticación con JWT alg=none",
                "CRITICA",
                "El servidor acepta tokens sin firma (alg=none).",
                f"Status con token alg=none: {status}",
            )
        else:
            print(f"[OK] Token alg=none rechazado (status {status}).\n")
    except (NotImplementedError, jwt.exceptions.InvalidKeyError):
        print("[OK] La librería cliente no permite generar alg=none (protección adicional).\n")

    # 4c. Secreto por defecto hardcodeado (u22326979) — ver app/core/security.py,
    # app/.env.example, compose.yml / podman-compose.yml
    default_secret_padded = ("u22326979" * ((32 // len("u22326979")) + 1))[:32]
    for secret_label, secret in [
        ("u22326979 (crudo)", "u22326979"),
        ("u22326979 (extendido a 32 bytes, como hace get_secret_key())", default_secret_padded),
    ]:
        forged = jwt.encode(
            {
                "user_id": 9999,
                "username": "atacante",
                "rol": "admin",
                "exp": int(time.time()) + 3600,
            },
            key=secret,
            algorithm="HS256",
        )
        status, data, _, _ = call(
            "GET", f"{base}/auth/usuarios", headers={"Authorization": f"Bearer {forged}"}
        )
        if status == 200:
            add_finding(
                "Secreto de firma JWT por defecto hardcodeado y predecible",
                "CRITICA",
                "app/core/security.py usa SECRET_KEY = os.environ.get('SECRET_KEY', "
                "'u22326979') como valor por defecto, y ese mismo valor aparece "
                "hardcodeado como fallback en app/.env.example, "
                "app/.env.podman.example, compose.yml y podman-compose.yml. Si el "
                "despliegue no define explícitamente la variable de entorno "
                "SECRET_KEY, cualquiera que lea el repositorio público puede forjar "
                "un JWT válido con rol=admin y comprometer el sistema por completo.",
                f"Token forjado con secreto '{secret_label}' fue ACEPTADO por el "
                f"servidor para GET /auth/usuarios (status {status}). "
                f"Payload forjado: user_id=9999, username='atacante', rol='admin'.",
            )
            break
    else:
        print("[OK] El servidor de prueba tiene configurado un SECRET_KEY distinto "
              "al valor por defecto del repositorio (no se pudo forjar un token "
              "válido con 'u22326979'). Nota: el propio valor por defecto sigue "
              "siendo un riesgo de configuración — ver hallazgo de código fuente.\n")


# ── 5. IDOR / escalación de privilegios ─────────────────────────────────

def check_idor(base):
    viewer_token = login(base, "viewer", "viewer123")
    if not viewer_token:
        print("[AVISO] No se pudo autenticar como 'viewer' — se omite la prueba de IDOR.\n")
        return

    intentos = [
        ("POST", "/equipos/", {"region": "IDOR", "deporte": "IDOR", "nombre_equipo": "IDOR"}),
        ("GET", "/auth/usuarios", None),
        ("GET", "/auth/auditoria", None),
        ("GET", "/notificaciones/", None),
        ("DELETE", "/equipos/1", None),
    ]
    fugas = []
    for method, path, body in intentos:
        status, _, _, _ = call(method, f"{base}{path}", body, headers={"Authorization": f"Bearer {viewer_token}"})
        if status not in (401, 403, 404):
            fugas.append((method, path, status))

    if fugas:
        add_finding(
            "Endpoint privilegiado accesible con rol 'visualizador'",
            "ALTA",
            "Un usuario con el rol de menor privilegio pudo ejecutar acciones "
            "reservadas a admin/operador.",
            f"Peticiones que no fueron bloqueadas: {fugas}",
        )
    else:
        print("[OK] El rol 'visualizador' fue bloqueado correctamente en todos los "
              "endpoints privilegiados probados (401/403).\n")


# ── 6. Fuerza bruta / enumeración de usuarios ───────────────────────────

def check_brute_force(base):
    intentos = 15
    statuses = []
    start = time.perf_counter()
    for i in range(intentos):
        status, _, _, _ = call("POST", f"{base}/auth/login", {"username": "admin", "password": f"incorrecta{i}"})
        statuses.append(status)
    elapsed = time.perf_counter() - start

    if all(s == 401 for s in statuses):
        add_finding(
            "Sin protección contra fuerza bruta en /auth/login",
            "MEDIA",
            f"Se realizaron {intentos} intentos de login fallidos consecutivos "
            f"contra el mismo usuario en {elapsed:.2f}s sin ningún bloqueo, "
            "CAPTCHA, backoff ni rate-limiting. Un atacante puede probar "
            "contraseñas indefinidamente (mitigado parcialmente por el costo de "
            "bcrypt, ver informe de rendimiento, pero no es una defensa dedicada).",
            f"{intentos} intentos en {elapsed:.2f}s, todos devolvieron 401 sin "
            f"bloqueo ni degradación de servicio.",
        )
    else:
        print(f"[INFO] Respuestas variadas durante fuerza bruta: {set(statuses)}\n")

    # Enumeración de usuarios por temporización (usuario válido vs inválido)
    _, _, _, t_valido = call("POST", f"{base}/auth/login", {"username": "admin", "password": "incorrecta"})
    _, _, _, t_invalido = call("POST", f"{base}/auth/login", {"username": "no_existe_e2e", "password": "incorrecta"})
    diferencia = t_valido - t_invalido
    if diferencia > 150:
        add_finding(
            "Posible enumeración de usuarios por canal lateral de tiempo",
            "BAJA",
            "El login responde notablemente más lento cuando el usuario existe "
            "(se calcula bcrypt) que cuando no existe (falla antes, sin bcrypt), "
            "lo que permite inferir qué usernames son válidos aunque el mensaje "
            "de error sea idéntico ('Credenciales inválidas' en ambos casos).",
            f"Latencia con usuario válido: {t_valido:.1f} ms. "
            f"Latencia con usuario inexistente: {t_invalido:.1f} ms. "
            f"Diferencia: {diferencia:.1f} ms.",
        )
    else:
        print(f"[OK] Diferencia de tiempos entre usuario válido/ inválido no es "
              f"significativa ({diferencia:.1f} ms).\n")


def main():
    parser = argparse.ArgumentParser(description="Pruebas de seguridad - Olimpiadas Perú")
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    token = login(base, "admin", "admin123")
    if not token:
        print(f"No se pudo autenticar contra {base}. ¿Está el servidor corriendo con los usuarios semilla?")
        return

    print("=== 1. Cabeceras de seguridad ===")
    check_security_headers(base)

    print("=== 2. CORS ===")
    check_cors(base)

    print("=== 3. Inyección SQL ===")
    check_sql_injection(base, token)

    print("=== 4. Bypass de autenticación / JWT ===")
    check_auth_bypass(base)

    print("=== 5. IDOR / escalación de privilegios ===")
    check_idor(base)

    print("=== 6. Fuerza bruta / enumeración de usuarios ===")
    check_brute_force(base)

    print(f"\nTotal de hallazgos: {len(FINDINGS)}")
    for f in FINDINGS:
        print(f" - [{f['severidad']}] {f['titulo']}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(FINDINGS, fh, ensure_ascii=False, indent=2)
        print(f"\nHallazgos guardados en {args.output}")


if __name__ == "__main__":
    main()
