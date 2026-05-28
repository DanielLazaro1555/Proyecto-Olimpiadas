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

    const dgStr = (dg) =>
      dg > 0 ? `<span class="text-green-600 font-medium">+${dg}</span>`
             : dg < 0 ? `<span class="text-red-500 font-medium">${dg}</span>`
             : `<span class="text-gray-400">0</span>`;

    const rowStyles = [
      "bg-yellow-50 border-l-4 border-yellow-400",   // 1°
      "bg-gray-50  border-l-4 border-gray-300",       // 2°
      "bg-orange-50 border-l-4 border-orange-300",    // 3°
    ];

    const filas = tabla.map((row, i) => {
      const pos    = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : `${i + 1}°`;
      const estilo = rowStyles[i] ?? "hover:bg-gray-50 border-l-4 border-transparent";
      const sinJuegos = row.pj === 0;

      return `
        <tr class="${estilo} border-b border-gray-100 transition-colors">
          <td class="px-4 py-3 text-center text-lg">${pos}</td>
          <td class="px-4 py-3">
            <span class="font-semibold text-gray-800">${row.equipo_nombre}</span>
            ${sinJuegos ? '<span class="ml-2 text-xs text-gray-400 italic">sin partidos</span>' : ""}
          </td>
          <td class="px-4 py-3 text-center text-gray-600">${row.pj}</td>
          <td class="px-4 py-3 text-center font-medium text-green-700">${row.pg}</td>
          <td class="px-4 py-3 text-center text-gray-500">${row.pe}</td>
          <td class="px-4 py-3 text-center text-red-500">${row.pp}</td>
          <td class="px-4 py-3 text-center text-gray-600">${row.gf}</td>
          <td class="px-4 py-3 text-center text-gray-600">${row.gc}</td>
          <td class="px-4 py-3 text-center">${dgStr(row.dg)}</td>
          <td class="px-4 py-3 text-center">
            <span class="inline-block bg-blue-600 text-white font-bold text-sm px-3 py-0.5 rounded-full min-w-[2rem]">
              ${row.puntos}
            </span>
          </td>
        </tr>`;
    }).join("");

    contenedor.innerHTML = `
      <div class="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-800 text-white text-xs">
              <th class="px-4 py-3 text-center w-10">Pos.</th>
              <th class="px-4 py-3 text-left">Equipo</th>
              <th class="px-4 py-3 text-center" title="Partidos jugados">J</th>
              <th class="px-4 py-3 text-center text-green-300" title="Partidos ganados">G</th>
              <th class="px-4 py-3 text-center text-yellow-300" title="Partidos empatados">E</th>
              <th class="px-4 py-3 text-center text-red-400" title="Partidos perdidos">P</th>
              <th class="px-4 py-3 text-center" title="Goles a favor">GF</th>
              <th class="px-4 py-3 text-center" title="Goles en contra">GC</th>
              <th class="px-4 py-3 text-center" title="Diferencia de goles">Dif.</th>
              <th class="px-4 py-3 text-center text-blue-300">Pts</th>
            </tr>
            <tr class="bg-gray-700 text-gray-300 text-xs">
              <td colspan="2" class="px-4 py-1 text-gray-400">Clasificación · ${deporte}</td>
              <td class="px-4 py-1 text-center text-gray-400">Jugados</td>
              <td class="px-4 py-1 text-center text-green-400">Ganados</td>
              <td class="px-4 py-1 text-center text-yellow-400">Empates</td>
              <td class="px-4 py-1 text-center text-red-400">Perdidos</td>
              <td class="px-4 py-1 text-center text-gray-400">A favor</td>
              <td class="px-4 py-1 text-center text-gray-400">En contra</td>
              <td class="px-4 py-1 text-center text-gray-400">Diferencia</td>
              <td class="px-4 py-1 text-center text-blue-400">Puntos</td>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">${filas}</tbody>
        </table>
      </div>
      <div class="flex flex-wrap gap-4 mt-3 text-xs text-gray-500">
        <span>🟢 <b>Victoria</b>: 3 pts</span>
        <span>🟡 <b>Empate</b>: 1 pt</span>
        <span>🔴 <b>Derrota</b>: 0 pts</span>
        <span class="text-gray-400">Orden: puntos → diferencia de goles → goles a favor</span>
      </div>`;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">❌ ${err.message}</p>`;
  }
}
