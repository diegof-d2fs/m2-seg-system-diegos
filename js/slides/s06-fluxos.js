import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight } from "../kit.js";
import { StrideChart } from "../charts.js";

export default () => SlideLayout({
  kicker: "Análise · seleção dos fluxos",
  title: "Quatro fluxos, 25 cenários",
  content: `
    <div class="apm-stack-26">
      <div class="apm-grid-4">
        ${Card({ accent: "turquoise", title: "FX1 · Login", children: Bullets({ size: 21, items: ["Identidade da loja", "M1: V1, V2, V6"] }) })}
        ${Card({ accent: "violet", title: "FX2 · Cadastro", children: Bullets({ size: 21, accent: "violet", items: ["Dados pessoais, reset", "M1: V7"] }) })}
        ${Card({ accent: "pink", title: "FX3 · Cesta e pedido", children: Bullets({ size: 21, accent: "pink", items: ["Compra e comprovante", "M1: V3, V4, V5"] }) })}
        ${Card({ accent: "orange", title: "FX4 · Admin", children: Bullets({ size: 21, accent: "orange", items: ["Função privilegiada", "Vários titulares"] }) })}
      </div>
      <div style="display:grid;grid-template-columns:1.15fr .85fr;gap:36px;flex:1;min-height:0">
        ${Card({ title: "Distribuição das 25 ameaças por categoria STRIDE", style: "display:flex;flex-direction:column;justify-content:center", children: `<div class="apm-chart">${StrideChart()}</div>` })}
        <div class="apm-stack-26" style="justify-content:center">
          ${Bullets({ size: 23, items: [
            "1 fluxo de <strong>autenticação</strong> (FX1) + dados pessoais (FX2, FX3)",
            "Todos cruzam uma <strong>fronteira</strong>; 3 trazem achados da M1",
            "≥ 6 ameaças por fluxo, cobrindo as seis categorias",
          ] })}
          ${Highlight({ children: "<strong>Information Disclosure</strong> lidera: exposição por token, resposta de erro, diretório e resposta de API." })}
        </div>
      </div>
    </div>`,
});
