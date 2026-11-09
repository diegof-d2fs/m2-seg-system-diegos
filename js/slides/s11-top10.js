import { SlideLayout } from "../layout.js";
import { Table, Highlight, Metric } from "../kit.js";

export default () => SlideLayout({
  kicker: "Visão consolidada",
  title: "Top 10 por média DREAD",
  content: `
    <div style="display:grid;grid-template-columns:1.25fr .75fr;gap:40px;height:100%">
      <div>
        ${Table({ head: ["#", "Cenário (elemento)", "DREAD", "Status"], rows: [
          ["1", "T-FX1-02 Injeção SQL no login (P2)", "<strong>9,8</strong>", "T1 · V1"],
          ["2", "T-FX2-06 Papel privilegiado no cadastro (P3)", "9,0", "Plausível*"],
          ["3", "T-FX2-01 Resposta previsível no reset (P3)", "8,8", "T1 · V7"],
          ["4", "T-FX1-04 Hash de senha no JWT (F10)", "8,6", "T1 · V2"],
          ["5", "T-FX4-04 Consulta de usuários (F16)", "8,6", "Plausível"],
          ["6", "T-FX3-06 Cesta de outro titular (P4)", "8,4", "T1 · V3"],
          ["7", "T-FX1-06 Chave de assinatura distribuída (P2)", "8,4", "Plausível"],
          ["8", "T-FX4-06 Exclusão de feedback (P5)", "8,2", "Plausível"],
          ["9", "T-FX1-01 Força bruta no login (P2)", "8,0", "T1 · V6"],
          ["10", "T-FX3-02 Checkout de cesta alheia (P4)", "7,8", "Plausível"],
        ] })}
      </div>
      <div class="apm-stack" style="justify-content:center">
        ${Metric({ value: "25", label: "cenários modelados" })}
        ${Metric({ value: "18", label: "risco alto (≥ 7,0)", accent: "orange" })}
        ${Metric({ value: "7", label: "apoiados em achados da M1", accent: "violet" })}
        ${Highlight({ children: "Parametrizar o login corrige o mecanismo de injeção; o <strong>controle de acesso</strong> ainda precisa agir em cada recurso." })}
        <p class="slide-caption">* reproduzida ao vivo na M2 (ver Validação).</p>
      </div>
    </div>`,
});
