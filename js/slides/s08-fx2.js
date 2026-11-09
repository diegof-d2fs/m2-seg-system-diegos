import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Evidence, Caption } from "../kit.js";

const compact = "padding:22px 26px";

export default () => SlideLayout({
  kicker: "FX2 · Cadastro e recuperação de senha",
  title: "Dados pessoais e recuperação frágil",
  content: `
    <div style="display:grid;grid-template-columns:1fr 1.05fr;gap:34px;height:100%">
      <div style="display:flex;flex-direction:column;gap:18px;min-height:0">
        <div class="apm-figure apm-figure-light" style="flex:1;padding:10px 14px">
          <img src="assets/dfd/fx2.svg" alt="Recorte do DFD do fluxo FX2">
        </div>
        ${Evidence({ title: "Reprodução M2 · cadastro privilegiado", accent: "orange", lines: [
          { k: "POST", v: "/api/Users" },
          { k: "body", v: '{ "role": "admin" }' },
          { k: "→ status", v: "201 Created" },
          { k: "→ role", v: '"admin"  (id 30)' },
        ] })}
        ${Caption({ children: "Caminho no DFD e a atribuição de papel aceita do cliente." })}
      </div>
      <div class="apm-stack" style="gap:22px;justify-content:center">
        ${Card({ accent: "orange", style: compact, title: "T-FX2-06 · Papel no cadastro — DREAD 9,0", children: Bullets({ size: 22, accent: "orange", items: ["<code>role: admin</code> aceito do cliente (mass assignment)", "Conta criada já como <strong>administrador</strong> · CWE-915 · A01"] }) })}
        ${Card({ accent: "turquoise", style: compact, title: "T-FX2-01 · Resposta previsível — 8,8", children: Bullets({ size: 22, items: ["Pergunta consultável; reset no 5º palpite (V7)", "Confirmada no T1 · CWE-640 · A04"] }) })}
        ${Highlight({ accent: "orange", children: "Papel só no <strong>servidor</strong>; recuperação de <strong>uso único</strong> e resposta uniforme." })}
      </div>
    </div>`,
});
