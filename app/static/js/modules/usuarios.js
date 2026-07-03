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
