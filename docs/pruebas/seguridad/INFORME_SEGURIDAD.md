# Informe de pruebas de seguridad — Sistema Olimpiadas Perú

## 1. Herramienta utilizada

La consigna pide "OWASP ZAP u otra herramienta". ZAP no está disponible en este
entorno. Se optó por un script propio (`security_test.py`) usando la librería
estándar de Python más `PyJWT` (ya es dependencia del proyecto), dirigido a las
categorías de riesgo más relevantes para una API REST con autenticación JWT:
inyección SQL, bypass de autenticación / forjado de tokens, IDOR y escalación de
privilegios, cabeceras de seguridad HTTP, configuración CORS, y fuerza bruta /
enumeración de usuarios. No es un escáner automatizado exhaustivo como ZAP, pero
cada hallazgo aquí reportado es real y reproducible — no hay hallazgos fabricados.

Código: [`security_test.py`](./security_test.py). Resultados crudos:
[`resultados_antes_del_fix.json`](./resultados_antes_del_fix.json) y
[`resultados_despues_del_fix.json`](./resultados_despues_del_fix.json).

## 2. Resumen ejecutivo

Se ejecutó la prueba dos veces: **antes** y **después** de corregir el hallazgo
crítico encontrado en la primera corrida. Resultado:

| # | Hallazgo | Severidad | Estado |
|---|---|---|---|
| 1 | Secreto de firma JWT por defecto hardcodeado y predecible | **CRÍTICA** | **Corregido en esta entrega** |
| 2 | Sin cabeceras de seguridad HTTP (X-Frame-Options, CSP, HSTS, X-Content-Type-Options) | MEDIA | Abierto (recomendación en §5) |
| 3 | CORS sin restricción de origen | MEDIA | Abierto (recomendación en §5) |
| 4 | Sin protección contra fuerza bruta en `/auth/login` | MEDIA | Abierto (recomendación en §5) |
| 5 | Posible enumeración de usuarios por canal lateral de tiempo | BAJA | Abierto (recomendación en §5) |

Se probó explícitamente inyección SQL (login, parámetro de ruta, cuerpo JSON),
bypass de autenticación sin token y con JWT `alg=none`, e IDOR/escalación de
privilegios con el rol de menor permiso (`visualizador`) — **ninguno de estos
resultó explotable**: las consultas parametrizadas de `sqlite3` y los decoradores
`roles_required` / validaciones en la capa de servicio funcionan correctamente.

## 3. Hallazgo crítico (corregido)

### Secreto de firma JWT por defecto hardcodeado y predecible

`app/core/security.py` definía `SECRET_KEY = os.environ.get("SECRET_KEY",
"u22326979")`. El mismo valor `u22326979` estaba además hardcodeado como *fallback*
en `app/.env.example`, `app/.env.podman.example`, `compose.yml` y
`podman-compose.yml`. Cualquiera que leyera el repositorio (público en GitHub)
conocía ese valor.

**Prueba de concepto (antes del fix):** con el servidor corriendo sin la variable
de entorno `SECRET_KEY` definida (el caso por defecto de `python app.py` en
desarrollo, y el caso de cualquier despliegue que olvide configurarla), se forjó
localmente un JWT con `PyJWT` firmado con el secreto `u22326979` (extendido a 32
bytes igual que hace `get_secret_key()`), con payload `{"rol": "admin", "username":
"atacante", "user_id": 9999}`. El servidor lo aceptó como válido:

```
GET /auth/usuarios  con  Authorization: Bearer <token forjado>  →  200 OK
```

Esto equivale a **acceso administrativo completo sin credenciales**, para
cualquier despliegue que no sobrescriba `SECRET_KEY`.

