// autocomplete.js — carga sugerencias dinámicas y puebla el select de equipos

import { API_BASE } from "./config.js";

export async function cargarSugerencias() {
  try {
    const res = await window.authFetch(`${API_BASE}/equipos/`);
    const equipos = await res.json();
    if (!res.ok) return;

    const deportes = [...new Set(equipos.map((e) => e.deporte))];

    // Datalist de deportes (compartido por fixture, consulta y tabla)
    const deportesList = document.getElementById("deportesList");
    if (deportesList) {
      deportesList.innerHTML = deportes.map((d) => `<option value="${d}">`).join("");
    }

    // Select de equipos para el formulario de deportistas
    const selectEquipo = document.getElementById("equipoId");
    if (selectEquipo) {
      const opcionesEquipos = equipos
        .map((e) => `<option value="${e.id}">${e.nombre_equipo} (${e.pais} — ${e.deporte})</option>`)
        .join("");
      selectEquipo.innerHTML = '<option value="">-- Selecciona un equipo --</option>' + opcionesEquipos;
    }
  } catch (err) {
    console.error("Error cargando sugerencias:", err);
  }
}
