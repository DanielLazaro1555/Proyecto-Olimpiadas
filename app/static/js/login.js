const passwordInput = document.getElementById("password");
const togglePasswordBtn = document.getElementById("togglePassword");
const loginForm = document.getElementById("loginForm");

togglePasswordBtn?.addEventListener("click", () => {
  passwordInput.type = passwordInput.type === "password" ? "text" : "password";
});

loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  const username = document.getElementById("username").value.trim();
  const password = passwordInput.value;
  const errorMsg = document.getElementById("errorMsg");
  const submitBtn = document.getElementById("submitBtn");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");

  errorMsg.classList.add("hidden");
  submitBtn.disabled = true;
  btnText.textContent = "Ingresando...";
  btnSpinner.classList.remove("hidden");

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Credenciales inválidas");
    }

    localStorage.setItem("token", data.token);
    localStorage.setItem("rol", data.rol);
    localStorage.setItem("username", data.username);
    window.location.href = "/";
  } catch (error) {
    errorMsg.textContent = error.message || "Error de conexión. Verifica que el servidor esté activo.";
    errorMsg.classList.remove("hidden");
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = "Ingresar";
    btnSpinner.classList.add("hidden");
  }
});
