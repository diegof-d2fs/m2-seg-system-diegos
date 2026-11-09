import { SlideLayout } from "../layout.js";
import { JOURNEY } from "../meta.js";
import { accentVar } from "../kit.js";

const item = (j, i) => `
  <a href="#slide-${j.target}" class="apm-card apm-journey-item" style="border-left-color:${accentVar(j.accent)}" aria-label="${j.label}: ir para o slide ${j.target}">
    <span class="j-num" style="color:${accentVar(j.accent)}">${String(i + 1).padStart(2, "0")}</span>
    <span><span class="j-label">${j.label}</span><br><span class="j-sub">${j.sub}</span></span>
  </a>`;

export default () => SlideLayout({
  kicker: "Roteiro",
  title: "O que veremos",
  content: `<div class="apm-grid-2" style="gap:16px">${JOURNEY.map(item).join("")}</div>`,
});
