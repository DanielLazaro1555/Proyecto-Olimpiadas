// notificaciones.js — historial de notificaciones (solo admin)

import { API_BASE } from "./config.js";

const ESTADO_BADGE = {
  enviado: "bg-green-100 text-green-800",
  simulado: "bg-blue-100 text-blue-700",
  fallido: "bg-red-100 text-red-800",
};

export async function listarNotificaciones() {
  const contenedor = document.getElementById("listaNotificaciones");
  if (!contenedor) return;

  try {
    const res = await window.authFetch(`${API_BASE}/notificaciones/`);
    const notificaciones = await res.json();
    if (!res.ok) throw new Error(notificaciones.error || "Error obteniendo notificaciones");

    if (notificaciones.length === 0) {
      contenedor.innerHTML = `<p class="text-gray-500 text-sm mt-2">No hay notificaciones registradas aún.</p>`;
      return;
    }

    const filas = notificaciones.map((n) => {
      const badge = ESTADO_BADGE[n.estado] || "bg-gray-100 text-gray-700";
      return `
        <tr class="border-b border-gray-100 hover:bg-gray-50 text-xs">
          <td class="px-2 py-1.5 text-gray-400">${n.id}</td>
          <td class="px-2 py-1.5 whitespace-nowrap text-gray-600">${n.fecha_hora}</td>
          <td class="px-2 py-1.5 font-medium">${n.tipo}</td>
          <td class="px-2 py-1.5 text-gray-500">${n.canal}</td>
          <td class="px-2 py-1.5 text-gray-600">${n.destinatario}</td>
          <td class="px-2 py-1.5 text-gray-700">${n.asunto}</td>
          <td class="px-2 py-1.5 text-center">
            <span class="font-semibold px-2 py-0.5 rounded-full ${badge}">${n.estado}</span>
          </td>
        </tr>`;
    }).join("");

    contenedor.innerHTML = `
      <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden mt-2">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="px-2 py-1.5 text-left">ID</th>
            <th class="px-2 py-1.5 text-left">Fecha/Hora</th>
            <th class="px-2 py-1.5 text-left">Tipo</th>
            <th class="px-2 py-1.5 text-left">Canal</th>
            <th class="px-2 py-1.5 text-left">Destinatario</th>
            <th class="px-2 py-1.5 text-left">Asunto</th>
            <th class="px-2 py-1.5 text-center">Estado</th>
          </tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>`;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">Error: ${err.message}</p>`;
  }
}
