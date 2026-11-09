import { SlideLayout } from "../layout.js";
import { Chip } from "../kit.js";

export default () => SlideLayout({
  bare: true,
  content: `
    <div class="capa-brand">UNIVALI · Escola Politécnica<br>Ciência da Computação<br>Segurança de Sistemas Computacionais · 2026/2</div>
    <div class="capa-wrap">
      <div class="apm-eyebrow"><span class="kicker-mark">‹</span>Trabalho 2 · Modelagem de Ameaças</div>
      <h1 class="slide-title-lg" style="max-width:1500px">Modelagem de Ameaças no OWASP Juice Shop</h1>
      <p class="slide-subtitle" style="max-width:1300px">Relatório final de modelagem com DFD, STRIDE e DREAD</p>
      <div class="capa-grad-bar"></div>
      <div class="capa-names">Diego Fonseca da Silva
Leonardo Pacheco B Dias
Gustavo Gonçalves Trindade
João Victor Rodrigues Santos</div>
      <div class="capa-chips">
        ${Chip({ accent: "turquoise", children: "DFD de contexto e nível 1" })}
        ${Chip({ accent: "violet", children: "STRIDE por elemento" })}
        ${Chip({ accent: "pink", children: "Priorização DREAD" })}
      </div>
      <p class="slide-caption">Prof. Ramicés dos Santos Silva · Itajaí (SC), novembro de 2026</p>
    </div>`,
});
