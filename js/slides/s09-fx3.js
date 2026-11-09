import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Evidence, Caption } from "../kit.js";

const compact = "padding:22px 26px";

export default () => SlideLayout({
  kicker: "FX3 · Cesta, checkout e registro do pedido",
  title: "Autorização por objeto, não só por sessão",
  content: `
    <div style="display:grid;grid-template-columns:1fr 1.05fr;gap:34px;height:100%">
      <div style="display:flex;flex-direction:column;gap:18px;min-height:0">
        <div class="apm-figure apm-figure-light" style="flex:1;padding:10px 14px">
          <img src="assets/dfd/fx3.svg" alt="Recorte do DFD do fluxo FX3">
        </div>
        ${Evidence({ title: "Reprodução M2 · leitura cruzada de cesta", accent: "orange", lines: [
          { k: "GET /rest/basket/{A}", v: "token de B → 200" },
          { k: "GET /rest/basket/{A}", v: "sem token → 401" },
        ] })}
        ${Caption({ children: "Caminho no DFD e o acesso a objeto de outro titular." })}
      </div>
      <div class="apm-stack" style="gap:22px;justify-content:center">
        ${Card({ accent: "orange", style: compact, title: "T-FX3-06 · Cesta de outro titular — 8,4", children: Bullets({ size: 22, accent: "orange", items: ["JWT válido lê a cesta de <strong>outra conta</strong> (IDOR)", "Confirmada no T1 (V3) · CWE-639 · A01"] }) })}
        ${Card({ accent: "turquoise", style: compact, title: "T-FX3-02 / T-FX3-07", children: Bullets({ size: 22, items: ["Checkout com referências de cesta alheia (7,8)", "Comprovante exposto pelo diretório /ftp/ (V5)"] }) })}
        ${Highlight({ accent: "orange", children: "Política de <strong>titularidade</strong> por objeto; servir arquivos só via API autorizada." })}
      </div>
    </div>`,
});