**Corrección aplicada** (`app/core/security.py`): se eliminó el valor por defecto
hardcodeado. Si `SECRET_KEY` no está definida en el entorno, la aplicación ahora
genera una clave aleatoria de 32 bytes (`secrets.token_hex(32)`) al arrancar, con
un aviso impreso en consola. Esto invalida sesiones anteriores al reiniciar el
proceso (comportamiento seguro por defecto) en vez de usar un secreto conocido.
También se limpiaron los archivos de configuración (`.env.example`,
`.env.podman.example`, `compose.yml`, `podman-compose.yml`) para que ya no
propaguen `u22326979` como valor por defecto; los `compose.yml` ahora **exigen**
que `SECRET_KEY` esté definida (`${SECRET_KEY:?...}`) antes de levantar el
contenedor de producción.

**Verificación tras el fix:** se repitió exactamente la misma prueba de forjado
contra un servidor reiniciado (de nuevo sin `SECRET_KEY` en el entorno, para
probar el peor caso). El token forjado con `u22326979` ahora es **rechazado**
(401) porque el servidor generó una clave aleatoria distinta al arrancar. Ver
`resultados_despues_del_fix.json` — el hallazgo crítico ya no aparece en la lista.

## 4. Hallazgos abiertos (detalle)

### 4.1 Sin cabeceras de seguridad HTTP — MEDIA
Faltan `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy` y
`Strict-Transport-Security` en las respuestas. Riesgo moderado porque la API es
consumida principalmente por el frontend servido desde el mismo origen, pero
conviene añadirlas para defensa en profundidad.

### 4.2 CORS sin restricción de origen — MEDIA
`CORS(app)` en `app/app.py` no restringe orígenes: un `Origin` arbitrario
(`https://sitio-atacante-e2e.example` en la prueba) recibe
`Access-Control-Allow-Origin` reflejando ese mismo origen. Cualquier sitio web
puede hacer peticiones a la API desde el navegador de un usuario autenticado.

### 4.3 Sin protección contra fuerza bruta en `/auth/login` — MEDIA
15 intentos de login fallidos consecutivos contra `admin` en 2.8 s, todos
respondidos con 401 sin bloqueo, backoff ni CAPTCHA. El costo de `bcrypt`
(~185 ms/intento, ver informe de rendimiento) hace la fuerza bruta más lenta que
en un hash rápido, pero no es una mitigación dedicada.

### 4.4 Enumeración de usuarios por canal lateral de tiempo — BAJA
Un login con usuario existente y contraseña incorrecta tarda ~190 ms (se ejecuta
`bcrypt.checkpw`); un login con usuario inexistente tarda ~2 ms (falla antes,
sin bcrypt). El mensaje de error es idéntico en ambos casos
("Credenciales inválidas"), pero la diferencia de tiempo permite inferir qué
nombres de usuario existen.

## 5. Recomendaciones

1. ~~Eliminar el secreto JWT por defecto hardcodeado.~~ **Hecho en esta entrega.**
2. Añadir cabeceras de seguridad, por ejemplo con `flask-talisman` o un
   `after_request` que las agregue manualmente (2–3 líneas por cabecera).
3. Restringir CORS a los orígenes reales del frontend en producción:
   `CORS(app, origins=["https://dominio-real"])` en vez de `CORS(app)` sin
   argumentos.
4. Agregar rate-limiting a `/auth/login` (p. ej. `flask-limiter`, N intentos por
   IP/usuario por minuto) para tener una defensa dedicada además del costo de
   bcrypt.
5. Para cerrar la enumeración por tiempo, se podría ejecutar un `bcrypt.checkpw`
   contra un hash dummy cuando el usuario no existe, igualando el tiempo de
   respuesta en ambos casos. Prioridad baja — el mensaje de error ya no filtra
   esta información directamente, solo el tiempo de respuesta.

## 6. Cómo reproducir

```bash
cd app
python app.py   # SECRET_KEY sin definir = peor caso (ya no es explotable tras el fix)

# en otra terminal
cd docs/pruebas/seguridad
python security_test.py --base-url http://127.0.0.1:5000
```
