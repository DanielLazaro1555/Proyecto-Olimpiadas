// ui.js — utilidades de interfaz compartidas por todos los módulos

export function showMessage(containerId, msg, isError = true) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const cls = isError
    ? "bg-red-50 border border-red-200 text-red-700"
    : "bg-green-50 border border-green-200 text-green-700";

  container.innerHTML = `<div class="${cls} text-sm px-4 py-2.5 rounded-lg">${msg}</div>`;

  setTimeout(() => {
    container.innerHTML = "";
  }, 5000);
}

export function showLoader(visible) {
  const loader = document.getElementById("global-loader");
  if (!loader) return;
  visible ? loader.classList.remove("hidden") : loader.classList.add("hidden");
}
