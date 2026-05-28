// equipos.js

import { API_BASE } from "./config.js";
import { showMessage, btnLoading } from "./ui.js";
import { cargarSugerencias } from "./autocomplete.js";

export async function registrarEquipo(event) {
  event.preventDefault();
  const region       = document.getElementById("region").value.trim();
  const deporte      = document.getElementById("deporteEquipo").value.trim();
  const nombre_equipo = document.getElementById("nombreEquipo").value.trim();

  if (!region)  { showMessage("equipoResultado", "❌ Selecciona una región."); return; }
  if (!deporte) { showMessage("equipoResultado", "❌ Selecciona un deporte."); return; }

  const btn     = event.submitter;
  const restore = btnLoading(btn, "Registrando...");

  try {
    const res = await window.authFetch(`${API_BASE}/equipos/`, {
      method: "POST",
      body: JSON.stringify({ region, deporte, nombre_equipo }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al registrar");

    showMessage("equipoResultado", `✅ ${data.mensaje}`, false);
    event.target.reset();
    cargarSugerencias();
    listarEquipos(); // actualizar lista automáticamente
  } catch (err) {
    showMessage("equipoResultado", `❌ ${err.message}`);
  } finally {
    restore();
  }
}

export async function listarEquipos() {
  const contenedor = document.getElementById("listaEquipos");
  if (!contenedor) return;

  try {
    const res    = await window.authFetch(`${API_BASE}/equipos/`);
    const equipos = await res.json();
    if (!res.ok) throw new Error("Error obteniendo equipos");

    if (equipos.length === 0) {
      contenedor.innerHTML = `
        <p class="text-gray-400 text-sm mt-3 italic">Aún no hay equipos registrados.</p>`;
      return;
    }

    const puedeEliminar = ["admin", "operador"].includes(localStorage.getItem("rol"));

    // Agrupar por deporte para mejor lectura
    const porDeporte = {};
    equipos.forEach(eq => {
      if (!porDeporte[eq.deporte]) porDeporte[eq.deporte] = [];
      porDeporte[eq.deporte].push(eq);
    });

    const tablas = Object.entries(porDeporte).map(([deporte, lista]) => {
      const filas = lista.map(eq => `
        <tr class="hover:bg-gray-50 border-b border-gray-100">
          <td class="px-3 py-2 font-medium text-gray-800">${eq.nombre_equipo}</td>
          <td class="px-3 py-2 text-gray-600">${eq.region}</td>
          <td class="px-3 py-2 text-center">
            ${puedeEliminar
              ? `<button onclick="window.eliminarEquipo(${eq.id}, '${eq.nombre_equipo}')"
                   class="bg-red-100 hover:bg-red-500 text-red-600 hover:text-white text-xs px-3 py-1 rounded-lg transition">
                   Eliminar
                 </button>`
              : ""}
          </td>
        </tr>`).join("");

      return `
        <div class="mb-4">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">${deporte}</p>
          <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden">
            <thead class="bg-gray-50 text-gray-500 text-xs">
              <tr>
                <th class="px-3 py-2 text-left">Nombre del equipo</th>
                <th class="px-3 py-2 text-left">Región</th>
                <th class="px-3 py-2 text-center w-24"></th>
              </tr>
            </thead>
            <tbody>${filas}</tbody>
          </table>
        </div>`;
    }).join("");

    contenedor.innerHTML = tablas;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">❌ ${err.message}</p>`;
  }
}

export async function eliminarEquipo(id, nombre) {
  if (!confirm(`¿Eliminar el equipo "${nombre}"?\nEsta acción no se puede deshacer.`)) return;
  try {
    const res  = await window.authFetch(`${API_BASE}/equipos/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al eliminar");
    showMessage("equipoResultado", `✅ ${data.mensaje}`, false);
    listarEquipos();
    cargarSugerencias();
  } catch (err) {
    showMessage("equipoResultado", `❌ ${err.message}`);
  }
}
