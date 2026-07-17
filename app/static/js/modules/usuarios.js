// usuarios.js — gestión de usuarios (solo admin)

import { API_BASE } from "./config.js";
import { showMessage } from "./ui.js";

function encodeValue(value) {
  return encodeURIComponent(String(value ?? ""));
}

export async function registrarUsuario(event) {
  event.preventDefault();
  const username = document.getElementById("nuevoUsername").value.trim();
  const password = document.getElementById("nuevoPassword").value;
  const rol      = document.getElementById("nuevoRol").value;

  try {
    const res = await window.authFetch(`${API_BASE}/auth/registro`, {
      method: "POST",
      body: JSON.stringify({ username, password, rol }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al registrar");

    showMessage("usuarioResultado", data.mensaje, false);
    document.getElementById("formUsuario").reset();
    listarUsuarios();
  } catch (err) {
    showMessage("usuarioResultado", err.message);
  }
}

export async function listarUsuarios() {
  const contenedor = document.getElementById("listaUsuarios");
  try {
    const res = await window.authFetch(`${API_BASE}/auth/usuarios`);
    const usuarios = await res.json();
    if (!res.ok) throw new Error(usuarios.error || "Error obteniendo usuarios");

    const miId = _miId();

    const filas = usuarios.map((u) => {
      const esSoy = u.id === miId;
      const badgeColor = u.rol === "admin"
        ? "bg-yellow-100 text-yellow-800"
        : u.rol === "operador"
          ? "bg-green-100 text-green-800"
          : "bg-blue-100 text-blue-700";
      const btnEliminar = esSoy
        ? `<span class="text-xs text-gray-400 italic">Tu cuenta</span>`
        : `<button
             data-action="eliminar-usuario"
             data-id="${u.id}"
             data-username="${encodeValue(u.username)}"
             class="bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1 rounded-lg transition"
           >Eliminar</button>`;

      return `
        <tr class="border-b border-gray-100 hover:bg-gray-50">
          <td class="px-3 py-2 text-gray-400 text-xs">${u.id}</td>
          <td class="px-3 py-2 font-medium">${u.username}${esSoy ? ' <span class="text-xs text-gray-400">(tú)</span>' : ""}</td>
          <td class="px-3 py-2">
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${badgeColor}">${u.rol}</span>
          </td>
          <td class="px-3 py-2 text-center">${btnEliminar}</td>
        </tr>`;
    }).join("");

    contenedor.innerHTML = `
      <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden mt-2">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="px-3 py-2 text-left">ID</th>
            <th class="px-3 py-2 text-left">Usuario</th>
            <th class="px-3 py-2 text-left">Rol</th>
            <th class="px-3 py-2 text-center">Acción</th>
          </tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>`;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">Error: ${err.message}</p>`;
  }
}

export async function eliminarUsuario(id, username) {
  if (!confirm(`¿Eliminar al usuario "${username}"? Esta acción no se puede deshacer.`)) return;
  try {
    const res = await window.authFetch(`${API_BASE}/auth/usuarios/${id}`, {
      method: "DELETE",
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error al eliminar");
    showMessage("usuarioResultado", data.mensaje, false);
    listarUsuarios();
  } catch (err) {
    showMessage("usuarioResultado", err.message);
  }
}

function _miId() {
  try {
    const token = localStorage.getItem("token");
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_id;
  } catch {
    return null;
  }
}

export async function listarAuditoria() {
  const contenedor = document.getElementById("listaAuditorias");
  if (!contenedor) return;
  try {
    const res = await window.authFetch(`${API_BASE}/auth/auditoria`);
    const auditorias = await res.json();
    if (!res.ok) throw new Error(auditorias.error || "Error obteniendo auditoría");

    if (auditorias.length === 0) {
      contenedor.innerHTML = `<p class="text-gray-500 text-sm mt-2">No hay registros de auditoría aún.</p>`;
      return;
    }

    const filas = auditorias.map((a) => {
      const badgeMetodo = a.metodo === "DELETE"
        ? "bg-red-100 text-red-800"
        : "bg-blue-100 text-blue-800";
      
      const badgeStatus = a.status_code >= 200 && a.status_code < 300
        ? "bg-green-100 text-green-800"
        : "bg-orange-100 text-orange-800";

      let payloadTruncated = a.payload || "";
      if (payloadTruncated.length > 50) {
        payloadTruncated = `<span title="${encodeValue(payloadTruncated)}">${payloadTruncated.slice(0, 47)}...</span>`;
      }

      return `
        <tr class="border-b border-gray-100 hover:bg-gray-50 text-xs">
          <td class="px-2 py-1.5 text-gray-400">${a.id}</td>
          <td class="px-2 py-1.5 whitespace-nowrap text-gray-600">${a.fecha_hora}</td>
          <td class="px-2 py-1.5 font-medium">${a.username}</td>
          <td class="px-2 py-1.5 text-gray-500">${a.rol}</td>
          <td class="px-2 py-1.5">
            <span class="font-bold px-1.5 py-0.5 rounded text-[10px] uppercase ${badgeMetodo}">${a.metodo}</span>
          </td>
          <td class="px-2 py-1.5 font-mono text-gray-700">${a.ruta}</td>
          <td class="px-2 py-1.5 max-w-[200px] truncate text-gray-500 font-mono text-[11px]">${payloadTruncated}</td>
          <td class="px-2 py-1.5 text-center">
            <span class="font-semibold px-2 py-0.5 rounded-full ${badgeStatus}">${a.status_code}</span>
          </td>
        </tr>`;
    }).join("");

    contenedor.innerHTML = `
      <table class="w-full text-sm border border-gray-100 rounded-lg overflow-hidden mt-2">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="px-2 py-1.5 text-left">ID</th>
            <th class="px-2 py-1.5 text-left">Fecha/Hora</th>
            <th class="px-2 py-1.5 text-left">Usuario</th>
            <th class="px-2 py-1.5 text-left">Rol</th>
            <th class="px-2 py-1.5 text-left">Método</th>
            <th class="px-2 py-1.5 text-left">Ruta</th>
            <th class="px-2 py-1.5 text-left">Payload</th>
            <th class="px-2 py-1.5 text-center">Estado</th>
          </tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>`;
  } catch (err) {
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">Error: ${err.message}</p>`;
  }
}
