// equipos.js

import { API_BASE } from "./config.js";
import { showMessage } from "./ui.js";
import { cargarSugerencias } from "./autocomplete.js";

export async function registrarEquipo(event) {
  event.preventDefault();
  const pais = document.getElementById("pais").value.trim();
  const deporte = document.getElementById("deporteEquipo").value.trim();
  const nombre_equipo = document.getElementById("nombreEquipo").value.trim();

  try {
    const res = await window.authFetch(`${API_BASE}/equipos/`, {
      method: "POST",
      body: JSON.stringify({ pais, deporte, nombre_equipo }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al registrar");

    showMessage("equipoResultado", `✅ ${data.mensaje} (ID: ${data.id})`, false);
    document.getElementById("formEquipo").reset();
    cargarSugerencias(); // refrescar select y datalists
  } catch (err) {
    showMessage("equipoResultado", `❌ ${err.message}`);
  }
}

export async function listarEquipos() {
  const contenedor = document.getElementById("listaEquipos");
  try {
    const res = await window.authFetch(`${API_BASE}/equipos/`);
    const equipos = await res.json();
    if (!res.ok) throw new Error("Error obteniendo equipos");

    if (equipos.length === 0) {
      contenedor.innerHTML = `<p class="text-gray-500 text-sm mt-2">No hay equipos registrados aún.</p>`;
      return;
    }

    const filas = equipos.map((eq) => `
      <tr class="hover:bg-gray-50">
        <td class="px-3 py-2 text-gray-500 text-xs">${eq.id}</td>
        <td class="px-3 py-2 font-medium">${eq.nombre_equipo}</td>
        <td class="px-3 py-2">${eq.pais}</td>
        <td class="px-3 py-2">
          <span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">${eq.deporte}</span>
        </td>
      </tr>
    `).join("");

    contenedor.innerHTML = `
      <table class="w-full text-sm mt-3 border border-gray-100 rounded-lg overflow-hidden">
        <thead class="bg-gray-50 text-gray-600 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">ID</th>
            <th class="px-3 py-2 text-left">Equipo</th>
            <th class="px-3 py-2 text-left">País</th>
            <th class="px-3 py-2 text-left">Deporte</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">${filas}</tbody>
      </table>
    `;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">❌ ${err.message}</p>`;
  }
}
