export const slides = [
  {
    eyebrow: "Proyecto final · Arquitectura Orientada a Servicios",
    title: "Sistema Olimpiadas Perú",
    content: `
      <div class="title-layout">
        <div>
          <p class="lead">Plataforma web para gestionar una competencia deportiva nacional entre las <span class="highlight">25 regiones del Perú</span>, diseñada con servicios REST y una arquitectura por capas.</p>
          <div class="metadata">
            <span><strong>Curso:</strong> Arquitectura Orientada al Servicio · 3 créditos</span>
            <span><strong>Código y sección:</strong> 1SI84 · 24230</span>
            <span><strong>Modalidad:</strong> Virtual en vivo</span>
            <span><strong>Docente:</strong> Macedo Ylachoque, Kelvin Celso</span>
            <span><strong>Estudiante:</strong> Huamán Lázaro, Daniel Esteban</span>
            <span><strong>Universidad Tecnológica del Perú · 2026</strong></span>
          </div>
        </div>
        <div class="project-badge" aria-hidden="true">🏆</div>
      </div>`,
  },
  {
    eyebrow: "01 · Problema y solución",
    title: "De procesos manuales a servicios conectados",
    content: `
      <div class="grid" style="--columns: 3">
        <article class="card"><div class="card__icon">🧩</div><h3 class="card__title">Problema</h3><p class="card__text">Datos dispersos, errores al crear fixtures y poca visibilidad de resultados.</p></article>
        <article class="card"><div class="card__icon">⚙️</div><h3 class="card__title">Solución</h3><p class="card__text">Servicios REST organizados por responsabilidad y consumidos por una interfaz web.</p></article>
        <article class="card"><div class="card__icon">🎯</div><h3 class="card__title">Resultado</h3><p class="card__text">Gestión trazable de equipos, deportistas, partidos y reportes de la competencia.</p></article>
      </div>`,
  },
  {
    eyebrow: "02 · Alcance funcional",
    title: "Una competencia nacional, cuatro disciplinas",
    content: `
      <p class="lead">Cada delegación representa una región peruana. El sistema cubre el ciclo desde la inscripción hasta los reportes de resultados.</p>
      <div class="grid" style="--columns: 4">
        <article class="card"><div class="card__icon">⚽</div><h3 class="card__title">Fútbol</h3><p class="card__text">Categoría varones.</p></article>
        <article class="card"><div class="card__icon">🏀</div><h3 class="card__title">Básquet</h3><p class="card__text">Categoría varones.</p></article>
        <article class="card"><div class="card__icon">🏐</div><h3 class="card__title">Vóley</h3><p class="card__text">Categoría damas.</p></article>
        <article class="card"><div class="card__icon">🏓</div><h3 class="card__title">Ping-Pong</h3><p class="card__text">Categoría mixta.</p></article>
      </div>
      <div class="flow"><span>Registro de equipos</span><b>→</b><span>Inscripción</span><b>→</b><span>Fixture</span><b>→</b><span>Resultados</span><b>→</b><span>Reportes</span></div>`,
  },
  {
    eyebrow: "03 · Tecnologías",
    title: "Tecnología elegida para el alcance del proyecto",
    content: `
      <div class="grid" style="--columns: 3">
        <article class="card"><div class="card__icon">🐍</div><h3 class="card__title">Python + Flask</h3><p class="card__text">Backend REST ligero, organizado con Blueprints por servicio.</p></article>
        <article class="card"><div class="card__icon">🗃️</div><h3 class="card__title">SQLite</h3><p class="card__text">Persistencia embebida y suficiente para el volumen académico.</p></article>
        <article class="card"><div class="card__icon">🔐</div><h3 class="card__title">PyJWT + bcrypt</h3><p class="card__text">Tokens de sesión y contraseñas protegidas con hash seguro.</p></article>
        <article class="card"><div class="card__icon">🖥️</div><h3 class="card__title">HTML, CSS y JavaScript</h3><p class="card__text">Cliente web modular con gráficos de reportes.</p></article>
        <article class="card"><div class="card__icon">📦</div><h3 class="card__title">Podman + Gunicorn</h3><p class="card__text">Ejecución aislada y ruta de despliegue reproducible.</p></article>
        <article class="card"><div class="card__icon">📜</div><h3 class="card__title">OpenAPI</h3><p class="card__text">Contratos documentados y Swagger UI en <code>/docs</code>.</p></article>
      </div>`,
  },
  {
    eyebrow: "04 · Inventario de servicios",
    title: "Siete servicios funcionales",
    content: `
      <div class="service-list">
        <div class="service"><span>🔐</span><div><p class="service__name">Autenticación</p><p class="service__path">/auth · JWT, bcrypt y roles</p></div></div>
        <div class="service"><span>👥</span><div><p class="service__name">Equipos</p><p class="service__path">/equipos · registro y consulta</p></div></div>
        <div class="service"><span>🏃</span><div><p class="service__name">Deportistas</p><p class="service__path">/deportistas · inscripción</p></div></div>
        <div class="service"><span>📅</span><div><p class="service__name">Fixture</p><p class="service__path">/fixture · calendario aleatorio</p></div></div>
        <div class="service"><span>⚽</span><div><p class="service__name">Partidos</p><p class="service__path">/partidos · resultados y tabla</p></div></div>
        <div class="service"><span>📊</span><div><p class="service__name">Reportes</p><p class="service__path">/reportes · goleadores y estadísticas</p></div></div>
        <div class="service"><span>✉️</span><div><p class="service__name">Notificaciones</p><p class="service__path">/notificaciones · historial y SMTP opcional</p></div></div>
        <div class="service"><span>🔎</span><div><p class="service__name">Catálogo</p><p class="service__path">/catalog · descubrimiento interno</p></div></div>
      </div>`,
  },
  {
    eyebrow: "05 · Diseño técnico",
    title: "Arquitectura por capas",
    content: `
      <p class="lead">La separación evita que las rutas HTTP contengan reglas de negocio o consultas SQL directamente.</p>
      <div class="layers">
        <div class="layer"><span class="layer__label">Adaptadores HTTP</span><span class="layer__detail">Blueprints Flask en <code>servicios/</code>: reciben solicitudes y devuelven respuestas REST.</span></div>
        <div class="layer"><span class="layer__label">Lógica de negocio</span><span class="layer__detail"><code>core/services/</code>: validaciones, reglas de resultados, fixture y reportes.</span></div>
        <div class="layer"><span class="layer__label">Persistencia</span><span class="layer__detail"><code>core/repositories/</code> y SQLite: acceso a datos desacoplado.</span></div>
      </div>`,
  },
  {
    eyebrow: "06 · Experiencia de usuario",
    title: "Una interfaz por roles y orientada a decisiones",
    content: `
      <div class="grid" style="--columns: 3">
        <article class="card"><div class="card__icon">👑</div><h3 class="card__title">Administrador</h3><p class="card__text">Gestiona usuarios, consulta auditoría y opera todos los servicios deportivos.</p></article>
        <article class="card"><div class="card__icon">🛠️</div><h3 class="card__title">Operador</h3><p class="card__text">Registra equipos, deportistas, fixture y resultados sin administrar usuarios.</p></article>
        <article class="card"><div class="card__icon">👁️</div><h3 class="card__title">Visualizador</h3><p class="card__text">Consulta información pública: fixture, tabla de posiciones y reportes.</p></article>
      </div>
      <p class="lead">Los reportes muestran tablas, ranking de goleadores, estadísticas y gráficos para convertir los resultados en información útil.</p>`,
  },
  {
    eyebrow: "07 · Procesos y calidad",
    title: "Reglas que preservan la integridad",
    content: `
      <div class="grid" style="--columns: 2">
        <article class="card"><div class="card__icon">✅</div><h3 class="card__title">Validaciones</h3><p class="card__text">Equipos únicos por región y deporte; deportistas sin duplicados; fixture con mínimo dos equipos.</p></article>
        <article class="card"><div class="card__icon">🔒</div><h3 class="card__title">Resultados confiables</h3><p class="card__text">Un resultado no se sobrescribe y los goles de goleadores deben coincidir con el marcador.</p></article>
        <article class="card"><div class="card__icon">🧾</div><h3 class="card__title">Auditoría</h3><p class="card__text">Las operaciones críticas quedan registradas con usuario, rol, ruta, método y estado HTTP.</p></article>
        <article class="card"><div class="card__icon">🗺️</div><h3 class="card__title">BPMN</h3><p class="card__text">Cuatro procesos modelados: registrar equipo, inscribir deportista, registrar resultado y generar fixture.</p></article>
      </div>`,
  },
  {
    eyebrow: "08 · Modelado de procesos",
    title: "BPMN conectado a reglas reales",
    content: `
      <div class="bpmn-gallery">
        <figure class="bpmn-card"><img src="../docs/bpmn/Diagrama_1_Registrar_equipo.png" alt="Diagrama BPMN para registrar un equipo" /><figcaption><strong>Registrar equipo</strong><span>Valida región y deporte antes de guardar.</span></figcaption></figure>
        <figure class="bpmn-card"><img src="../docs/bpmn/Diagrama_2_Inscribir_deportista.png" alt="Diagrama BPMN para inscribir un deportista" /><figcaption><strong>Inscribir deportista</strong><span>Evita inscripciones duplicadas por equipo.</span></figcaption></figure>
        <figure class="bpmn-card"><img src="../docs/bpmn/Diagrama_3_Registrar_resultado.png" alt="Diagrama BPMN para registrar un resultado" /><figcaption><strong>Registrar resultado</strong><span>Protege contra sobrescribir resultados.</span></figcaption></figure>
        <figure class="bpmn-card"><img src="../docs/bpmn/Diagrama_4_Generar_fixture_simple.png" alt="Diagrama BPMN para generar un fixture" /><figcaption><strong>Generar fixture</strong><span>Requiere un mínimo de dos equipos.</span></figcaption></figure>
      </div>`,
  },
  {
    eyebrow: "09 · Auditoría y trazabilidad",
    title: "Cada operación crítica deja evidencia",
    content: `
      <div class="layers">
        <div class="layer"><span class="layer__label">Evento</span><span class="layer__detail">Una operación <code>POST</code> o <code>DELETE</code> se realiza sobre un servicio del sistema.</span></div>
        <div class="layer"><span class="layer__label">Registro</span><span class="layer__detail">El middleware captura usuario, rol, método, ruta, payload sensible censurado y estado HTTP.</span></div>
        <div class="layer"><span class="layer__label">Consulta</span><span class="layer__detail">El administrador accede al historial mediante <code>GET /auth/auditoria</code>.</span></div>
      </div>
      <p class="lead">Esta trazabilidad facilita investigar errores y demostrar quién ejecutó una operación durante la gestión del evento.</p>`,
  },
  {
    eyebrow: "10 · Evidencia de pruebas",
    title: "Calidad verificada",
    content: `
      <div class="metrics">
        <article class="metric"><p class="metric__value">21</p><p class="metric__label">pruebas unitarias e integración</p></article>
        <article class="metric"><p class="metric__value">0</p><p class="metric__label">fallos en la ejecución final</p></article>
        <article class="metric"><p class="metric__value">4</p><p class="metric__label">diagramas BPMN documentados</p></article>
      </div>
      <p class="lead">La suite cubre autenticación, equipos, fixture, resultados, goles, reportes, notificaciones, auditoría y endpoints Flask con SQLite temporal.</p>`,
  },
  {
    eyebrow: "11 · Rendimiento",
    title: "Carga concurrente sin errores",
    content: `
      <table class="result-table"><thead><tr><th>Escenario · 20 clientes</th><th>Peticiones</th><th>Errores</th><th>Latencia p95</th></tr></thead>
      <tbody><tr><td>Lecturas públicas</td><td>400</td><td class="status">0</td><td>22.2 ms</td></tr><tr><td>Login con bcrypt</td><td>200</td><td class="status">0</td><td>682.4 ms</td></tr><tr><td>Escrituras SQLite</td><td>100</td><td class="status">0</td><td>185.5 ms</td></tr></tbody></table>
      <p class="lead">El costo del login es deliberado: bcrypt protege las contraseñas. Para mayor concurrencia, se recomienda habilitar WAL en SQLite y repetir la prueba con Gunicorn.</p>`,
  },
  {
    eyebrow: "12 · Seguridad",
    title: "Seguridad evaluada con evidencia",
    content: `
      <div class="grid" style="--columns: 2">
        <article class="card"><div class="card__icon">🛡️</div><h3 class="card__title">Controles confirmados</h3><p class="card__text">No se explotó inyección SQL, bypass JWT <code>alg=none</code>, IDOR ni escalación de privilegios.</p></article>
        <article class="card"><div class="card__icon">🔑</div><h3 class="card__title">Hallazgo crítico corregido</h3><p class="card__text">Se eliminó el secreto JWT predecible; producción exige definir <code>SECRET_KEY</code>.</p></article>
        <article class="card"><div class="card__icon">⚠️</div><h3 class="card__title">Mejoras pendientes</h3><p class="card__text">Cabeceras HTTP, CORS restringido, rate limiting y mitigación de enumeración por tiempo.</p></article>
        <article class="card"><div class="card__icon">🔍</div><h3 class="card__title">Pruebas reproducibles</h3><p class="card__text">Informe y script para repetir la revisión de riesgos sobre un servidor local.</p></article>
      </div>`,
  },
  {
    eyebrow: "13 · Despliegue",
    title: "Preparado para ejecutarse en una máquina nueva",
    content: `
      <div class="grid" style="--columns: 3">
        <article class="card"><div class="card__icon">1</div><h3 class="card__title">Configurar</h3><p class="card__text">Clonar el repositorio, instalar dependencias y definir <code>SECRET_KEY</code>.</p></article>
        <article class="card"><div class="card__icon">2</div><h3 class="card__title">Ejecutar</h3><p class="card__text">Usar venv en desarrollo o Podman para una ejecución aislada y persistente.</p></article>
        <article class="card"><div class="card__icon">3</div><h3 class="card__title">Verificar</h3><p class="card__text">Comprobar catálogo, Swagger, login y tabla de posiciones tras el despliegue.</p></article>
      </div>
      <p class="lead">El plan también cubre variables de entorno, persistencia de SQLite, backup, rollback y el uso de Gunicorn en producción.</p>`,
  },
  {
    eyebrow: "14 · Cumplimiento del curso",
    title: "Evidencias técnicas de la entrega final",
    content: `
      <table class="result-table"><thead><tr><th>Requisito técnico</th><th>Evidencia en el proyecto</th><th>Estado</th></tr></thead>
      <tbody><tr><td>Servicios y capas empresariales</td><td>Blueprints, servicios y repositorios separados</td><td class="status">Cumplido</td></tr><tr><td>Reportes y notificaciones</td><td>Endpoints, interfaz, gráficos e historial</td><td class="status">Cumplido</td></tr><tr><td>Pruebas no funcionales</td><td>Informes de rendimiento y seguridad reproducibles</td><td class="status">Cumplido</td></tr><tr><td>Despliegue</td><td>Guía venv/Podman y variables de entorno</td><td class="status">Cumplido</td></tr></tbody></table>
      <p class="lead">Las exposiciones, el PPT y las entregas en UTP Class son evidencias externas que requieren validación del docente.</p>`,
  },
  {
    eyebrow: "15 · Próximos pasos",
    title: "Evolución responsable hacia producción",
    content: `
      <div class="grid" style="--columns: 3">
        <article class="card"><div class="card__icon">🛡️</div><h3 class="card__title">Endurecer seguridad</h3><p class="card__text">Restringir CORS, agregar cabeceras HTTP y rate limiting al login.</p></article>
        <article class="card"><div class="card__icon">⚡</div><h3 class="card__title">Escalar datos</h3><p class="card__text">Usar WAL como mejora inmediata y una base de datos de servidor si el volumen crece.</p></article>
        <article class="card"><div class="card__icon">🔗</div><h3 class="card__title">Integración avanzada</h3><p class="card__text">Incorporar mensajería asíncrona o un ESB cuando el contexto lo justifique.</p></article>
      </div>`,
  },
  {
    eyebrow: "Conclusión",
    title: "Un prototipo SOA funcional y defendible",
    content: `
      <div class="closing"><div><p class="lead">El proyecto entrega una solución funcional para la gestión deportiva, con servicios desacoplados, controles de seguridad, pruebas automatizadas y documentación de operación.</p><p class="lead">Su siguiente evolución natural es reforzar los controles de producción y reemplazar SQLite por una base de datos de servidor si el volumen crece.</p><p class="sources">Evidencias: README, pruebas automatizadas, diagramas BPMN e informes de rendimiento, seguridad y despliegue.</p></div></div>`,
  },
];
