// deportistas.js

import { API_BASE } from "./config.js";
import { showMessage, btnLoading } from "./ui.js";

export async function inscribirDeportista(event) {
  event.preventDefault();
  const id_equipo  = parseInt(document.getElementById("equipoId").value);
  const nombre     = document.getElementById("nombreDeportista").value.trim();
  const apellido   = document.getElementById("apellidoDeportista").value.trim();
  const documento  = document.getElementById("documento").value.trim();

  if (!id_equipo) {
    showMessage("deportistaResultado", "Selecciona un equipo antes de continuar.");
    return;
  }

  const btn     = event.submitter;
  const restore = btnLoading(btn, "Inscribiendo...");

  try {
    const res = await window.authFetch(`${API_BASE}/deportistas/inscribir`, {
      method: "POST",
      body: JSON.stringify({ id_equipo, nombre, apellido, documento }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error en inscripción");

    showMessage("deportistaResultado", data.mensaje, false);
    event.target.reset();
    listarDeportistas(id_equipo); // refrescar lista del mismo equipo
  } catch (err) {
    showMessage("deportistaResultado", err.message);
  } finally {
    restore();
  }
}

export async function listarDeportistas(equipoId) {
  const contenedor = document.getElementById("listaDeportistas");
  if (!contenedor || !equipoId) return;

  contenedor.innerHTML = `<p class="text-gray-400 text-xs italic mt-2">Cargando...</p>`;

  try {
    const res         = await window.authFetch(`${API_BASE}/deportistas/equipo/${equipoId}`);
    const deportistas = await res.json();
    if (!res.ok) throw new Error("Error obteniendo deportistas");

    if (deportistas.length === 0) {
      contenedor.innerHTML = `
        <p class="text-gray-400 text-xs italic mt-2">Este equipo aún no tiene deportistas inscritos.</p>`;
      return;
    }

    const filas = deportistas.map((d, i) => `
      <tr class="border-b border-gray-100 hover:bg-gray-50">
        <td class="px-3 py-2 text-gray-400 text-xs text-center">${i + 1}</td>
        <td class="px-3 py-2 font-medium">${d.nombre} ${d.apellido}</td>
        <td class="px-3 py-2 text-gray-500 text-xs">${d.documento}</td>
      </tr>`).join("");

    contenedor.innerHTML = `
      <p class="text-xs text-gray-500 mt-3 mb-1 font-medium">
        ${deportistas.length} deportista${deportistas.length !== 1 ? "s" : ""} inscrito${deportistas.length !== 1 ? "s" : ""}:
      </p>
      <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden">
        <thead class="bg-gray-50 text-gray-500 text-xs">
          <tr>
            <th class="px-3 py-2 text-center w-8">#</th>
            <th class="px-3 py-2 text-left">Nombre completo</th>
            <th class="px-3 py-2 text-left">Documento</th>
          </tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>`;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-500 text-xs mt-2">Error: ${err.message}</p>`;
  }
}
