import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Caption } from "../kit.js";

const compact = "padding:22px 26px";

export default () => SlideLayout({
  kicker: "FX1 · Login e uso da sessão",
  title: "A identidade que sustenta tudo",
  content: `
    <div style="display:grid;grid-template-columns:1fr 1.05fr;gap:34px;height:100%">
      <div style="display:flex;flex-direction:column;gap:18px;min-height:0">
        <div class="apm-figure apm-figure-light" style="flex:1;padding:10px 14px">
          <img src="assets/dfd/fx1.svg" alt="Recorte do DFD do fluxo FX1">
        </div>
        <div class="apm-figure apm-figure-dark" style="padding:8px"><img src="assets/fig_login_strip.png" alt="Campo de login com injeção" style="max-height:150px"></div>
        ${Caption({ children: "Caminho no DFD e a entrada do ataque: <code>' OR 1=1--</code> no campo e-mail." })}
      </div>
      <div class="apm-stack" style="gap:22px;justify-content:center">
        ${Card({ accent: "orange", style: compact, title: "T-FX1-02 · Injeção SQL — DREAD 9,8", children: Bullets({ size: 22, accent: "orange", items: ["E-mail concatenado à consulta → sessão <strong>admin</strong>", "Confirmada no T1 (V1) · CWE-89 · A03"] }) })}
        ${Card({ accent: "turquoise", style: compact, title: "T-FX1-04 · Hash no JWT — 8,6", children: Bullets({ size: 22, items: ["Token serializa a conta, com <code>password</code> MD5 e sem <code>exp</code>", "Confirmada no T1 (V2) · CWE-522/916 · A02"] }) })}
        ${Highlight({ accent: "orange", children: "Consulta <strong>parametrizada</strong>, claims restritos e hash <strong>Argon2id</strong>." })}
      </div>
    </div>`,
});
