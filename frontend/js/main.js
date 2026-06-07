/* ═══════════════════════════════════════════════════════════════════════════
   main.js — Shared utilities, theme toggle, API config, toast, reveal
   ═══════════════════════════════════════════════════════════════════════════ */

// ── API Config ───────────────────────────────────────────────────────────────
// ¡IMPORTANTE! Reemplaza "https://TU-BACKEND.onrender.com" con la URL real de tu Web Service en Render
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
const isTunnel = window.location.hostname.includes("loca.lt") || window.location.hostname.includes("trycloudflare.com") || window.location.hostname.includes("ngrok.io");
const API_BASE = isLocalhost 
  ? "http://localhost:5000" 
  : (isTunnel ? window.location.origin : "https://proyectofinal-i2ch.onrender.com"); // <-- CAMBIA ESTO

async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) { const txt = await res.text(); throw new Error(txt || "Error " + res.status); }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "Error de red (" + res.status + ")" }));
    throw new Error(err.error || "Error de red (" + res.status + ")");
  }
  return res.json();
}

async function apiUpload(path, formData) {
  const res = await fetch(API_BASE + path, { method: "POST", body: formData });
  if (!res.ok) { const txt = await res.text(); throw new Error(txt || "Error " + res.status); }
  return res.json();
}

// ── Theme ────────────────────────────────────────────────────────────────────
const THEME_KEY = "linreg-theme";

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  document.querySelectorAll(".theme-toggle").forEach((btn) => {
    btn.innerHTML = theme === "dark" ? "☀️" : "🌙";
    btn.title = theme === "dark" ? "Modo claro" : "Modo oscuro";
  });
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  applyTheme(current === "dark" ? "light" : "dark");
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem(THEME_KEY) || "dark";
  applyTheme(saved);
  document.querySelectorAll(".theme-toggle").forEach((btn) => {
    btn.addEventListener("click", toggleTheme);
  });

  // Scroll reveal
  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    const obs = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add("visible")),
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => obs.observe(el));
  }

  // Navbar scroll shadow
  const navbar = document.querySelector(".navbar-custom");
  if (navbar) {
    window.addEventListener("scroll", () => {
      navbar.style.boxShadow = window.scrollY > 40 ? "0 4px 24px rgba(0,0,0,.35)" : "";
    });
  }
});

// ── Toast ────────────────────────────────────────────────────────────────────
function showToast(message, type = "info", duration = 3500) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  const toast = document.createElement("div");
  toast.className = `toast-custom ${type}`;
  toast.innerHTML = `<span style="font-size:1.1rem">${icons[type] || "ℹ️"}</span>
                     <span class="toast-msg">${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = "0"; toast.style.transform = "translateX(20px)"; toast.style.transition = ".3s"; setTimeout(() => toast.remove(), 320); }, duration);
}

// ── Loading overlay ──────────────────────────────────────────────────────────
function showLoading(text = "Procesando...") {
  let ov = document.getElementById("loading-overlay");
  if (!ov) {
    ov = document.createElement("div");
    ov.id = "loading-overlay";
    ov.className = "loading-overlay";
    ov.innerHTML = `<div class="spinner-ring"></div><p class="loading-text">${text}</p>`;
    document.body.appendChild(ov);
  } else {
    ov.querySelector(".loading-text").textContent = text;
  }
  ov.classList.add("active");
}

function hideLoading() {
  const ov = document.getElementById("loading-overlay");
  if (ov) ov.classList.remove("active");
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function fmt(n, decimals = 4) {
  return typeof n === "number" ? n.toFixed(decimals) : n;
}

function pct(n) {
  return typeof n === "number" ? (n * 100).toFixed(2) + "%" : n;
}

// Populate a <select> element
function populateSelect(selectEl, options, placeholder = "-- Seleccionar --") {
  selectEl.innerHTML = `<option value="">${placeholder}</option>`;
  options.forEach((opt) => {
    const o = document.createElement("option");
    o.value = typeof opt === "object" ? opt.value : opt;
    o.textContent = typeof opt === "object" ? opt.label : opt;
    selectEl.appendChild(o);
  });
}

// Build a table from array of objects
function buildTable(container, rows, columns) {
  if (!rows || rows.length === 0) { container.innerHTML = "<p class='text-muted text-center py-3'>Sin datos</p>"; return; }
  const cols = columns || Object.keys(rows[0]);
  let html = `<div style="overflow-x:auto"><table class="table-custom"><thead><tr>`;
  cols.forEach((c) => (html += `<th>${c}</th>`));
  html += `</tr></thead><tbody>`;
  rows.forEach((row) => {
    html += "<tr>";
    cols.forEach((c) => (html += `<td>${row[c] ?? ""}</td>`));
    html += "</tr>";
  });
  html += "</tbody></table></div>";
  container.innerHTML = html;
}
