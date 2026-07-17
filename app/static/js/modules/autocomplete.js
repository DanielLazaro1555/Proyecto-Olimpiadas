// autocomplete.js — inicializa searchSelect desde JSON y carga el select de equipos

import { API_BASE } from "./config.js";
import { initSearchSelect } from "./searchSelect.js";

export async function cargarSugerencias() {
  // ── 1. Cargar JSON de regiones y deportes en paralelo ────────────────────
  const [regionesRes, deportesRes] = await Promise.all([
    fetch("/static/data/regiones.json"),
    fetch("/static/data/deportes.json"),
  ]);
  const regiones = await regionesRes.json();
  const deportes = await deportesRes.json();

  // ── 2. SearchSelect para REGIÓN (formulario de equipo) ───────────────────
  initSearchSelect("region", regiones, "Escribe la región...");

  // ── 3. SearchSelect para DEPORTE en formulario de equipo ─────────────────
  // Usamos los nombres simples como valores y las etiquetas con categoría de display
  _initDeporteSelect("deporteEquipo", deportes);

  // ── 4. Selects simples de deporte para Fixture / Consulta / Tabla ────────
  _initDeporteSelect("deporteFixture",   deportes);
  _initDeporteSelect("deporteConsultar", deportes);
  _initDeporteSelect("deporteTabla",     deportes);
  _initDeporteSelect("deporteReportes",  deportes);

  // ── 5. Select de equipos (formulario de deportistas) ─────────────────────
  try {
    const res = await window.authFetch(`${API_BASE}/equipos/`);
    const equipos = await res.json();
    if (!res.ok) return;

    const selectEquipo = document.getElementById("equipoId");
    if (selectEquipo) {
      const opciones = equipos
        .map((e) => `<option value="${e.id}">${e.nombre_equipo} — ${e.region} (${e.deporte})</option>`)
        .join("");
      selectEquipo.innerHTML =
        '<option value="">-- Selecciona un equipo --</option>' + opciones;
    }
  } catch (err) {
    console.error("Error cargando equipos:", err);
  }
}

// Convierte un <input id="X"> en un <select> con las 4 opciones de deporte
function _initDeporteSelect(inputId, deportes) {
  const original = document.getElementById(inputId);
  if (!original) return;
  // Evitar doble inicialización (ya es un select)
  if (original.tagName === "SELECT") return;

  const select = document.createElement("select");
  select.id        = inputId;
  select.name      = original.name || inputId;
  select.className = original.className;
  select.required  = original.required;

  select.innerHTML =
    '<option value="">-- Selecciona un deporte --</option>' +
    deportes
      .map(
        (d) =>
          `<option value="${d.nombre}">${d.nombre} &mdash; ${d.categoria}</option>`
      )
      .join("");

  original.replaceWith(select);
}
