# Plan de Despliegue — Sistema Olimpiadas Perú

Guía paso a paso para desplegar el sistema en una máquina nueva, desde cero. Cubre
dos rutas: **entorno virtual (venv)** para desarrollo/pruebas locales, y
**Podman** (contenedorizado) para un despliegue reproducible tipo producción.

## 1. Requisitos previos

| Componente | Versión mínima | Verificar con |
|---|---|---|
| Python | 3.10+ | `python3 --version` |
| pip | cualquiera reciente | `pip --version` |
| Podman (solo ruta contenedorizada) | 4.x+ | `podman --version` |
| podman-compose (opcional, ruta contenedorizada) | cualquiera reciente | `podman-compose --version` |
| Git | cualquiera reciente | `git --version` |

No se requiere un servidor de base de datos: el sistema usa SQLite embebido, sin
proceso ni servicio externo que instalar.

## 2. Obtener el código

```bash
git clone https://github.com/DanielLazaro1555/Proyecto-Olimpiadas.git
cd Proyecto-Olimpiadas
```

## 3. Variables de entorno

| Variable | Obligatoria | Descripción | Notas |
|---|---|---|---|
| `SECRET_KEY` | **Sí, en producción** | Clave para firmar los JWT | Si no se define, la app genera una clave aleatoria por proceso al arrancar (las sesiones no sobreviven a un reinicio) — ver `app/core/security.py`. **No** existe un valor por defecto hardcodeado; nunca reutilizar un valor de ejemplo. Generar con: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | No | `development` \| `production` | Informativo, no cambia comportamiento crítico de Flask 3.x |
| `FLASK_DEBUG` | No | `true` \| `false` (default `false`) | **Nunca `true` en producción** (expone el debugger interactivo de Werkzeug) |
| `PORT` | No | Puerto HTTP (default `5000`) | |
| `DATABASE_PATH` | No | Ruta del archivo SQLite (default `olimpiadas.db` local, `/data/olimpiadas.db` en contenedor) | |
| `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`, `SMTP_PORT` | No | Envío real de notificaciones por correo | Si no se configuran, las notificaciones se registran igual con estado `simulado` (ver `app/core/services/notification_service.py`) — no rompe el flujo |
| `NOTIFY_EMAIL` | No | Destinatario de las notificaciones internas | Default `admin@olimpiadasperu.local` |

## 4. Ruta A — Entorno virtual (venv)

Recomendada para desarrollo local o para correr la app sin Podman.

```bash
# 1. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r app/requirements.txt

# 3. Definir SECRET_KEY (recomendado incluso en local, para no perder sesión al reiniciar)
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 4. Arrancar la aplicación
cd app
python app.py
```

La aplicación queda disponible en `http://127.0.0.1:5000`. La base de datos
`olimpiadas.db` se inicializa automáticamente en el primer arranque, con las
tablas necesarias y los tres usuarios semilla (`admin`/`admin123`,
`operador`/`operador123`, `viewer`/`viewer123`).

Para producción real con este método (sin contenedor), usar `gunicorn` en vez del
servidor de desarrollo de Flask:

```bash
gunicorn --chdir app --bind 0.0.0.0:5000 --workers 2 --timeout 120 "app:create_app()"
```

## 5. Ruta B — Podman (contenedorizado)

Recomendada para un despliegue reproducible, aislado del sistema anfitrión.

### 5.1 Con `podman-compose` (más simple)

```bash
# 1. Crear archivo de entorno para el contenedor
cp app/.env.podman.example app/.env

# 2. Editar app/.env y definir un SECRET_KEY real (no dejarlo vacío en producción)
python -c "import secrets; print(secrets.token_hex(32))"
#   copiar el resultado como valor de SECRET_KEY en app/.env

# 3. Construir e iniciar
podman-compose up --build -d

# 4. Verificar que levantó
podman-compose ps
```

La aplicación queda disponible en `http://127.0.0.1:5000`. La base de datos
persiste en el volumen `olimpiadas_data`, sobrevive a reinicios y recreaciones
del contenedor.

`compose.yml` y `podman-compose.yml` exigen `SECRET_KEY` explícitamente
(`${SECRET_KEY:?...}`) — si no está definida, `podman-compose up` falla con un
mensaje claro en vez de arrancar con un valor inseguro.

Detener:

```bash
podman-compose down
```

### 5.2 Con `podman` directo (sin compose)

