import { esc } from "./kit.js";

export const DECK_TITLE = "Modelagem de Ameaças\nOWASP Juice Shop";
export const DECK_TAG = "UNIVALI · Trabalho 2 · 2026/2";

export function SlideLayout({ kicker, title, content = "", bare = false, hideUnderline = false, footerBottom = 42 }) {
  if (bare) return `<div class="slide-content">${content}</div>`;
  return `
  <div class="slide-content">
    <div class="slide-frame">
      ${kicker ? `<div class="slide-kicker"><span class="kicker-mark">‹</span>${esc(kicker)}</div>` : ""}
      ${title ? `<h1 class="slide-title">${title}</h1>` : ""}
      ${hideUnderline ? "" : `<div class="slide-underline"></div>`}
      <div class="slide-body-area">${content}</div>
    </div>
    <footer class="slide-footer" style="bottom:${footerBottom}px">
      <div class="slide-footer-left">${esc(DECK_TITLE)}</div>
      <img src="assets/logo.svg" alt="" height="96">
      <div class="slide-footer-right">${esc(DECK_TAG)}</div>
    </footer>
  </div>`;
}
