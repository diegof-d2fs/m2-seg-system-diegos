import { SlideLayout } from "../layout.js";
import { Card, Bullets, Flow, Highlight, Source } from "../kit.js";

export default () => SlideLayout({
  kicker: "Metodologia",
  title: "Quatro perguntas, três ferramentas",
  content: `
    <div class="apm-stack-26">
      ${Source({ children: "Shostack (2014) · STRIDE/Microsoft SDL · DREAD (Meier et al., 2003)" })}
      ${Flow({ steps: [
        "O que construímos?<br><span class='slide-caption'>DFD + fronteiras</span>",
        "O que pode dar errado?<br><span class='slide-caption'>STRIDE por elemento</span>",
        "O que fazer?<br><span class='slide-caption'>DREAD + mitigações</span>",
        "Fizemos um bom trabalho?<br><span class='slide-caption'>validação</span>",
      ] })}
      <div class="apm-grid-3">
        ${Card({ accent: "turquoise", title: "DFD", children: Bullets({ items: [
          "Entidades, processos, armazenamentos, fluxos",
          "Fronteiras de confiança (TB) onde a confiança muda",
          "IDs únicos rastreáveis em todo o relatório",
        ] }) })}
        ${Card({ accent: "violet", title: "STRIDE por elemento", children: Bullets({ accent: "violet", items: [
          "S, T, R, I, D, E conforme o tipo de elemento",
          "Ameaça no formato padrão, não genérica",
          "N/A sempre justificado",
        ] }) })}
        ${Card({ accent: "pink", title: "DREAD", children: Bullets({ accent: "pink", items: [
          "Dano, reprodutibilidade, explorabilidade, usuários, descoberta",
          "Média de 1 a 10, cada nota justificada",
          "Escala: baixo &lt;4 · médio 4–6,9 · alto ≥7",
        ] }) })}
      </div>
      ${Highlight({ children: "Cada ameaça liga-se a um requisito <strong>ASVS 5.0</strong>, a um <strong>CWE</strong> e, havendo dado pessoal, ao <strong>art. 46 da LGPD</strong>." })}
    </div>`,
});