```bash
# 1. Construir la imagen
podman build -t localhost/proyecto-olimpiadas:latest -f Containerfile .

# 2. Crear el volumen persistente (una sola vez)
podman volume create olimpiadas_data

# 3. Generar y exportar un SECRET_KEY
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 4. Ejecutar el contenedor
podman run -d \
  --name proyecto-olimpiadas-app \
  -p 5000:5000 \
  -e SECRET_KEY="$SECRET_KEY" \
  -e DATABASE_PATH=/data/olimpiadas.db \
  -v olimpiadas_data:/data:Z \
  localhost/proyecto-olimpiadas:latest
```

Ver logs: `podman logs -f proyecto-olimpiadas-app`
Detener: `podman stop proyecto-olimpiadas-app && podman rm proyecto-olimpiadas-app`

## 6. Verificación post-despliegue

Tras arrancar (por cualquiera de las dos rutas), confirmar que el sistema quedó
operativo:

```bash
# 1. El catálogo de servicios responde (endpoint público, sin auth)
curl -s http://127.0.0.1:5000/catalog/ | head -c 200

# 2. La documentación interactiva carga
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/docs
# Esperado: 200

# 3. Login con el usuario admin semilla funciona
curl -s -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# Esperado: {"token": "...", "username": "admin", "rol": "admin"}

# 4. La tabla de posiciones (endpoint con lógica de negocio) responde sin error
curl -s http://127.0.0.1:5000/partidos/tabla/F%C3%BAtbol
# Esperado: [] (array vacío en una instalación nueva) o la tabla real
```

Si los cuatro pasos responden como se indica, el despliegue es correcto.

### 6.1 Correr la suite de pruebas contra el despliegue

```bash
# Entorno venv
cd Proyecto-Olimpiadas
source venv/bin/activate
python -m pytest tests/ -q

# Entorno Podman (dentro de la imagen, sin afectar el contenedor en ejecución)
podman run --rm \
  -v "$(pwd)":/workspace:Z \
  -w /workspace \
  localhost/proyecto-olimpiadas:latest \
  python -m pytest tests/ -q
```

Se espera `21 passed`.

## 7. Actualizar un despliegue existente

```bash
git pull
# Ruta venv:
pip install -r app/requirements.txt   # por si hay dependencias nuevas
# Ruta Podman:
podman-compose up --build -d          # reconstruye la imagen y recrea el contenedor
```

La base de datos SQLite no se pierde en ninguna ruta: en venv es un archivo en
disco (`app/olimpiadas.db` o el que indique `DATABASE_PATH`); en Podman vive en
el volumen `olimpiadas_data`, independiente del ciclo de vida del contenedor.

## 8. Copia de seguridad de la base de datos

```bash
# Ruta venv
cp app/olimpiadas.db app/olimpiadas.db.bak-$(date +%Y%m%d)

# Ruta Podman
podman run --rm -v olimpiadas_data:/data:Z -v "$(pwd)":/backup:Z \
  localhost/proyecto-olimpiadas:latest \
  cp /data/olimpiadas.db /backup/olimpiadas.db.bak-$(date +%Y%m%d)
```

## 9. Rollback

Si un despliegue nuevo falla la verificación del §6:

```bash
# Ruta Podman: volver a la imagen anterior (si se etiquetó) o reconstruir
# desde un commit anterior conocido-bueno
git checkout <commit-anterior>
podman-compose up --build -d

# Restaurar la base de datos desde el backup más reciente si además se
# corrompió algo en la BD (poco común, ya que las migraciones son aditivas)
```

## 10. Notas de seguridad para producción

Ver también `docs/pruebas/seguridad/INFORME_SEGURIDAD.md` para el detalle
completo. Puntos que aplican directamente al despliegue:

- **`SECRET_KEY` siempre definida y secreta** en producción — no reutilizar el
  valor de ningún archivo `.env.example` del repositorio (son solo plantillas).
- **`FLASK_DEBUG=false`** siempre en producción.
- Servir detrás de un proxy TLS (nginx, Caddy, etc.) si se expone a Internet —
  este proyecto no implementa TLS propio; `gunicorn`/Flask sirven HTTP plano.
- Restringir el origen CORS (`app/app.py`, `CORS(app)`) a los dominios reales
  del frontend antes de exponer la API públicamente (hallazgo abierto, ver
  informe de seguridad).
