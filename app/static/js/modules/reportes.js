// reportes.js — tab de Reportes: goleadores y estadísticas con gráficos (Chart.js)

import { API_BASE } from "./config.js";
import { showMessage } from "./ui.js";

const COLOR_GOLES = "#2a78d6";
const COLOR_JUGADOS = "#2a78d6";
const COLOR_PENDIENTES = "#c3c2b7";
const COLOR_GRID = "#e1e0d9";

let chartGoleadores = null;
let chartPartidos = null;

export async function consultarReportes(event) {
  event.preventDefault();
  const deporte = document.getElementById("deporteReportes").value.trim();
  if (!deporte) {
    showMessage("reportesEstadisticas", "Selecciona un deporte.");
    return;
  }

  try {
    const [resGoleadores, resEstadisticas] = await Promise.all([
      window.authFetch(`${API_BASE}/reportes/goleadores/${encodeURIComponent(deporte)}?limite=10`),
      window.authFetch(`${API_BASE}/reportes/estadisticas/${encodeURIComponent(deporte)}`),
    ]);
    const goleadores = await resGoleadores.json();
    const estadisticas = await resEstadisticas.json();
    if (!resGoleadores.ok || !resEstadisticas.ok) {
      throw new Error("Error obteniendo los reportes");
    }

    renderEstadisticas(estadisticas);
    renderGoleadores(goleadores);
    renderPartidosChart(estadisticas);
  } catch (err) {
    document.getElementById("reportesEstadisticas").innerHTML =
      `<p class="text-red-600 text-sm">Error: ${err.message}</p>`;
  }
}

function renderEstadisticas(estadisticas) {
  const tiles = [
    { label: "Partidos totales", value: estadisticas.partidos_totales },
    { label: "Jugados", value: estadisticas.partidos_jugados },
    { label: "Pendientes", value: estadisticas.partidos_pendientes },
    { label: "Goles totales", value: estadisticas.total_goles },
    { label: "Promedio goles/partido", value: estadisticas.promedio_goles_por_partido },
  ];

  const tilesHtml = tiles.map((t) => `
    <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3">
      <p class="text-xs text-gray-500">${t.label}</p>
      <p class="mt-1 text-2xl font-bold text-gray-800">${t.value ?? "—"}</p>
    </div>`).join("");

  const liderHtml = estadisticas.equipo_lider ? `
    <div class="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3">
      <p class="text-xs text-gray-500">Equipo líder</p>
      <p class="mt-1 text-lg font-bold text-gray-800">${estadisticas.equipo_lider}</p>
    </div>` : "";

  document.getElementById("reportesEstadisticas").innerHTML = tilesHtml + liderHtml;
}

function renderGoleadores(goleadores) {
  const vacio = document.getElementById("reportesGoleadoresVacio");
  const canvas = document.getElementById("chartGoleadores");

  if (!goleadores.length) {
    vacio.textContent = "Aún no hay goleadores registrados para este deporte.";
    canvas.classList.add("hidden");
    chartGoleadores?.destroy();
    chartGoleadores = null;
    return;
  }

  vacio.textContent = "";
  canvas.classList.remove("hidden");

  const labels = goleadores.map((g) => `${g.nombre} ${g.apellido}`);
  const datos = goleadores.map((g) => g.goles);

  chartGoleadores?.destroy();
  chartGoleadores = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Goles",
        data: datos,
        backgroundColor: COLOR_GOLES,
        borderRadius: 4,
        maxBarThickness: 28,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: COLOR_GRID } },
        y: { grid: { display: false } },
      },
    },
  });
}

function renderPartidosChart(estadisticas) {
  const canvas = document.getElementById("chartPartidos");
  chartPartidos?.destroy();
  chartPartidos = new Chart(canvas, {
    type: "bar",
    data: {
      labels: ["Jugados", "Pendientes"],
      datasets: [{
        data: [estadisticas.partidos_jugados, estadisticas.partidos_pendientes],
        backgroundColor: [COLOR_JUGADOS, COLOR_PENDIENTES],
        borderRadius: 4,
        maxBarThickness: 48,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: COLOR_GRID } },
        x: { grid: { display: false } },
      },
    },
  });
}
