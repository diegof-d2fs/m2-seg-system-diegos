import { SLIDES } from "./slides/index.js";
import { SECTION_LABELS, SHORT_ROUTE_HIDDEN } from "./meta.js";
import { renderMarkdown } from "./markdown.js";
import { DECK_TITLE } from "./layout.js";

const $ = id => document.getElementById(id);
const slug = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const sectionOf = n => { const s = SLIDES[n - 1]; return s ? (SECTION_LABELS[s.section] || s.section) : ""; };

function parse(md) {
  const lines = String(md).replace(/\r\n/g, "\n").split("\n");
  const sections = [];
  let cur = null;
  const push = () => { if (cur) { cur.body = cur.body.join("\n").trim(); sections.push(cur); cur = null; } };
  let title = DECK_TITLE.replace(/\n/g, " ");
  let apx = 0;

  for (const line of lines) {
    let m;
    if ((m = line.match(/^#\s+(.+)$/))) { title = m[1].trim(); continue; }
    if ((m = line.match(/^###\s+Slide\s+(\d+)\s*:\s*(.+)$/i))) {
      push();
      cur = { id: `slide-${m[1]}`, kind: "slide", slide: Number(m[1]), heading: m[2].trim(), body: [] };
      continue;
    }
    if ((m = line.match(/^##\s+(.+)$/))) {
      push();
      const h = m[1].trim();
      cur = { id: `apx-${++apx}-${slug(h)}`, kind: "appendix", heading: h, body: [] };
      continue;
    }
    if (cur) cur.body.push(line);
    else {
      if (!sections.length || sections[0].kind !== "intro") sections.unshift({ id: "intro", kind: "intro", heading: title, body: [line] });
      else sections[0].body += "\n" + line;
    }
  }
  push();
  return { title, sections };
}

let shortRoute = false;

function build(data) {
  const intro = data.sections.find(s => s.kind === "intro");
  const body = data.sections.filter(s => s.kind !== "intro");

  const tocHtml = body.map(s => {
    const hidden = s.kind === "slide" && SHORT_ROUTE_HIDDEN.includes(s.slide);
    const label = s.kind === "slide" ? `${String(s.slide).padStart(2, "0")}. ${s.heading}` : `§ ${s.heading}`;
    return `<a href="#${s.id}" class="${s.kind === "appendix" ? "apx" : ""}" data-hidden="${hidden}">${label}</a>`;
  }).join("");

  const sectionsHtml = body.map(s => {
    const optional = s.kind === "slide" && SHORT_ROUTE_HIDDEN.includes(s.slide);
    const meta = s.kind === "slide"
      ? `Bloco: ${sectionOf(s.slide)}${optional ? " · opcional na rota curta" : ""}`
      : "Apêndice";
    const h = s.kind === "slide" ? `Slide ${s.slide} · ${s.heading}` : s.heading;
    return `<section id="${s.id}" class="cola-section" data-optional="${optional}">
      <h2>${h}</h2>
      <p class="cola-meta">${meta}</p>
      <div class="cola-md">${renderMarkdown(s.body)}</div>
    </section>`;
  }).join("");

  $("cola").innerHTML = `
    ${intro ? `<p class="cola-intro">${renderMarkdown(intro.body)}</p>` : ""}
    <nav class="cola-toc cola-no-print" aria-label="Índice do roteiro">${tocHtml}</nav>
    ${sectionsHtml}`;

  applyShort();
}

function applyShort() {
  document.querySelectorAll('.cola-section[data-optional="true"]').forEach(s => s.setAttribute("data-hidden", String(shortRoute)));
  document.querySelectorAll('.cola-toc a[data-hidden]').forEach(a => {
    if (a.classList.contains("apx")) return;
    const id = a.getAttribute("href").slice(1);
    const sec = document.getElementById(id);
    if (sec && sec.dataset.optional === "true") a.setAttribute("data-hidden", String(shortRoute));
  });
  const btn = $("btn-short");
  btn.dataset.active = String(shortRoute);
  btn.setAttribute("aria-pressed", String(shortRoute));
  btn.textContent = shortRoute ? "Desativar rota curta" : "Ativar rota curta (30 min)";
}

function init() {
  if (new URLSearchParams(location.search).has("curta")) shortRoute = true;
  $("btn-short").addEventListener("click", () => { shortRoute = !shortRoute; applyShort(); });
  $("btn-print").addEventListener("click", () => window.print());

  fetch("content/cola.md")
    .then(r => { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(txt => build(parse(txt)))
    .then(() => { if (location.hash) { const el = document.getElementById(location.hash.slice(1)); if (el) el.scrollIntoView(); } })
    .catch(() => {
      $("cola").innerHTML = `<div class="cola-error">Não foi possível carregar o roteiro. Rode um servidor local (ex.: <code>python -m http.server</code>) em vez de abrir o arquivo direto.</div>`;
    });

  if (location.search.includes("check")) import("./check.js");
}

document.addEventListener("DOMContentLoaded", init);
