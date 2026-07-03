// fixture.js

import { API_BASE } from "./config.js";
import { showMessage, btnLoading } from "./ui.js";

function encodeValue(value) {
  return encodeURIComponent(String(value ?? ""));
}

export async function generarFixture(event) {
  event.preventDefault();
  const deporte = document.getElementById("deporteFixture").value.trim();
  if (!deporte) { showMessage("fixtureResultado", "Selecciona un deporte."); return; }

  const btn     = event.submitter;
  const restore = btnLoading(btn, "Generando...");

  try {
    const res  = await window.authFetch(
      `${API_BASE}/fixture/generar/${encodeURIComponent(deporte)}`,
      { method: "POST" },
    );
    const data = await res.json();

    if (!res.ok) {
      // Si ya existe, ofrecer opción de regenerar
      if (res.status === 409) {
        document.getElementById("fixtureResultado").innerHTML = `
          <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm px-4 py-3 rounded-lg">
            Ya existe un calendario para <strong>${deporte}</strong>.
            <button id="btnRegenerar"
              class="ml-2 bg-yellow-500 hover:bg-yellow-600 text-white text-xs font-semibold px-3 py-1 rounded-lg transition">
              Eliminar y regenerar
            </button>
          </div>`;
        document.getElementById("btnRegenerar").addEventListener("click", () =>
          _eliminarYRegererar(deporte)
        );
        return;
      }
      throw new Error(data.error || "Error generando el calendario");
    }

    let msg = `${data.mensaje} — ${data.total_partidos} partidos generados`;
    if (data.partidos?.length) {
      const lista = data.partidos
        .map(p => `<li class="py-0.5">${p.local} <span class="text-gray-400">vs</span> ${p.visitante} &nbsp;·&nbsp; ${p.fecha} ${p.hora}</li>`)
        .join("");
      msg += `<ul class="mt-2 ml-2 list-disc list-inside text-gray-700 text-xs">${lista}</ul>`;
    }
    showMessage("fixtureResultado", msg, false);
  } catch (err) {
    showMessage("fixtureResultado", err.message);
  } finally {
    restore();
  }
}

async function _eliminarYRegererar(deporte) {
  const btn     = document.getElementById("btnRegenerar");
  const restore = btnLoading(btn, "Procesando...");
  try {
    const del = await window.authFetch(
      `${API_BASE}/fixture/eliminar/${encodeURIComponent(deporte)}`,
      { method: "DELETE" },
    );
    if (!del.ok) throw new Error("No se pudo eliminar el calendario anterior");

    const gen  = await window.authFetch(
      `${API_BASE}/fixture/generar/${encodeURIComponent(deporte)}`,
      { method: "POST" },
    );
    const data = await gen.json();
    if (!gen.ok) throw new Error(data.error || "Error regenerando");

    showMessage("fixtureResultado", `Calendario generado nuevamente — ${data.total_partidos} partidos`, false);
  } catch (err) {
    showMessage("fixtureResultado", err.message);
  } finally {
    restore();
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
    if (!res.ok) throw new Error("Error consultando el calendario");

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

      const esAdmin = ["admin", "operador"].includes(localStorage.getItem("rol"));
      const accion =
        p.resultado_local !== null
          ? `<span class="text-green-600 font-medium text-xs">Registrado</span>`
          : esAdmin
            ? `<button
                 class="bg-orange-500 hover:bg-orange-600 text-white text-xs font-medium px-3 py-1 rounded-lg transition"
                 data-action="registrar-resultado"
                 data-id="${p.id}"
                 data-local="${encodeValue(p.local)}"
                 data-visitante="${encodeValue(p.visitante)}"
               >Registrar</button>`
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
    contenedor.innerHTML = `<p class="text-red-600 text-sm mt-2">Error: ${err.message}</p>`;
  }
}
