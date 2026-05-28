// ui.js — utilidades de interfaz compartidas por todos los módulos

export function showMessage(containerId, msg, isError = true) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const cls = isError
    ? "bg-red-50 border border-red-200 text-red-700"
    : "bg-green-50 border border-green-200 text-green-700";

  container.innerHTML = `
    <div class="${cls} text-sm px-4 py-2.5 rounded-lg flex items-start justify-between gap-2">
      <span>${msg}</span>
      <button onclick="this.parentElement.parentElement.innerHTML=''"
        class="text-current opacity-50 hover:opacity-100 font-bold leading-none mt-0.5 flex-shrink-0">✕</button>
    </div>`;

  // Errores duran 10 s, éxitos 5 s
  const ms = isError ? 10000 : 5000;
  setTimeout(() => { if (container) container.innerHTML = ""; }, ms);
}

export function showLoader(visible) {
  const loader = document.getElementById("global-loader");
  if (!loader) return;
  visible ? loader.classList.remove("hidden") : loader.classList.add("hidden");
}

// Pone un botón en estado de carga y devuelve función para restaurarlo
export function btnLoading(btn, textoEspera = "Procesando...") {
  const original = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="opacity-70">${textoEspera}</span>`;
  return () => {
    btn.disabled = false;
    btn.innerHTML = original;
  };
}
