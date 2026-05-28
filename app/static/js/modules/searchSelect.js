// searchSelect.js
// Convierte un <input type="hidden" id="X"> en un select con búsqueda en tiempo real.
// El ID original queda en el hidden input, así el resto del código no cambia nada.

export function initSearchSelect(hiddenInputId, options, placeholder = "Escribe para filtrar...") {
  const hidden = document.getElementById(hiddenInputId);
  if (!hidden) return;
  // Evitar doble inicialización
  if (hidden.parentElement.classList.contains("ss-wrapper")) return;

  // Construir wrapper
  const wrapper = document.createElement("div");
  wrapper.className = "relative ss-wrapper";

  // Input visible (solo lectura mientras no filtra)
  const display = document.createElement("input");
  display.type = "text";
  display.placeholder = placeholder;
  display.autocomplete = "off";
  display.spellcheck = false;
  display.className = hidden.className;

  // Dropdown
  const dropdown = document.createElement("div");
  dropdown.className =
    "absolute z-20 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-52 overflow-y-auto hidden";

  // Reemplazar el hidden input con la estructura
  hidden.type = "hidden";
  hidden.className = "";
  hidden.removeAttribute("placeholder");
  hidden.removeAttribute("required");

  hidden.parentNode.insertBefore(wrapper, hidden);
  wrapper.appendChild(display);
  wrapper.appendChild(dropdown);
  wrapper.appendChild(hidden);

  // Renderizar lista filtrada
  function render(list) {
    if (!list.length) {
      dropdown.innerHTML =
        '<p class="px-3 py-2 text-sm text-gray-400 italic">Sin resultados</p>';
    } else {
      dropdown.innerHTML = list
        .map(
          (opt) =>
            `<div class="px-3 py-2 text-sm cursor-pointer hover:bg-blue-50 hover:text-blue-700 transition-colors" data-val="${opt}">${opt}</div>`
        )
        .join("");
    }
    dropdown.classList.remove("hidden");
  }

  // Abrir al hacer foco
  display.addEventListener("focus", () => render(options));

  // Filtrar al escribir
  display.addEventListener("input", () => {
    const q = display.value.trim().toLowerCase();
    hidden.value = ""; // invalida hasta que se seleccione
    const filtered = q ? options.filter((o) => o.toLowerCase().includes(q)) : options;
    render(filtered);
  });

  // Seleccionar opción (mousedown para que no se dispare blur antes)
  dropdown.addEventListener("mousedown", (e) => {
    const item = e.target.closest("[data-val]");
    if (!item) return;
    e.preventDefault();
    display.value = item.dataset.val;
    hidden.value = item.dataset.val;
    dropdown.classList.add("hidden");
  });

  // Al perder foco: si el texto no coincide exactamente, limpiar
  display.addEventListener("blur", () => {
    setTimeout(() => {
      dropdown.classList.add("hidden");
      if (!options.includes(display.value)) {
        display.value = "";
        hidden.value = "";
      }
    }, 150);
  });

  // Teclado: Escape cierra
  display.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      dropdown.classList.add("hidden");
      display.blur();
    }
  });

  return {
    getValue: () => hidden.value,
    setValue(val) {
      display.value = val;
      hidden.value = val;
    },
    reset() {
      display.value = "";
      hidden.value = "";
    },
  };
}
