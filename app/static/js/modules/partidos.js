// partidos.js

import { API_BASE } from "./config.js";
import { showMessage } from "./ui.js";

export async function registrarResultado(event) {
  event.preventDefault();
  const id_partido = parseInt(document.getElementById("idPartido").value);
  const goles_local = parseInt(document.getElementById("golesLocal").value);
  const goles_visitante = parseInt(document.getElementById("golesVisitante").value);

  try {
    const res = await window.authFetch(`${API_BASE}/partidos/resultado`, {
      method: "POST",
      body: JSON.stringify({ id_partido, goles_local, goles_visitante }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al registrar resultado");

    showMessage("resultadoRegistro", `✅ ${data.mensaje}`, false);
    document.getElementById("formResultado").reset();
    document.getElementById("resultadoCard").classList.add("hidden");

    // Refrescar la tabla de partidos si hay deporte consultado
    const deporteConsultar = document.getElementById("deporteConsultar")?.value;
    if (deporteConsultar) {
      document.getElementById("formConsultarFixture")?.dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true }),
      );
    }
  } catch (err) {
    showMessage("resultadoRegistro", `❌ ${err.message}`);
  }
}

export async function mostrarTabla(event) {
  event.preventDefault();
  const deporte = document.getElementById("deporteTabla").value.trim();
  const contenedor = document.getElementById("tablaPosiciones");

  try {
    const res = await window.authFetch(
      `${API_BASE}/partidos/tabla/${encodeURIComponent(deporte)}`,
    );
    const tabla = await res.json();
    if (!res.ok) throw new Error("Error obteniendo clasificación");

    if (tabla.length === 0) {
      contenedor.innerHTML = `<p class="text-gray-500 mt-2">No hay datos para este deporte. Registra algunos resultados primero.</p>`;
      return;
    }

    const filas = tabla.map((row, i) => {
      const medalla = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `${i + 1}`;
      return `
        <tr class="${i < 3 ? "bg-yellow-50" : "hover:bg-gray-50"} border-b border-gray-100">
          <td class="px-3 py-2 text-center font-bold">${medalla}</td>
          <td class="px-3 py-2 font-semibold">${row.equipo_nombre}</td>
          <td class="px-3 py-2 text-center">${row.pj}</td>
          <td class="px-3 py-2 text-center text-green-700 font-medium">${row.pg}</td>
          <td class="px-3 py-2 text-center text-gray-500">${row.pe}</td>
          <td class="px-3 py-2 text-center text-red-500">${row.pp}</td>
          <td class="px-3 py-2 text-center">${row.gf}</td>
          <td class="px-3 py-2 text-center">${row.gc}</td>
          <td class="px-3 py-2 text-center">${row.dg}</td>
          <td class="px-3 py-2 text-center font-bold text-blue-700 text-base">${row.puntos}</td>
        </tr>`;
    }).join("");

    contenedor.innerHTML = `
      <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-center">#</th>
            <th class="px-3 py-2 text-left">Equipo</th>
            <th class="px-3 py-2 text-center" title="Partidos Jugados">PJ</th>
            <th class="px-3 py-2 text-center" title="Partidos Ganados">PG</th>
            <th class="px-3 py-2 text-center" title="Partidos Empatados">PE</th>
            <th class="px-3 py-2 text-center" title="Partidos Perdidos">PP</th>
            <th class="px-3 py-2 text-center" title="Goles a Favor">GF</th>
            <th class="px-3 py-2 text-center" title="Goles en Contra">GC</th>
            <th class="px-3 py-2 text-center" title="Diferencia de Goles">DG</th>
            <th class="px-3 py-2 text-center" title="Puntos totales">Pts</th>
          </tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>
      <p class="text-xs text-gray-400 mt-2">* Pasa el cursor sobre las siglas para ver su significado</p>`;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">❌ ${err.message}</p>`;
  }
}
