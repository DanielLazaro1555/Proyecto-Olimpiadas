// deportistas.js

import { API_BASE } from "./config.js";
import { showMessage } from "./ui.js";

export async function inscribirDeportista(event) {
  event.preventDefault();
  const id_equipo = parseInt(document.getElementById("equipoId").value);
  const nombre = document.getElementById("nombreDeportista").value.trim();
  const apellido = document.getElementById("apellidoDeportista").value.trim();
  const documento = document.getElementById("documento").value.trim();

  if (!id_equipo) {
    showMessage("deportistaResultado", "❌ Selecciona un equipo antes de continuar.");
    return;
  }

  try {
    const res = await window.authFetch(`${API_BASE}/deportistas/inscribir`, {
      method: "POST",
      body: JSON.stringify({ id_equipo, nombre, apellido, documento }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Error en inscripción");

    showMessage(
      "deportistaResultado",
      `✅ ${data.mensaje} (ID deportista: ${data.id_deportista})`,
      false,
    );
    document.getElementById("formDeportista").reset();
  } catch (err) {
    showMessage("deportistaResultado", `❌ ${err.message}`);
  }
}
