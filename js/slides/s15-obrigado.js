import { SlideLayout } from "../layout.js";
import { Chip } from "../kit.js";

export default () => SlideLayout({
  bare: true,
  content: `
    <div style="position:absolute;inset:0;padding:110px 120px;display:grid;grid-template-columns:1.2fr .8fr;gap:60px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:30px">
        <div class="apm-eyebrow"><span class="kicker-mark">‹</span>Obrigado</div>
        <h1 style="font-size:140px;line-height:.95;letter-spacing:-.05em;margin:0;font-weight:700">Obrigado.</h1>
        <p class="apm-quote" style="max-width:900px">“O que estamos construindo, o que pode dar errado, o que fazer a respeito e se fizemos um bom trabalho.”<cite>As quatro perguntas de Shostack (2014)</cite></p>
        <div style="display:flex;gap:16px;flex-wrap:wrap">
          ${Chip({ accent: "turquoise", children: "DFD + STRIDE + DREAD" })}
          ${Chip({ accent: "violet", children: "25 cenários · Top 10" })}
          ${Chip({ accent: "pink", children: "Reproduzido no laboratório" })}
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:22px">
        <div class="apm-card" style="box-shadow:inset 0 4px 0 0 var(--apm-turquoise)">
          <h3 class="apm-card-title">Equipe</h3>
          <p class="capa-names" style="font-size:26px">Diego Fonseca da Silva
Leonardo Pacheco B Dias
Gustavo Gonçalves Trindade
João Victor Rodrigues Santos</p>
        </div>
        <div class="apm-card" style="box-shadow:inset 0 4px 0 0 var(--apm-violet)">
          <h3 class="apm-card-title">Materiais</h3>
          <p class="slide-body" style="font-size:22px;color:var(--apm-fg-2)">
            Relatório, modelo (.drawio/JSON) e scripts no repositório.<br>
            <span class="slide-caption">github.com/diegof-d2fs/m2-seg-system-diegos</span><br>
            <span class="slide-caption">Base: github.com/diisilva/m1-seg-system-diegos</span>
          </p>
        </div>
      </div>
    </div>`,
});
