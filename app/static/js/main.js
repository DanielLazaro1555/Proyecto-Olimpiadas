// main.js — punto de entrada principal

import { registrarEquipo, listarEquipos, eliminarEquipo } from "./modules/equipos.js";
import { inscribirDeportista, listarDeportistas } from "./modules/deportistas.js";
import { generarFixture, consultarFixture } from "./modules/fixture.js";
import { registrarResultado, mostrarTabla } from "./modules/partidos.js";
import { cargarSugerencias } from "./modules/autocomplete.js";
import { registrarUsuario, listarUsuarios, eliminarUsuario } from "./modules/usuarios.js";

// authFetch: fetch con token JWT incluido automáticamente
window.authFetch = async function (url, options = {}) {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "/login";
    throw new Error("No autenticado");
  }
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (res.status === 401) {
    localStorage.clear();
    window.location.href = "/login";
    throw new Error("Sesión expirada");
  }
  return res;
};

// Exponer funciones globales (llamadas desde onclick en tablas dinámicas)
window.eliminarUsuario = eliminarUsuario;
window.eliminarEquipo  = eliminarEquipo;

document.addEventListener("DOMContentLoaded", () => {
  if (!localStorage.getItem("token")) {
    window.location.href = "/login";
    return;
  }

  // Formularios de gestión
  document.getElementById("formEquipo")?.addEventListener("submit", registrarEquipo);
  document.getElementById("btnListarEquipos")?.addEventListener("click", listarEquipos);
  document.getElementById("formDeportista")?.addEventListener("submit", inscribirDeportista);

  // Al cambiar el equipo en el select, cargar sus deportistas automáticamente
  document.getElementById("equipoId")?.addEventListener("change", (e) => {
    const id = parseInt(e.target.value);
    listarDeportistas(id || null);
  });

  // Formularios de competencia
  document.getElementById("formFixture")?.addEventListener("submit", generarFixture);
  document.getElementById("formConsultarFixture")?.addEventListener("submit", consultarFixture);
  document.getElementById("formResultado")?.addEventListener("submit", registrarResultado);

  // Tabla de clasificación
  document.getElementById("formTabla")?.addEventListener("submit", mostrarTabla);

  // Administración (solo admin)
  document.getElementById("formUsuario")?.addEventListener("submit", registrarUsuario);
  document.getElementById("btnRefrescarUsuarios")?.addEventListener("click", listarUsuarios);

  // Cargar sugerencias (selects de equipos y deportes)
  cargarSugerencias();

  // Si es admin, cargar lista de usuarios al iniciar
  if (localStorage.getItem("rol") === "admin") {
    listarUsuarios();
  }
});
