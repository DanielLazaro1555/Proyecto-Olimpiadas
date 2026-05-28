# **UNIVERSIDAD TECNOLÓGICA DEL PERÚ – FACULTAD DE INGENIERÍA** {#universidad-tecnológica-del-perú-–-facultad-de-ingeniería}

**Asignatura:** Arquitectura Orientada al Servicio  
**Sección:** 35875  
**Docente:** Ing. Kelvin Macedo Ylachoque  
**Tema:** Primera Entrega \- Trabajo Final SOA  
**Integrantes:** Huamán Lázaro, Daniel Esteban \- U22326979

**Lima \- Perú**  
**2025**

[**UNIVERSIDAD TECNOLÓGICA DEL PERÚ – FACULTAD DE INGENIERÍA	1**](#universidad-tecnológica-del-perú-–-facultad-de-ingeniería)

[INTRODUCCIÓN	2](#introducción)

[PROBLEMÁTICA	2](#problemática)

[SOLUCIÓN PROPUESTA	2](#solución-propuesta)

[MODELO DE PROCESOS	3](#modelo-de-procesos)

[IDENTIFICACIÓN DE SERVICIOS	4](#identificación-de-servicios)

[Servicio de Equipos	4](#servicio-de-equipos)

[Servicio de Deportistas	4](#servicio-de-deportistas)

[Servicio de Partidos	5](#servicio-de-partidos)

[Servicio de Fixture (Sorteo)	5](#servicio-de-fixture-\(sorteo\))

[TECNOLOGÍAS A UTILIZAR	5](#tecnologías-a-utilizar)

[Lenguaje de programación	6](#lenguaje-de-programación)

[Framework para servicios web (API REST)	6](#framework-para-servicios-web-\(api-rest\))

[Base de datos	6](#base-de-datos)

[Cliente (frontend)	6](#cliente-\(frontend\))

[Herramientas de desarrollo y pruebas	6](#herramientas-de-desarrollo-y-pruebas)

[Infraestructura	6](#infraestructura)

[PLANIFICACIÓN DEL PROYECTO (DIAGRAMA DE GANTT)	7](#planificación-del-proyecto-\(diagrama-de-gantt\))

[REFERENCIAS	9](#referencias)

## **INTRODUCCIÓN** {#introducción}

La Arquitectura Orientada a Servicios (SOA) estructura los sistemas en módulos reutilizables, con contratos bien definidos y bajo acoplamiento, permitiendo que proveedores y consumidores interactúen de forma desacoplada (Delgado et al., 2010; Mohor Tapia, 2006). Este enfoque facilita la interoperabilidad y escalabilidad ante cambios operativos (Chamari et al., 2023; Peralta Ascue et al., 2017).

Aplicar estos principios al sistema **Olimpiadas Perú** permite que funcionalidades como registro de equipos, inscripción de deportistas, generación de fixtures y publicación de resultados se estructuren como servicios independientes, evolucionando y reutilizándose mediante APIs RESTful sin afectar el sistema completo.

## **PROBLEMÁTICA** {#problemática}

La gestión tradicional de eventos deportivos a gran escala suele depender de procesos manuales o herramientas desconectadas, lo que genera silos de información, redundancia de datos y altos costos de mantenimiento (López et al., 2014). Esta fragmentación dificulta la trazabilidad, introduce errores en la asignación de horarios y limita la capacidad de escalar a nuevas disciplinas o instituciones, problemática recurrente en entornos sin una arquitectura de integración unificada (Mohor Tapia, 2006; Peralta Ascue et al., 2017). En el caso de Olimpiadas Perú, la ausencia de un modelo estandarizado para el registro de equipos, sorteo de fixtures y publicación de resultados compromete la transparencia y la eficiencia operativa, haciendo indispensable la adopción de un enfoque arquitectónico que desacople la lógica de negocio de la infraestructura tecnológica.

## **SOLUCIÓN PROPUESTA** {#solución-propuesta}

Se propone un sistema basado en SOA que modularice los procesos críticos de las olimpiadas en servicios independientes y reutilizables, garantizando bajo acoplamiento y contratos de interfaz claros (Delgado et al., 2010). Al adoptar un enfoque *API-first* y principios de diseño moderno, la arquitectura permitirá que funcionalidades como el registro de equipos, la inscripción de deportistas, la generación aleatoria de fixtures y el registro de resultados operen de forma autónoma, escalable y consumible mediante APIs RESTful (Chamari et al., 2023). Esta estructura no solo automatiza las operaciones actuales, sino que sienta las bases para incorporar nuevos deportes, reglas de competencia o integraciones externas sin afectar el sistema completo.

## **MODELO DE PROCESOS** {#modelo-de-procesos}

1. Diagrama 1: Registrar equipo  
   ![][image2]  
   *“Diagrama 1 \- Se inicia el proceso ingresando valores como país, deporte y nombre del equipo. Luego el sistema verifica si ya existe un equipo del mismo país en ese deporte. **Si NO existe**, se guarda el equipo en la base de datos y se confirma el registro exitoso. **Si SÍ existe**, se muestra un mensaje de error y se regresa al paso de ingresar datos para corregir o intentar con otro país/deporte.”*  
     
     
     
     
     
     
     
     
     
2. Diagrama 2: Inscribir deportista  
   ![][image3]  
   *“Diagrama 2 \- Se inicia el proceso seleccionando un equipo ya registrado. Luego se ingresan los datos del deportista. El sistema verifica si ese deportista ya está inscrito en el equipo seleccionado. **Si NO existe** (es decir, el deportista no está aún en ese equipo), se guarda la inscripción y se confirma el registro exitoso. **Si SÍ existe**, se muestra un mensaje de error (deportista duplicado) y se regresa a la selección del equipo para reiniciar el proceso.”*  
3. Diagrama 3: Registrar Resultado  
   ![][image4]  
   *“Diagrama 3 \- Se inicia el proceso seleccionando un partido del fixture previamente generado. Luego se ingresa el marcador (goles o puntos). El sistema verifica si ese partido ya tiene un resultado registrado. **Si NO existe** (aún no se ha registrado resultado), se guarda el marcador y se actualiza automáticamente la tabla de posiciones. **Si SÍ existe**, se muestra un mensaje de error indicando que no se puede sobrescribir el resultado y el proceso termina sin cambios.”*  
4. Diagrama 4: Generar fixture simple  
   ![][image5]  
   *“Diagrama 4 \- Se inicia el proceso cuando el usuario solicita el sorteo para un deporte específico. El sistema cuenta cuántos equipos están inscritos en ese deporte. **Si hay al menos 2 equipos**, se generan enfrentamientos aleatorios, se asignan fechas y horas básicas, se guarda el fixture y se notifica a los equipos. **Si hay menos de 2 equipos**, se muestra un mensaje de error (equipos insuficientes) y el proceso termina sin generar fixture.”*

## **IDENTIFICACIÓN DE SERVICIOS** {#identificación-de-servicios}

A partir del análisis de los procesos modelados en BPMN (registro de equipos, inscripción de deportistas, registro de resultados y generación de fixture), se han identificado los siguientes servicios que formarán parte de la arquitectura orientada a servicios del sistema Olimpiadas Perú. Cada servicio agrupa un conjunto de operaciones relacionadas, diseñadas para ser reutilizables, independientes y fácilmente invocables desde distintos clientes.

### **Servicio de Equipos** {#servicio-de-equipos}

Gestiona toda la información relacionada con los equipos participantes. Sus operaciones principales son:

* `registrarEquipo(pais, deporte, nombreEquipo)`: guarda un nuevo equipo en la base de datos, previa validación de unicidad.  
* `verificarExistencia(pais, deporte)`: comprueba si ya existe un equipo del mismo país en el deporte indicado. Retorna `true` o `false`.  
* `consultarEquipos()`: devuelve el listado completo de equipos registrados.  
* `eliminarEquipo(idEquipo)`: elimina un equipo existente (solo si no tiene partidos asignados).

### **Servicio de Deportistas** {#servicio-de-deportistas}

Administra la inscripción y consulta de deportistas en los equipos. Incluye:

* `inscribirDeportista(idEquipo, datosDeportista)`: registra un deportista en un equipo específico, siempre que no esté ya inscrito.  
* `verificarInscripcion(idEquipo, idDeportista)`: retorna si el deportista ya pertenece al equipo.  
* `listarDeportistasPorEquipo(idEquipo)`: obtiene la lista de deportistas de un equipo dado.  
* `eliminarInscripcion(idInscripcion)`: elimina la inscripción de un deportista.

### **Servicio de Partidos** {#servicio-de-partidos}

Gestiona los resultados de los encuentros y la actualización de la tabla de posiciones. Sus operaciones son:

* `registrarResultado(idPartido, marcador)`: almacena el resultado de un partido, siempre que no exista un resultado previo.  
* `verificarResultadoExistente(idPartido)`: indica si el partido ya tiene un resultado registrado.  
* `consultarFixture(deporte)`: devuelve el calendario de partidos para un deporte específico.  
* `actualizarTablaPosiciones(idDeporte)`: recalcula y actualiza la tabla de posiciones después de registrar un resultado.

### **Servicio de Fixture (Sorteo)** {#servicio-de-fixture-(sorteo)}

Se encarga de generar el calendario de enfrentamientos de forma aleatoria. Contiene:

* `generarFixture(idDeporte)`: crea los emparejamientos y asigna fechas/horas básicas, siempre que haya al menos 2 equipos inscritos.  
* `contarEquiposInscriptos(idDeporte)`: retorna el número de equipos registrados en un deporte.  
* `notificarEquipos(idFixture)`: envía una notificación (dentro del sistema o por correo) a los equipos con las fechas asignadas.

Estos servicios serán implementados mediante APIs RESTful y expuestos a través de un cliente (aplicación web o móvil) que los consumirá según las necesidades de cada proceso. La granularidad elegida permite que cada servicio pueda evolucionar de forma independiente, facilitando el mantenimiento y la escalabilidad futura.

## 

## **TECNOLOGÍAS A UTILIZAR** {#tecnologías-a-utilizar}

Esta selección tecnológica se sustenta en la evolución moderna de SOA hacia enfoques *API-first* y servicios modulares, que priorizan la ligereza, la interoperabilidad nativa con HTTP/JSON y la facilidad de despliegue (Chamari et al., 2023). El uso de estándares web abiertos y frameworks livianos como Flask permite construir contratos de servicio claros sin depender de intermediarios complejos, facilitando la integración, las pruebas unitarias y el mantenimiento ágil durante el ciclo de desarrollo del proyecto (Peralta Ascue et al., 2017).

### **Lenguaje de programación** {#lenguaje-de-programación}

* **Python 3**: Lenguaje interpretado, multiplataforma, con amplia biblioteca estándar y gran facilidad para desarrollar servicios web de forma rápida y mantenible.

### **Framework para servicios web (API REST)** {#framework-para-servicios-web-(api-rest)}

* **Flask**: Microframework liviano y flexible para construir APIs RESTful. Permite exponer los servicios identificados (Equipos, Deportistas, Partidos, Fixture) mediante rutas y métodos HTTP. Se complementará con **Flask-CORS** para permitir peticiones desde clientes web.

### **Base de datos** {#base-de-datos}

* **SQLite**: Motor de base de datos relacional ligero, sin necesidad de servidor adicional. Almacena los datos en un archivo local, suficiente para la escala del proyecto. Las tablas incluirán: equipos, deportistas, inscripciones, partidos, resultados y fixture.

### **Cliente (frontend)** {#cliente-(frontend)}

* **HTML5, CSS y JavaScript puro (Vanilla JS)**: Se desarrollará una interfaz web simple que consuma los servicios REST mediante `fetch` o `axios`. Esto permitirá probar y demostrar la funcionalidad completa sin dependencias complejas.

### 

### **Herramientas de desarrollo y pruebas** {#herramientas-de-desarrollo-y-pruebas}

* **Insomnia**: Para probar los endpoints de los servicios durante el desarrollo.  
* **Git**: Control de versiones del código fuente.  
* **Entorno virtual (venv)**: Aislamiento de dependencias del proyecto.

### **Infraestructura** {#infraestructura}

* **Localhost (127.0.0.1)**: El sistema se ejecutará de manera local, sin necesidad de servidores en la nube ni costos adicionales, tal como lo indicó el profesor en clase.

Esta selección tecnológica permite cumplir con los plazos del curso, centrarse en la lógica de negocio de las olimpiadas y demostrar los principios de SOA sin complejidades innecesarias.

## **PLANIFICACIÓN DEL PROYECTO (DIAGRAMA DE GANTT)** {#planificación-del-proyecto-(diagrama-de-gantt)}

He planificado las actividades del proyecto desde la semana 5 hasta la semana 18\. La tabla siguiente muestra qué voy a hacer cada semana.

| Actividad | Semana 5 | Semana 6 | Semana 7 | Semana 8 | Semana 9 | Semana 10 | Semana 11 | Semana 12 | Semana 13 | Semana 14 | Semana 15 | Semana 16 | Semana 17 | Semana 18 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Análisis y modelado (BPMN) | X |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Diseño de servicios y arquitectura | X | X |  |  |  |  |  |  |  |  |  |  |  |  |
| Configuración de entorno (Python/Flask) |  | X |  |  |  |  |  |  |  |  |  |  |  |  |
| Implementación servicio de Equipos |  | X | X |  |  |  |  |  |  |  |  |  |  |  |
| Implementación servicio de Deportistas |  |  | X | X |  |  |  |  |  |  |  |  |  |  |
| Implementación servicio de Fixture |  |  |  | X | X |  |  |  |  |  |  |  |  |  |
| Implementación servicio de Partidos |  |  |  |  | X | X |  |  |  |  |  |  |  |  |
| Pruebas unitarias e integración |  |  |  |  |  | X | X |  |  |  |  |  |  |  |
| **Avance APF2 (semana 10\)** |  |  |  |  |  | **X** |  |  |  |  |  |  |  |  |
| Implementación frontend (cliente web) |  |  |  |  |  |  | X | X | X |  |  |  |  |  |
| Pruebas de calidad (Insomnia, estrés) |  |  |  |  |  |  |  |  | X | X |  |  |  |  |
| **Avance APF3 (semana 15\)** |  |  |  |  |  |  |  |  |  |  | **X** |  |  |  |
| Documentación final y manual |  |  |  |  |  |  |  |  |  |  | X | X |  |  |
| Pruebas finales y correcciones |  |  |  |  |  |  |  |  |  |  |  | X | X |  |
| **Entrega final PROY (semana 18\)** |  |  |  |  |  |  |  |  |  |  |  |  |  | **X** |

## **REFERENCIAS** {#referencias}

Chamari, L., Petrova, E., & Pauwels, P. (2023). An end-to-end implementation of a service-oriented architecture for data-driven smart buildings. IEEE Access, 11, 117261–117281. [https://doi.org/10.1109/ACCESS.2023.3325767](https://doi.org/10.1109/ACCESS.2023.3325767)

Delgado, A., García-Rodríguez de Guzmán, I., Ruiz, F., & Piattini, M. (2010). Metodologías de desarrollo para Service Oriented Architectures con Rational Unified Process. Revista Iberoamericana de Ingeniería de Software, 3(2), 125–136.

López, D. J., Guerrero, J. A., & Díaz Benachí, E. (2014). Arquitectura Orientada a Servicios \- SOA, aplicada a la industria. Corporación Universitaria Comfacauca, Grupo de Investigación en Sistemas Inteligentes.

Marante Valdivia, M. (2010). Análisis y diseño de servicios en la adopción de una arquitectura orientada a servicios \[Ponencia de conferencia\]. 8th Latin American and Caribbean Conference for Engineering and Technology (LACCEI 2010), Arequipa, Perú. https://doi.org/10.18053/201008.001.WE1-1

Mohor Tapia, C. A. (2006). Análisis y diseño de una arquitectura SOA para una institución financiera \[Tesis de pregrado, Pontificia Universidad Católica de Valparaíso\]. Repositorio Institucional PUCV.

Peralta Ascue, M., Merma Aroni, J. L., & Fuentes Huamán, Y. (2017). Integración de procesos de negocio aplicando la arquitectura orientada a servicios (SOA). INTERFASES, (10), 93–121. [https://revistas.ulima.edu.pe/index.php/Interfases/article/view/1771](https://revistas.ulima.edu.pe/index.php/Interfases/article/view/1771)



[image2]: Diagrama_1_Registrar_equipo.png

[image3]: Diagrama_2_Inscribir_deportista.png

[image4]: Diagrama_3_Registrar_resultado.png

[image5]: Diagrama_4_Generar_fixture_simple.png
