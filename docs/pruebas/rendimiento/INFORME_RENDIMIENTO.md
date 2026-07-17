# Informe de pruebas de rendimiento — Sistema Olimpiadas Perú

## 1. Herramienta utilizada

La consigna pide "JMeter u otra herramienta". Apache JMeter no está disponible en este
entorno (requiere descarga manual de ~70 MB y no hay razón para bloquear la entrega por
eso). Java sí está instalado (OpenJDK 25), pero se optó por un script propio en Python
(`load_test.py`), usando únicamente la librería estándar (`concurrent.futures` +
`urllib`), para no depender de instalar herramientas adicionales ni paquetes externos.
El script es reproducible con un solo comando y no requiere red ni licencias.

Código: [`load_test.py`](./load_test.py).

## 2. Entorno de la prueba

- Máquina: 12 CPUs lógicas, Linux.
- Python 3.14.5, SQLite 3.50.2.
- Servidor: **servidor de desarrollo de Flask/Werkzeug** (`python app.py`), un solo
  proceso, `threaded=False` (configuración por defecto del proyecto — ver
  `app/app.py`). **Esto es una limitación intencional documentada**: en producción el
  proyecto usa `gunicorn --workers 2` (ver `Containerfile`), que sí atiende peticiones
  en paralelo entre procesos. Los números de este informe son por lo tanto una **cota
  inferior conservadora** del rendimiento real; una repetición de esta prueba contra
  gunicorn debería mostrar mejor throughput en los escenarios de lectura y escritura
  (no en el login, cuyo costo es CPU-bound por bcrypt y escala con núcleos, no con
  threads de un solo proceso Python por el GIL).
- Base de datos: SQLite vacía, poblada solo con el usuario `admin` semilla (sin datos
  de negocio previos, para no sesgar los tiempos de consulta).

## 3. Metodología

Tres escenarios, cada uno con **20 "usuarios" concurrentes** (hilos cliente):

- **A — Lecturas públicas** (20 peticiones/usuario = 400 total): GET aleatorio entre
  `/partidos/tabla/<deporte>`, `/reportes/estadisticas/<deporte>` y `/equipos/`.
- **B — Login concurrente** (10 peticiones/usuario = 200 total): POST
  `/auth/login` con credenciales válidas, para medir el costo real de `bcrypt.checkpw`
  bajo concurrencia.
- **C — Escrituras concurrentes** (5 peticiones/usuario = 100 total): POST
  `/equipos/` con una región distinta por petición (evita conflictos de negocio 409;
  aísla la contención de escritura de SQLite).

Comando ejecutado:
```bash
python load_test.py --base-url http://127.0.0.1:5000 --users 20 --requests 20
```

## 4. Resultados

| Escenario | Peticiones | Errores | Rendimiento (req/s) | Latencia media | p50 | p95 | p99 | Máx |
|---|---|---|---|---|---|---|---|---|
| A — Lecturas públicas | 400 | 0 | 1267.72 | 14.9 ms | 13.6 ms | 22.2 ms | 31.3 ms | 84.4 ms |
| B — Login (bcrypt) | 200 | 0 | 43.45 | 448.9 ms | 438.0 ms | 682.4 ms | 916.7 ms | 1044.3 ms |
| C — Escrituras (SQLite) | 100 | 0 | 227.69 | 48.1 ms | 21.0 ms | 185.5 ms | 337.2 ms | 435.7 ms |

(0 errores en los tres escenarios: no hubo caídas ni timeouts bajo esta carga.)

## 5. Análisis

- **El login es, por mucho, el endpoint más lento** (p50 438 ms vs. 13.6 ms en lecturas
  simples — más de 30x). Esto es **esperado y correcto**: `bcrypt` está diseñado para
  ser computacionalmente costoso y así resistir ataques de fuerza bruta offline sobre
  hashes filtrados. No es un bug, es el trade-off de seguridad de bcrypt. Con 20 logins
  concurrentes en un solo proceso Python, el costo se serializa por el GIL (bcrypt en
  este paquete libera el GIL durante el cálculo nativo en C, por lo que sí hay algo de
  paralelismo real entre hilos, pero limitado por los núcleos disponibles al proceso).
- **Las lecturas públicas son rápidas y estables** (p99 de solo 31 ms), consistente con
  consultas SQLite simples sobre una base de datos pequeña sin índices adicionales
  necesarios a este volumen de datos.
- **Las escrituras muestran una cola larga**: la mediana (21 ms) es baja, pero p95/p99
  se disparan a 185–337 ms. Esto es consistente con el modo de bloqueo por defecto de
  SQLite (`journal_mode` no configurado explícitamente a WAL en `database.py`): cuando
  varias escrituras concurrentes compiten, todas menos una esperan a que la conexión
  activa libere el lock exclusivo. Con más concurrencia o partidos/resultados
  simultáneos, esta cola de espera crecería.

## 6. Recomendaciones

1. **No es necesario optimizar el login** — la lentitud es deliberada (seguridad). Si
   en el futuro se vuelve un cuello de botella real bajo tráfico legítimo alto, la vía
   correcta es escalar horizontalmente (más workers de gunicorn), no bajar el costo de
   bcrypt.
2. **Activar `PRAGMA journal_mode=WAL`** en `database.py` reduciría la contención de
   escritura observada en el Escenario C, permitiendo lecturas concurrentes mientras
   hay una escritura en curso (SQLite en modo WAL no bloquea lectores contra un
   escritor). Es un cambio de una línea con beneficio medible.
3. **Repetir esta prueba contra `gunicorn --workers 2`** (el servidor real de
   producción, ver `Containerfile`) antes de sacar conclusiones definitivas de
   capacidad — el servidor de desarrollo de Flask usado aquí subestima el throughput
   real de lecturas y escrituras.
4. Con el volumen actual (proyecto académico, decenas de equipos/partidos), el
   rendimiento medido es más que suficiente; estas recomendaciones son para cuando el
   volumen de datos o usuarios concurrentes crezca significativamente.

## 7. Cómo reproducir

```bash
cd app
python app.py   # o gunicorn --workers 2 --bind 0.0.0.0:5000 "app:create_app()"

# en otra terminal
cd docs/pruebas/rendimiento
python load_test.py --base-url http://127.0.0.1:5000 --users 20 --requests 20
```
