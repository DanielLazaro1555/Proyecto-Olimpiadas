function applyRoleBadge(rolEl, rol) {
  const rolLabel = {
    admin: "Admin",
    operador: "Operador",
    visualizador: "Visualizador",
  };
  const rolColor = {
    admin: "bg-amber-200 text-amber-950",
    operador: "bg-slate-200 text-slate-800",
    visualizador: "bg-teal-100 text-teal-900",
  };

  rolEl.textContent = rolLabel[rol] || rol;
  rolEl.className =
    `inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-semibold ${rolColor[rol] || rolColor.visualizador}`;
}

function initTabs() {
  const tabs = Array.from(document.querySelectorAll(".tab-btn"));
  const contents = Array.from(document.querySelectorAll(".tab-content"));

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabs.forEach((tab) => {
        tab.classList.remove("is-active");
        tab.setAttribute("aria-selected", "false");
      });

      contents.forEach((content) => content.classList.add("hidden"));

      btn.classList.add("is-active");
      btn.setAttribute("aria-selected", "true");
      document.getElementById(btn.dataset.tab)?.classList.remove("hidden");
    });
  });
}

function applyViewerRestrictions(rol) {
  if (rol !== "visualizador") {
    return;
  }

  document.getElementById("bannerViewer")?.classList.remove("hidden");
  document.getElementById("guiaPasos")?.classList.add("hidden");

  const formEquipo = document.getElementById("formEquipo");
  if (formEquipo) {
    formEquipo.classList.add("hidden");
    const notice = document.createElement("p");
    notice.className = "mb-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500";
    notice.textContent = "Solo operadores y administradores pueden registrar equipos.";
    formEquipo.parentNode.insertBefore(notice, formEquipo);
  }

  document.getElementById("cardInscribirDeportista")?.classList.add("hidden");
  document.getElementById("cardGenerarFixture")?.classList.add("hidden");
}

export function openResultForm(partidoId, local, visitante) {
  if (!["admin", "operador"].includes(localStorage.getItem("rol"))) {
    return;
  }

  document.getElementById("idPartido").value = partidoId;
  document.getElementById("partidoEquipos").textContent = `${local} vs ${visitante}`;
  document.getElementById("formResultado").reset();
  document.getElementById("golesLocal").placeholder = `Goles ${local}`;
  document.getElementById("golesVisitante").placeholder = `Goles ${visitante}`;

  const card = document.getElementById("resultadoCard");
  card.classList.remove("hidden");
  card.scrollIntoView({ behavior: "smooth", block: "center" });
}

export function initShell() {
  const username = localStorage.getItem("username") || "Usuario";
  const rol = localStorage.getItem("rol") || "visualizador";

  document.getElementById("navUsername").textContent = username;
  applyRoleBadge(document.getElementById("navRol"), rol);

  if (rol === "admin") {
    document.getElementById("tabAdminBtn")?.classList.remove("hidden");
  }

  applyViewerRestrictions(rol);
  initTabs();

  document.getElementById("logoutBtn")?.addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/login";
  });

  document.getElementById("cancelarResultado")?.addEventListener("click", () => {
    document.getElementById("resultadoCard").classList.add("hidden");
    document.getElementById("formResultado").reset();
    document.getElementById("partidoEquipos").textContent = "— vs —";
  });
}
