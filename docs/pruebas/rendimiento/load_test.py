#!/usr/bin/env python3
"""Prueba de carga para el Sistema Olimpiadas Perú.

Alternativa a Apache JMeter (no disponible en este entorno) usando solo la
librería estándar de Python: hilos concurrentes + urllib. No requiere
instalar dependencias adicionales.

Uso:
    python load_test.py --base-url http://127.0.0.1:5000 --users 20 --requests 20

Escenarios ejecutados:
    A. Lecturas públicas concurrentes (tabla, estadísticas, equipos)
    B. Login concurrente (POST /auth/login, costo real de bcrypt)
    C. Escrituras concurrentes (POST /equipos/, contención de SQLite)
"""
import argparse
import concurrent.futures
import json
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request


def timed_request(method, url, body=None, token=None, timeout=15):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            res.read()
            status = res.status
    except urllib.error.HTTPError as err:
        err.read()
        status = err.code
    except Exception:
        status = 0
    elapsed_ms = (time.perf_counter() - start) * 1000
    return status, elapsed_ms


def percentile(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (pct / 100)
    f, c = int(k), min(int(k) + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def run_scenario(name, task_fn, users, requests_per_user):
    latencies = []
    statuses = []
    start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=users) as pool:
        futures = [
            pool.submit(task_fn, u, r)
            for u in range(users)
            for r in range(requests_per_user)
        ]
        for fut in concurrent.futures.as_completed(futures):
            status, elapsed_ms = fut.result()
            statuses.append(status)
            latencies.append(elapsed_ms)

    total_time = time.perf_counter() - start
    total = len(latencies)
    ok = sum(1 for s in statuses if 200 <= s < 300)
    errors = total - ok

    print(f"\n=== Escenario {name} ===")
    print(f"Total peticiones : {total}")
    print(f"Exitosas (2xx)   : {ok}")
    print(f"Errores          : {errors}")
    print(f"Tiempo total     : {total_time:.2f} s")
    print(f"Throughput       : {total / total_time:.2f} req/s")
    print(f"Latencia media   : {statistics.mean(latencies):.1f} ms")
    print(f"Latencia p50     : {percentile(latencies, 50):.1f} ms")
    print(f"Latencia p95     : {percentile(latencies, 95):.1f} ms")
    print(f"Latencia p99     : {percentile(latencies, 99):.1f} ms")
    print(f"Latencia máxima  : {max(latencies):.1f} ms")

    return {
        "escenario": name,
        "total": total,
        "exitosas": ok,
        "errores": errors,
        "tiempo_total_s": round(total_time, 3),
        "throughput_req_s": round(total / total_time, 2),
        "latencia_media_ms": round(statistics.mean(latencies), 1),
        "latencia_p50_ms": round(percentile(latencies, 50), 1),
        "latencia_p95_ms": round(percentile(latencies, 95), 1),
        "latencia_p99_ms": round(percentile(latencies, 99), 1),
        "latencia_max_ms": round(max(latencies), 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Prueba de carga - Olimpiadas Perú")
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--users", type=int, default=20, help="Usuarios concurrentes")
    parser.add_argument("--requests", type=int, default=20, help="Peticiones por usuario")
    parser.add_argument("--deporte", default="Fútbol")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin123")
    parser.add_argument("--output", default=None, help="Ruta JSON de salida (opcional)")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    deporte = urllib.parse.quote(args.deporte)

    # Token para escenarios que requieren autenticación
    status, _ = timed_request("GET", f"{base}/equipos/")
    if status == 0:
        print(f"No se pudo conectar a {base}. ¿Está corriendo el servidor?")
        return

    req = urllib.request.Request(
        f"{base}/auth/login",
        data=json.dumps({"username": args.username, "password": args.password}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        token = json.loads(res.read())["token"]

    resultados = []

    # Escenario A: lecturas públicas concurrentes
    def lectura(u, r):
        endpoints = [
            f"{base}/partidos/tabla/{deporte}",
            f"{base}/reportes/estadisticas/{deporte}",
            f"{base}/equipos/",
        ]
        return timed_request("GET", endpoints[(u + r) % len(endpoints)])

    resultados.append(run_scenario("A - Lecturas públicas", lectura, args.users, args.requests))

    # Escenario B: login concurrente (costo real de bcrypt)
    def login(u, r):
        return timed_request(
            "POST", f"{base}/auth/login", {"username": args.username, "password": args.password}
        )

    resultados.append(run_scenario("B - Login concurrente (bcrypt)", login, args.users, max(1, args.requests // 2)))

    # Escenario C: escrituras concurrentes (contención SQLite)
    def escritura(u, r):
        region = f"CargaTest-{u}-{r}-{time.time_ns()}"
        return timed_request(
            "POST",
            f"{base}/equipos/",
            {"region": region, "deporte": "CargaSintetica", "nombre_equipo": f"Equipo {region}"},
            token=token,
        )

    resultados.append(run_scenario("C - Escrituras concurrentes (SQLite)", escritura, args.users, max(1, args.requests // 4)))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"\nResultados guardados en {args.output}")


if __name__ == "__main__":
    main()
