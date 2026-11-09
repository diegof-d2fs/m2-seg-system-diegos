import { SlideLayout } from "../layout.js";
import { Highlight, Metric, Card } from "../kit.js";
import { DreadChart } from "../charts.js";

export default () => SlideLayout({
  kicker: "Visão consolidada",
  title: "Top 10 por média DREAD",
  content: `
    <div style="display:grid;grid-template-columns:1.35fr .65fr;gap:40px;height:100%">
      ${Card({ style: "display:flex;flex-direction:column;justify-content:center;padding:26px 30px", children: `<div class="apm-chart">${DreadChart()}</div>` })}
      <div class="apm-stack" style="justify-content:center">
        ${Metric({ value: "25", label: "cenários modelados" })}
        ${Metric({ value: "18", label: "risco alto (≥ 7,0)", accent: "orange" })}
        ${Metric({ value: "7", label: "apoiados em achados da M1", accent: "violet" })}
        ${Highlight({ children: "Parametrizar o login corrige o mecanismo de injeção; o <strong>controle de acesso</strong> ainda precisa agir em cada recurso." })}
        <p class="slide-caption">Escala: alto ≥ 7,0 · médio 4,0–6,9. Status em T1 (confirmada) ou plausível.</p>
      </div>
    </div>`,
});
