# Sistema Olimpiadas Perú — SOA

**Universidad Tecnológica del Perú · Facultad de Ingeniería**  
**Asignatura:** Arquitectura Orientada al Servicio (100000SI84) · Sección 35875  
**Docente:** Ing. Kelvin Macedo Ylachoque  
**Estudiante:** Huamán Lázaro, Daniel Esteban · U22326979  
**Año:** 2026

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Problemática](#problemática)
- [Solución propuesta](#solución-propuesta)
- [Arquitectura de servicios](#arquitectura-de-servicios)
- [Análisis de Arquitectura Hexagonal](#análisis-de-arquitectura-hexagonal)
- [Procesos BPMN](#procesos-bpmn)
- [Tecnologías](#tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Cómo ejecutar](#cómo-ejecutar)
- [Endpoints REST](#endpoints-rest)
- [Planificación](#planificación)
- [Plan APF3](#plan-apf3-semana-15)
- [Referencias](#referencias)

---

## Descripción

Sistema de gestión de eventos deportivos basado en **Arquitectura Orientada a Servicios (SOA)**. Modulariza los procesos críticos de las **Olimpiadas Perú** —competencia deportiva **interna a nivel nacional**— en servicios independientes y reutilizables, expuestos mediante APIs RESTful y consumidos por un cliente web.

Cada equipo representa una de las **25 regiones del Perú** (Amazonas, Áncash, Arequipa, Lima, etc.). No es una competencia internacional; los participantes son delegaciones regionales peruanas.

Los cuatro deportes obligatorios son:

| Deporte | Categoría |
|---------|-----------|
| Fútbol | Varones |
| Básquet | Varones |
| Vóley | Damas |
| Ping-Pong | Mixto |

## Problemática

La gestión tradicional de eventos deportivos a gran escala depende de procesos manuales o herramientas desconectadas, lo que genera:

- Silos de información y redundancia de datos
- Errores en la asignación de horarios y fixture
- Alta dificultad para escalar a nuevas disciplinas o instituciones
- Falta de transparencia en resultados y tablas de posiciones
- Sin control de acceso diferenciado por rol de usuario

## Solución propuesta

Sistema *API-first* basado en SOA que desacopla la lógica de negocio en cuatro servicios independientes con contratos de interfaz claros. Cada servicio evoluciona de forma autónoma sin afectar al sistema completo. Incluye autenticación JWT con tres roles (admin / operador / visualizador) para control de acceso diferenciado.

---

## Arquitectura de servicios

### Servicio de Autenticación (`/auth`)
Gestiona el acceso al sistema mediante JWT y bcrypt.

| Operación | Descripción |
|---|---|
| `login(username, password)` | Autentica al usuario y retorna token JWT |
| `registrarUsuario(username, password, rol)` | Crea una cuenta nueva (solo admin) |
| `listarUsuarios()` | Lista todos los usuarios del sistema (solo admin) |
| `eliminarUsuario(id)` | Elimina un usuario (solo admin, no puede autoeliminar) |

### Servicio de Equipos (`/equipos`)
Gestiona los equipos participantes.

| Operación | Descripción |
|---|---|
| `registrarEquipo(region, deporte, nombreEquipo)` | Registra un equipo con validación de unicidad por región (solo admin/operador) |
| `consultarEquipos()` | Devuelve el listado completo de equipos |
| `eliminarEquipo(idEquipo)` | Elimina un equipo si no tiene partidos asignados (solo admin/operador) |

### Servicio de Deportistas (`/deportistas`)
Administra la inscripción de deportistas en equipos.

| Operación | Descripción |
|---|---|
| `inscribirDeportista(idEquipo, datos)` | Inscribe un deportista validando duplicados (solo admin/operador) |
| `listarDeportistasPorEquipo(idEquipo)` | Lista los deportistas de un equipo |

### Servicio de Partidos (`/partidos`)
Gestiona resultados y tabla de posiciones.

| Operación | Descripción |
|---|---|
| `registrarResultado(idPartido, golesLocal, golesVisitante)` | Registra resultado (no sobrescribible, solo admin/operador) |
| `consultarTablaPosiciones(deporte)` | Calcula y devuelve la tabla de posiciones por deporte |

### Servicio de Fixture (`/fixture`)
Genera el calendario de enfrentamientos aleatorios.

| Operación | Descripción |
|---|---|
| `generarFixture(deporte)` | Crea emparejamientos aleatorios con fechas (mínimo 2 equipos, solo admin/operador) |
| `consultarFixture(deporte)` | Devuelve el calendario de partidos por deporte |

---

## Análisis de Arquitectura Hexagonal

> **Contexto (Semana 9 — Tema del sílabo):** ¿El prototipo usa o puede usar arquitectura hexagonal? ¿Genera valor?

### ¿Qué es la Arquitectura Hexagonal?

La arquitectura hexagonal (Ports & Adapters, propuesta por Alistair Cockburn) separa el sistema en tres zonas:

- **Core / Dominio:** lógica de negocio pura, sin dependencias de infraestructura.
- **Puertos:** interfaces que definen cómo el core se comunica hacia afuera.
- **Adaptadores:** implementaciones concretas de esos puertos (HTTP, base de datos, etc.).

### ¿El prototipo la usa actualmente?

**Parcialmente.** La estructura actual presenta una separación por capas que se acerca al modelo hexagonal:

| Componente actual | Rol en arquitectura hexagonal |
|---|---|
| `app.py` | Punto de entrada / adaptador de arranque |
| Blueprints Flask (`equipos.py`, etc.) | Adaptadores HTTP (entrada) |
| `database.py` | Adaptador de persistencia (salida) |
| Lógica dentro de cada blueprint | Core (pero mezclada con Flask) |

El principal punto de mejora es que la **lógica de negocio está acoplada al framework Flask** dentro de los mismos archivos de rutas. En una arquitectura hexagonal pura, el core no debería importar `Flask`, `request` ni `jsonify`.

### ¿Puede adoptarla?

Sí. La refactorización consistiría en:

```
app/
├── core/                    # Lógica de negocio pura (sin Flask, sin SQLite)
│   ├── equipos_service.py
│   ├── fixture_service.py
│   └── partidos_service.py
├── adaptadores/
│   ├── http/                # Blueprints Flask (adaptadores de entrada)
│   └── db/                  # Acceso a SQLite (adaptadores de salida)
└── puertos/
    └── interfaces.py        # Clases abstractas / protocolos Python
```

### ¿Genera valor para este proyecto?

| Beneficio | Aplica al proyecto |
|---|---|
| Cambiar SQLite por PostgreSQL sin tocar el core | ✅ Sí — relevante si escala |
| Probar la lógica sin levantar Flask ni BD | ✅ Sí — facilita pruebas unitarias |
| Cambiar de REST a GraphQL o gRPC | ✅ Sí — sin reescribir reglas de negocio |
| Justifica la complejidad para un sistema de esta escala | ⚠ Parcialmente — para producción sí, para prototipo académico agrega overhead |

**Conclusión:** La arquitectura hexagonal *puede* adoptarse y *generaría valor real* si el sistema fuera a producción o se integrara con sistemas externos. Para el prototipo académico actual, la separación por capas implementada es suficiente y mantiene los principios SOA (encapsulamiento, contratos claros, independencia de servicios). Se aplicará progresivamente en las semanas 11–15 como parte de la mejora continua del proyecto.

---

## Procesos BPMN

Los flujos de negocio están modelados en cuatro diagramas ubicados en `docs/bpmn/`:

| Diagrama | Descripción |
|---|---|
| [Registrar equipo](docs/bpmn/Diagrama_1_Registrar_equipo.png) | Valida unicidad por región y deporte antes de guardar |
| [Inscribir deportista](docs/bpmn/Diagrama_2_Inscribir_deportista.png) | Valida que el deportista no esté ya inscrito |
| [Registrar resultado](docs/bpmn/Diagrama_3_Registrar_resultado.png) | Solo permite registrar si el partido no tiene resultado previo |
| [Generar fixture](docs/bpmn/Diagrama_4_Generar_fixture_simple.png) | Solo genera si hay al menos 2 equipos en el deporte |

---

## Tecnologías

| Capa | Tecnología | Justificación |
|---|---|---|
| Lenguaje backend | Python 3 | Sintaxis clara, gran ecosistema para APIs |
| Framework API | Flask + Flask-CORS | Ligero, ideal para SOA con blueprints modulares |
| Autenticación | PyJWT + bcrypt | JWT stateless para APIs REST, bcrypt para hash seguro de contraseñas |
| Base de datos | SQLite (`olimpiadas.db`) | Sin servidor, fácil despliegue académico |
| Frontend | HTML5 + Tailwind CSS + JavaScript (ES Modules) | UI responsiva sin build tools, módulos JS por servicio |
| Control de versiones | Git + GitHub | Historial de commits, colaboración y entrega |
| Entorno | venv (entorno virtual Python) | Aislamiento de dependencias |

---

## Estructura del proyecto

```
Proyecto-Olimpiadas/
├── README.md
├── .gitignore
├── app/                            # Aplicación Flask
│   ├── app.py                      # Entry point — registra todos los blueprints
│   ├── auth.py                     # Servicio de autenticación (JWT + bcrypt)
│   ├── database.py                 # Inicialización y conexión SQLite
│   ├── requirements.txt            # Dependencias Python
│   ├── olimpiadas.db               # Base de datos SQLite (se genera al primer arranque)
│   ├── servicios/
│   │   ├── equipos.py              # Servicio de Equipos
│   │   ├── deportistas.py          # Servicio de Deportistas
│   │   ├── partidos.py             # Servicio de Partidos
│   │   └── fixture.py              # Servicio de Fixture
│   ├── static/
│   │   ├── data/
│   │   │   ├── regiones.json       # 25 regiones del Perú
│   │   │   └── deportes.json       # 4 deportes con categoría
│   │   └── js/
│   │       ├── main.js             # Punto de entrada JS
│   │       └── modules/            # Módulos ES por servicio
│   │           ├── config.js
│   │           ├── equipos.js
│   │           ├── deportistas.js
│   │           ├── fixture.js
│   │           ├── partidos.js
│   │           ├── usuarios.js
│   │           ├── autocomplete.js
│   │           ├── searchSelect.js  # Combobox buscable (regiones/deportes)
│   │           └── ui.js
│   └── templates/
│       ├── index.html              # Interfaz principal (Tailwind CSS)
│       └── login.html              # Página de autenticación
├── docs/
│   ├── bpmn/                       # Diagramas BPMN (.bpmn, .png, .svg)
│   └── referencias/                # PDFs de referencias académicas
└── silabus/                        # Sílabo oficial del curso
```

---

## Cómo ejecutar

### 1. Clonar el repositorio

```bash
git clone https://github.com/DanielLazaro1555/Proyecto-Olimpiadas.git
cd Proyecto-Olimpiadas
```

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r app/requirements.txt
```

### 4. Ejecutar la aplicación

```bash
cd app
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`

> La base de datos `olimpiadas.db` se inicializa automáticamente al primer arranque con las tablas necesarias y un usuario `admin` / `admin123` para comenzar.

### Credenciales por defecto

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Administrador (acceso completo + gestión de usuarios) |
| `operador` | `operador123` | Operador (gestión deportiva, sin gestión de usuarios) |
| `viewer` | `viewer123` | Visualizador (solo consulta) |

---

## Endpoints REST

### Autenticación — `/auth`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/auth/login` | — | Iniciar sesión, retorna token JWT |
| POST | `/auth/registro` | Admin | Registrar nuevo usuario |
| GET | `/auth/usuarios` | Admin | Listar todos los usuarios |
| DELETE | `/auth/usuarios/<id>` | Admin | Eliminar un usuario |

### Equipos — `/equipos`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/equipos/` | — | Listar todos los equipos |
| POST | `/equipos/` | Admin/Op | Registrar un nuevo equipo |
| DELETE | `/equipos/<id>` | Admin/Op | Eliminar un equipo |

### Deportistas — `/deportistas`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/deportistas/equipo/<id>` | — | Listar deportistas de un equipo |
| POST | `/deportistas/inscribir` | Admin/Op | Inscribir un deportista |

### Fixture — `/fixture`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/fixture/generar/<deporte>` | Admin/Op | Generar calendario para un deporte |
| DELETE | `/fixture/eliminar/<deporte>` | Admin/Op | Eliminar el calendario de un deporte |
| GET | `/fixture/consultar/<deporte>` | Token | Consultar partidos de un deporte |

### Partidos — `/partidos`

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/partidos/resultado` | Admin/Op | Registrar resultado de un partido |
| GET | `/partidos/tabla/<deporte>` | Token | Consultar tabla de posiciones |

> **Auth:** `—` = público · `Token` = requiere JWT válido · `Admin` = solo administrador · `Admin/Op` = administrador u operador

---

## Planificación (Diagrama de Gantt)

| Actividad | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 | S13 | S14 | S15 | S16 | S17 | S18 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Análisis y modelado BPMN | ✅ | | | | | | | | | | | | | |
| Diseño de servicios y arquitectura | ✅ | ✅ | | | | | | | | | | | | |
| **APF1** — documentación entregada | **✅** | | | | | | | | | | | | | |
| Configuración de entorno y Git | | ✅ | | | | | | | | | | | | |
| Autenticación JWT + bcrypt | | | ✅ | | | | | | | | | | | |
| Servicio de Equipos | | ✅ | ✅ | | | | | | | | | | | |
| Servicio de Deportistas | | | ✅ | ✅ | | | | | | | | | | |
| Servicio de Fixture | | | | ✅ | ✅ | | | | | | | | | |
| Servicio de Partidos | | | | | ✅ | ✅ | | | | | | | | |
| Frontend (Tailwind + roles) | | | | ✅ | ✅ | ✅ | | | | | | | | |
| Control de roles en UI y backend | | | | | | ✅ | | | | | | | | |
| **APF2** — 30% funcionalidad | | | | | | **✅** | | | | | | | | |
| Registro de servicios (UDDI-like) | | | | | | | X | | | | | | | |
| Integración B2B / OpenAPI docs | | | | | | | | X | X | | | | | |
| SOA + BPM: trazabilidad de procesos | | | | | | | | | X | X | | | | |
| Mejores prácticas SOA | | | | | | | | | | X | X | | | |
| **APF3** — 60% funcionalidad | | | | | | | | | | | **X** | | | |
| Service Bus / auditoría | | | | | | | | | | | | X | X | |
| Pruebas finales y correcciones | | | | | | | | | | | | X | X | |
| **Proyecto Final** | | | | | | | | | | | | | | **X** |

> ✅ = completado · X = planificado

---

## Plan APF3 (Semana 15)

Según el sílabo (Unidad 3 — Semanas 11–15), los temas a abordar e implementar son:

### Semana 11 — Implementación SOA: capas empresariales
- Documentar las capas del sistema (presentación → servicio → datos)
- Comenzar separación core/adaptadores (arquitectura hexagonal parcial)

### Semana 12 — Registro de Servicios (concepto UDDI)
- Implementar endpoint `GET /servicios` que liste todos los servicios disponibles con sus operaciones y contratos (registro interno tipo UDDI simplificado)

### Semana 13 — Integración de procesos / B2B
- Generar documentación OpenAPI (Swagger) de la API para consumo externo
- Exponer un endpoint de metadatos que permita a sistemas externos descubrir los servicios

### Semana 14 — SOA y BPM
- Relacionar explícitamente cada proceso BPMN con su endpoint REST correspondiente en la documentación
- Agregar trazabilidad: registrar en BD quién realizó cada operación (audit log básico)

### Semana 15 — Integridad de procesos + Mejores prácticas SOA
- Validaciones de integridad referencial más robustas
- Manejo de errores estandarizado en todos los endpoints
- Revisión de los 8 principios de diseño de servicios SOA aplicados al proyecto
- **Entrega APF3**

---

## Referencias

- Chamari, L., Petrova, E., & Pauwels, P. (2023). *An end-to-end implementation of a service-oriented architecture for data-driven smart buildings.* IEEE Access, 11, 117261–117281.
- Delgado, A., García-Rodríguez de Guzmán, I., Ruiz, F., & Piattini, M. (2010). *Metodologías de desarrollo para Service Oriented Architectures con Rational Unified Process.*
- López, D. J., Guerrero, J. A., & Díaz Benachí, E. (2014). *Arquitectura Orientada a Servicios - SOA, aplicada a la industria.* Corporación Universitaria Comfacauca.
- Marante Valdivia, M. (2010). *Análisis y diseño de servicios en la adopción de una arquitectura orientada a servicios.* LACCEI 2010, Arequipa, Perú.
- Mohor Tapia, C. A. (2006). *Análisis y diseño de una arquitectura SOA para una institución financiera.* PUCV.

---

> Licencia: [MIT](LICENSE) · Proyecto académico — Universidad Tecnológica del Perú · 2026
