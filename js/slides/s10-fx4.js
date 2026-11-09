import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Caption } from "../kit.js";

const compact = "padding:22px 26px";

export default () => SlideLayout({
  kicker: "FX4 · Administração e contabilidade",
  title: "Função privilegiada e vários titulares",
  content: `
    <div style="display:grid;grid-template-columns:1fr 1.05fr;gap:34px;height:100%">
      <div class="apm-stack" style="gap:20px;justify-content:center">
        <div class="apm-figure apm-figure-light" style="padding:8px 12px">
          <img src="assets/dfd/fx4.svg" alt="Recorte do DFD do fluxo FX4" style="max-height:170px">
        </div>
        ${Card({ accent: "orange", style: compact, title: "T-FX4-04 · Consulta de usuários — 8,6", children: Bullets({ size: 22, accent: "orange", items: ["Listagem de contas sem verificação de papel", "Conta comum veria <strong>muitos titulares</strong> · A01"] }) })}
        ${Card({ accent: "turquoise", style: compact, title: "T-FX4-06 · Exclusão de feedback — 8,2", children: Bullets({ size: 22, items: ["DELETE sem exigir admin; função desigual entre rotas"] }) })}
        ${Highlight({ accent: "orange", children: "Matriz de <strong>papéis no servidor</strong> por rota; negar por padrão e registrar." })}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px;min-height:0;justify-content:center">
        <div class="apm-figure apm-figure-dark" style="flex:1;padding:10px">
          <img class="apm-shot" src="assets/fig_admin_panel.png" alt="Painel de administração com lista de usuários e feedbacks">
        </div>
        ${Caption({ children: "Painel <code>/#/administration</code> alcançado na reprodução M2: lista de e-mails e feedbacks (desafio <em>Admin Section</em> reconhecido)." })}
      </div>
    </div>`,
});
