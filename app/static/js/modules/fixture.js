// fixture.js

import { API_BASE } from "./config.js";
import { showMessage } from "./ui.js";

export async function generarFixture(event) {
  event.preventDefault();
  const deporte = document.getElementById("deporteFixture").value.trim();

  try {
    const res = await window.authFetch(
      `${API_BASE}/fixture/generar/${encodeURIComponent(deporte)}`,
      { method: "POST" },
    );
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error generando calendario");

    let msg = `✅ ${data.mensaje} — ${data.total_partidos} partidos generados`;
    if (data.partidos?.length) {
      const lista = data.partidos
        .map((p) => `<li class="py-0.5">${p.local} <span class="font-bold text-gray-500">vs</span> ${p.visitante} · ${p.fecha} ${p.hora}</li>`)
        .join("");
      msg += `<ul class="mt-2 ml-2 list-disc list-inside text-gray-700">${lista}</ul>`;
    }
    showMessage("fixtureResultado", msg, false);
  } catch (err) {
    showMessage("fixtureResultado", `❌ ${err.message}`);
  }
}

export async function consultarFixture(event) {
  event.preventDefault();
  const deporte = document.getElementById("deporteConsultar").value.trim();
  const contenedor = document.getElementById("fixtureListado");

  try {
    const res = await window.authFetch(
      `${API_BASE}/fixture/consultar/${encodeURIComponent(deporte)}`,
    );
    const partidos = await res.json();
    if (!res.ok) throw new Error("Error consultando calendario");

    if (partidos.length === 0) {
      contenedor.innerHTML = `<p class="text-gray-500 mt-2">No hay partidos para este deporte. Genera el calendario primero.</p>`;
      document.getElementById("resultadoCard").classList.add("hidden");
      return;
    }

    const filas = partidos.map((p) => {
      const resultado =
        p.resultado_local !== null && p.resultado_visitante !== null
          ? `<span class="font-bold">${p.resultado_local} – ${p.resultado_visitante}</span>`
          : `<span class="text-gray-400 italic">Pendiente</span>`;

      const esAdmin = localStorage.getItem("rol") === "admin";
      const accion =
        p.resultado_local !== null
          ? `<span class="text-green-600 font-medium text-xs">✓ Finalizado</span>`
          : esAdmin
            ? `<button
                 class="bg-orange-500 hover:bg-orange-600 text-white text-xs font-medium px-3 py-1 rounded-lg transition"
                 onclick="window.mostrarFormularioResultado(${p.id})"
               >Registrar resultado</button>`
            : `<span class="text-gray-400 text-xs italic">Solo lectura</span>`;

      return `
        <tr class="hover:bg-gray-50 border-b border-gray-100">
          <td class="px-3 py-2 text-gray-400 text-xs">#${p.id}</td>
          <td class="px-3 py-2 font-medium">${p.local}</td>
          <td class="px-3 py-2 text-center text-gray-400 text-xs">vs</td>
          <td class="px-3 py-2 font-medium">${p.visitante}</td>
          <td class="px-3 py-2 text-gray-600">${p.fecha} ${p.hora}</td>
          <td class="px-3 py-2 text-center">${resultado}</td>
          <td class="px-3 py-2 text-center">${accion}</td>
        </tr>`;
    }).join("");

    contenedor.innerHTML = `
      <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden mt-2">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">N°</th>
            <th class="px-3 py-2 text-left">Local</th>
            <th class="px-3 py-2"></th>
            <th class="px-3 py-2 text-left">Visitante</th>
            <th class="px-3 py-2 text-left">Fecha y hora</th>
            <th class="px-3 py-2 text-center">Resultado</th>
            <th class="px-3 py-2 text-center">Acción</th>
          </tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>`;

    document.getElementById("resultadoCard").classList.add("hidden");
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">❌ ${err.message}</p>`;
  }
}
