# Sistema Olimpiadas Perú — SOA

**Universidad Tecnológica del Perú · Facultad de Ingeniería**  
**Asignatura:** Arquitectura Orientada al Servicio · Sección 35875  
**Docente:** Ing. Kelvin Macedo Ylachoque  
**Estudiante:** Huamán Lázaro, Daniel Esteban · U22326979  
**Año:** 2025

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Problemática](#problemática)
- [Solución propuesta](#solución-propuesta)
- [Arquitectura de servicios](#arquitectura-de-servicios)
- [Procesos BPMN](#procesos-bpmn)
- [Tecnologías](#tecnologías)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Cómo ejecutar](#cómo-ejecutar)
- [Endpoints REST](#endpoints-rest)
- [Planificación](#planificación)
- [Referencias](#referencias)

---

## Descripción

Sistema de gestión de eventos deportivos basado en **Arquitectura Orientada a Servicios (SOA)**. Modulariza los procesos críticos de las Olimpiadas Perú en servicios independientes y reutilizables, expuestos mediante APIs RESTful.

## Problemática

La gestión tradicional de eventos deportivos a gran escala depende de procesos manuales o herramientas desconectadas, lo que genera:

- Silos de información y redundancia de datos
- Errores en la asignación de horarios
- Alta dificultad para escalar a nuevas disciplinas o instituciones
- Falta de transparencia en resultados y fixtures

## Solución propuesta

Sistema *API-first* basado en SOA que desacopla la lógica de negocio en cuatro servicios independientes con contratos de interfaz claros. Permite que cada servicio evolucione de forma autónoma sin afectar al sistema completo.

---

## Arquitectura de servicios

### Servicio de Equipos
Gestiona los equipos participantes.

| Operación | Descripción |
|---|---|
| `registrarEquipo(pais, deporte, nombreEquipo)` | Registra un equipo con validación de unicidad |
| `verificarExistencia(pais, deporte)` | Comprueba si ya existe un equipo del mismo país en ese deporte |
| `consultarEquipos()` | Devuelve el listado completo de equipos |
| `eliminarEquipo(idEquipo)` | Elimina un equipo (solo si no tiene partidos asignados) |

### Servicio de Deportistas
Administra la inscripción de deportistas en equipos.

| Operación | Descripción |
|---|---|
| `inscribirDeportista(idEquipo, datosDeportista)` | Inscribe un deportista validando que no esté duplicado |
| `verificarInscripcion(idEquipo, idDeportista)` | Verifica si el deportista ya pertenece al equipo |
| `listarDeportistasPorEquipo(idEquipo)` | Lista los deportistas de un equipo |
| `eliminarInscripcion(idInscripcion)` | Elimina la inscripción de un deportista |

### Servicio de Partidos
Gestiona resultados y tabla de posiciones.

| Operación | Descripción |
|---|---|
| `registrarResultado(idPartido, marcador)` | Registra el resultado (no permite sobrescribir) |
| `verificarResultadoExistente(idPartido)` | Indica si el partido ya tiene resultado |
| `consultarFixture(deporte)` | Devuelve el calendario de partidos por deporte |
| `actualizarTablaPosiciones(idDeporte)` | Recalcula la tabla de posiciones |

### Servicio de Fixture (Sorteo)
Genera el calendario de enfrentamientos aleatorios.

| Operación | Descripción |
|---|---|
| `generarFixture(idDeporte)` | Crea emparejamientos y asigna fechas (mínimo 2 equipos) |
| `contarEquiposInscriptos(idDeporte)` | Retorna el número de equipos en un deporte |
| `notificarEquipos(idFixture)` | Notifica a los equipos sus fechas asignadas |

---

## Procesos BPMN

Los flujos de negocio están modelados en cuatro diagramas BPMN ubicados en `Proyecto Individual/Diagramas BPMN/`:

1. **Registrar equipo** — Valida unicidad por país y deporte antes de guardar.
2. **Inscribir deportista** — Valida que el deportista no esté ya inscrito en el equipo.
3. **Registrar resultado** — Solo permite registrar si el partido no tiene resultado previo.
4. **Generar fixture** — Solo genera si hay al menos 2 equipos inscritos en el deporte.

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3 |
| Framework API | Flask + Flask-CORS |
| Base de datos | SQLite (`olimpiadas.db`) |
| Frontend | HTML5 + CSS3 + JavaScript (Vanilla) |
| Pruebas | Insomnia |
| Control de versiones | Git |
| Entorno | venv (entorno virtual Python) |

---

## Estructura del proyecto

```
Proyecto-Olimpiadas/
├── README.md
├── LICENSE
├── .gitignore
├── app/                        # Aplicación Flask
│   ├── app.py                  # Entry point — registra todos los blueprints
│   ├── auth.py                 # Blueprint de autenticación
│   ├── database.py             # Inicialización y conexión a SQLite
│   ├── olimpiadas.db           # Base de datos SQLite
│   ├── servicios/
│   │   ├── __init__.py
│   │   ├── equipos.py          # Servicio de Equipos
│   │   ├── deportistas.py      # Servicio de Deportistas
│   │   ├── partidos.py         # Servicio de Partidos
│   │   └── fixture.py          # Servicio de Fixture
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── main.js
│   │       └── modules/        # Módulos JS por servicio
│   └── templates/
│       ├── index.html          # Interfaz principal
│       └── login.html          # Página de autenticación
├── docs/
│   ├── bpmn/                   # Diagramas BPMN (.bpmn, .png, .svg) + README
│   └── referencias/            # PDFs de referencias académicas
└── venv/                       # Entorno virtual (ignorado por .gitignore)
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
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install flask flask-cors
```

### 4. Ejecutar la aplicación

```bash
cd app
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`

> La base de datos `olimpiadas.db` se inicializa automáticamente al arrancar.

---

## Endpoints REST

### Equipos — `/equipos`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/equipos` | Listar todos los equipos |
| POST | `/equipos` | Registrar un nuevo equipo |
| DELETE | `/equipos/<id>` | Eliminar un equipo |

### Deportistas — `/deportistas`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/deportistas/<equipo_id>` | Listar deportistas de un equipo |
| POST | `/deportistas` | Inscribir un deportista |
| DELETE | `/deportistas/<id>` | Eliminar inscripción |

### Partidos — `/partidos`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/partidos/<deporte>` | Consultar fixture por deporte |
| POST | `/partidos/<id>/resultado` | Registrar resultado de un partido |

### Fixture — `/fixture`
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/fixture/generar` | Generar fixture para un deporte |

---

## Planificación (Diagrama de Gantt)

| Actividad | S5 | S6 | S7 | S8 | S9 | S10 | S11 | S12 | S13 | S14 | S15 | S16 | S17 | S18 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Análisis y modelado BPMN | X | | | | | | | | | | | | | |
| Diseño de servicios y arquitectura | X | X | | | | | | | | | | | | |
| Configuración de entorno | | X | | | | | | | | | | | | |
| Servicio de Equipos | | X | X | | | | | | | | | | | |
| Servicio de Deportistas | | | X | X | | | | | | | | | | |
| Servicio de Fixture | | | | X | X | | | | | | | | | |
| Servicio de Partidos | | | | | X | X | | | | | | | | |
| Pruebas unitarias e integración | | | | | | X | X | | | | | | | |
| **APF2 (semana 10)** | | | | | | **X** | | | | | | | | |
| Frontend (cliente web) | | | | | | | X | X | X | | | | | |
| Pruebas de calidad | | | | | | | | | X | X | | | | |
| **APF3 (semana 15)** | | | | | | | | | | | **X** | | | |
| Documentación final | | | | | | | | | | | X | X | | |
| Pruebas finales y correcciones | | | | | | | | | | | | X | X | |
| **Entrega final (semana 18)** | | | | | | | | | | | | | | **X** |

---

## Referencias

- Chamari, L., Petrova, E., & Pauwels, P. (2023). *An end-to-end implementation of a service-oriented architecture for data-driven smart buildings.* IEEE Access, 11, 117261–117281.
- Delgado, A., García-Rodríguez de Guzmán, I., Ruiz, F., & Piattini, M. (2010). *Metodologías de desarrollo para Service Oriented Architectures con Rational Unified Process.* Revista Iberoamericana de Ingeniería de Software, 3(2), 125–136.
- López, D. J., Guerrero, J. A., & Díaz Benachí, E. (2014). *Arquitectura Orientada a Servicios - SOA, aplicada a la industria.* Corporación Universitaria Comfacauca.
- Marante Valdivia, M. (2010). *Análisis y diseño de servicios en la adopción de una arquitectura orientada a servicios.* LACCEI 2010, Arequipa, Perú.
- Mohor Tapia, C. A. (2006). *Análisis y diseño de una arquitectura SOA para una institución financiera.* PUCV.

---

> Licencia: [MIT](LICENSE) · Proyecto académico de código abierto
