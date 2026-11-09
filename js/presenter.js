import { mountStage } from "./stage.js";
import { SLIDES } from "./slides/index.js?v=5";
import { SECTION_LABELS } from "./meta.js";

const N = SLIDES.length;
const $ = id => document.getElementById(id);

const viewport = $("viewport");
const stage = $("stage");
const toc = $("toc");
const live = $("live");
const chrome = $("chrome");
const counter = $("counter");
const progress = $("progress");

let current = 1;
let tocOpen = false;
let lastRendered = 0;

const clamp = n => Math.min(Math.max(n | 0, 1), Math.max(N, 1));

function buildToc() {
  if (!N) return;
  let html = "";
  let prevSection = null;
  for (const s of SLIDES) {
    if (s.section !== prevSection) {
      html += `<div class="toc-section">${SECTION_LABELS[s.section] || s.section}</div>`;
      prevSection = s.section;
    }
    html += `<button data-goto="${s.id}"><span class="num">${String(s.id).padStart(2, "0")}</span><span>${s.title}</span></button>`;
  }
  toc.innerHTML = html;
}

function render() {
  if (!N) return;
  if (current !== lastRendered) {
    stage.innerHTML = SLIDES[current - 1].render();
    lastRendered = current;
  }
  const title = SLIDES[current - 1].title;
  counter.textContent = `${current} / ${N}`;
  progress.style.width = `${(current / N) * 100}%`;
  document.title = `${current}/${N}: ${title}`;
  live.textContent = `Slide ${current} de ${N}: ${title}`;

  toc.querySelectorAll("[data-goto]").forEach(b => {
    const on = Number(b.dataset.goto) === current;
    if (on) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current");
  });
  toc.hidden = !tocOpen;
  $("btn-toc").setAttribute("aria-expanded", String(tocOpen));
  if (tocOpen) {
    chrome.classList.remove("is-hidden");
    const cur = toc.querySelector('[aria-current="true"]');
    if (cur) cur.scrollIntoView({ block: "nearest" });
  }
}

function goTo(n) {
  current = clamp(n);
  history.replaceState(null, "", "#slide-" + current);
  render();
}

function readHash() {
  const m = (location.hash || "").match(/slide-(\d+)/i);
  const n = m ? Number(m[1]) : 1;
  const c = clamp(n);
  if (!m || c !== n) goTo(c); else { current = c; render(); }
}

// --------- Chrome auto-ocultar ---------
let hideTimer = null;
function pokeChrome() {
  chrome.classList.remove("is-hidden");
  clearTimeout(hideTimer);
  hideTimer = setTimeout(() => { if (!tocOpen) chrome.classList.add("is-hidden"); }, 2600);
}

// --------- Fullscreen ---------
function toggleFs() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {});
  else document.exitFullscreen().catch(() => {});
}

function setToc(open) { tocOpen = open; render(); }

// --------- Lightbox: clicar numa imagem/gráfico do slide abre ampliado ---------
const lightbox = $("lightbox");
const lbFrame = $("lightbox-frame");
const lbCaption = $("lightbox-caption");
let lbReturnFocus = null;

const lbOpen = () => !lightbox.hidden;

function openLightbox(el) {
  lbFrame.innerHTML = "";
  lbFrame.className = "lightbox-frame";
  let label = "";
  if (el.tagName === "IMG") {
    const img = document.createElement("img");
    img.src = el.currentSrc || el.src;
    img.alt = el.alt || "";
    label = el.alt || "";
    // Diagramas SVG e figuras em painel claro ficam sobre fundo branco.
    if (/\.svg(\?|$)/i.test(img.src) || el.closest(".apm-figure-light") ||
        (el.closest(".apm-figure") && el.closest(".apm-figure").style.background.includes("255")))
      lbFrame.classList.add("is-light");
    lbFrame.appendChild(img);
  } else {
    // Gráfico em SVG inline: clona o nó.
    const svg = el.cloneNode(true);
    svg.removeAttribute("width");
    label = svg.getAttribute("aria-label") || "Gráfico";
    lbFrame.classList.add("is-chart");
    lbFrame.appendChild(svg);
  }
  lbCaption.textContent = label ? `${label} · Esc ou × para voltar` : "Esc ou × para voltar";
  lbReturnFocus = document.activeElement;
  lightbox.hidden = false;
  $("lightbox-close").focus();
}

function closeLightbox() {
  if (!lbOpen()) return;
  lightbox.hidden = true;
  lbFrame.innerHTML = "";
  if (lbReturnFocus && lbReturnFocus.focus) lbReturnFocus.focus();
}

// --------- Eventos ---------
function init() {
  mountStage(viewport, stage);
  buildToc();
  readHash();

  window.addEventListener("hashchange", readHash);

  $("btn-prev").addEventListener("click", () => goTo(current - 1));
  $("btn-next").addEventListener("click", () => goTo(current + 1));
  $("btn-fs").addEventListener("click", toggleFs);
  $("btn-toc").addEventListener("click", () => setToc(!tocOpen));

  toc.addEventListener("click", e => {
    const b = e.target.closest("[data-goto]");
    if (!b) return;
    setToc(false);
    goTo(Number(b.dataset.goto));
  });

  stage.addEventListener("click", e => {
    const el = e.target.closest(".slide-body-area img, .slide-body-area .apm-chart svg");
    if (el) openLightbox(el);
  });
  $("lightbox-close").addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", e => { if (e.target === lightbox) closeLightbox(); });

  window.addEventListener("keydown", e => {
    if (lbOpen()) {
      // Com a imagem aberta, as teclas não trocam de slide.
      if (e.key === "Escape" || e.key === "Backspace") { e.preventDefault(); closeLightbox(); }
      else if (e.key !== "Tab") e.preventDefault();
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    switch (e.key) {
      case "ArrowRight": case " ": case "PageDown": e.preventDefault(); goTo(current + 1); break;
      case "ArrowLeft": case "PageUp": e.preventDefault(); goTo(current - 1); break;
      case "Home": e.preventDefault(); goTo(1); break;
      case "End": e.preventDefault(); goTo(N); break;
      case "s": case "S": setToc(!tocOpen); break;
      case "Escape": if (tocOpen) setToc(false); break;
      case "f": case "F": toggleFs(); break;
    }
  });

  window.addEventListener("mousemove", pokeChrome);
  pokeChrome();

  if (location.search.includes("check")) import("./check.js");
}

document.addEventListener("DOMContentLoaded", init);
