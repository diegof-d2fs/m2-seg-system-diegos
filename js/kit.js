// Primitivas do design system. Cada função recebe um objeto e retorna string HTML.
// Conteúdo (children/items/steps) aceita HTML confiável (escrito pela equipe).
// Para texto externo, usar esc().

/** @typedef {"turquoise"|"orange"|"violet"|"pink"} Accent */

export const esc = (s = "") => String(s).replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export const accentVar = a => `var(--apm-${a})`;
export const accentClass = a => `apm-text-${a}`;

export const Card = ({ accent, title, children = "", style = "" }) => `
  <div class="apm-card" style="${accent ? `box-shadow: inset 0 4px 0 0 ${accentVar(accent)};` : ""}${style}">
    ${title ? `<h3 class="apm-card-title">${title}</h3>` : ""}
    ${children}
  </div>`;

export const Bullets = ({ items, accent = "turquoise", size = 24 }) => `
  <ul class="apm-bullets" style="font-size:${size}px">
    ${items.map(i => `<li><span class="${accentClass(accent)}" aria-hidden="true">›</span><span>${i}</span></li>`).join("")}
  </ul>`;

export const Numbered = ({ items, accent = "turquoise", size = 24 }) => `
  <ol class="apm-numbered" style="font-size:${size}px">
    ${items.map((i, n) => `<li><span class="apm-num ${accentClass(accent)}">${String(n + 1).padStart(2, "0")}</span><span>${i}</span></li>`).join("")}
  </ol>`;

export const Flow = ({ steps, accent = "turquoise" }) => `
  <div class="apm-flow">
    ${steps.map(s => `<div class="apm-flow-step">${s}</div>`)
      .join(`<span class="apm-flow-arrow ${accentClass(accent)}" aria-hidden="true">→</span>`)}
  </div>`;

export const Highlight = ({ children, accent = "turquoise" }) =>
  `<p class="apm-highlight" style="border-left-color:${accentVar(accent)}">${children}</p>`;

export const Metric = ({ value, label, accent = "turquoise" }) => `
  <div class="apm-metric">
    <span class="apm-metric-value" style="color:${accentVar(accent)}">${value}</span>
    <span class="apm-metric-label">${label}</span>
  </div>`;

export const Chip = ({ children, accent = "turquoise" }) =>
  `<span class="apm-chip"><span class="dot ${accentClass(accent)}" aria-hidden="true">●</span>${children}</span>`;

export const Table = ({ head, rows }) => `
  <table class="apm-table">
    ${head ? `<thead><tr>${head.map(h => `<th>${h}</th>`).join("")}</tr></thead>` : ""}
    <tbody>${rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody>
  </table>`;

export const Tradeoff = ({ left, right }) =>
  `<div class="apm-tradeoff"><span class="l">${left}</span><span class="x" aria-hidden="true">×</span><span class="r">${right}</span></div>`;

export const Quote = ({ children, cite }) =>
  `<blockquote class="apm-quote">${children}${cite ? `<cite>${cite}</cite>` : ""}</blockquote>`;

export const Placeholder = ({ children }) => `<div class="apm-placeholder">${children}</div>`;

export const Source = ({ children }) => `<p class="apm-source">${children}</p>`;

export const Figure = ({ src, alt = "", style = "", shot = false, panel = "dark" }) =>
  `<div class="apm-figure apm-figure-${panel}" style="${style}"><img class="${shot ? "apm-shot" : ""}" src="${src}" alt="${esc(alt)}"></div>`;

// Legenda curta sob uma figura/print.
export const Caption = ({ children }) => `<p class="apm-figcaption">${children}</p>`;

// Painel de evidência estilo terminal/código. lines = [{k, v}] ou strings HTML.
export const Evidence = ({ title, accent = "turquoise", lines }) => `
  <div class="apm-evidence" style="box-shadow: inset 0 3px 0 0 ${accentVar(accent)}">
    ${title ? `<div class="apm-evidence-head"><span class="dot ${accentClass(accent)}">●</span>${title}</div>` : ""}
    <pre class="apm-evidence-body">${lines.map(l => typeof l === "string" ? l : `<span class="ev-k">${l.k}</span>  <span class="ev-v">${l.v}</span>`).join("\n")}</pre>
  </div>`;
