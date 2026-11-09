import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight } from "../kit.js";

export default () => SlideLayout({
  kicker: "Análise · seleção dos fluxos",
  title: "Quatro fluxos, 25 cenários",
  content: `
    <div class="apm-stack-26">
      <div class="apm-grid-4">
        ${Card({ accent: "turquoise", title: "FX1 · Login e sessão", children: Bullets({ size: 22, items: ["Identidade de toda a loja", "Evidências M1: V1, V2, V6"] }) })}
        ${Card({ accent: "violet", title: "FX2 · Cadastro e recuperação", children: Bullets({ size: 22, accent: "violet", items: ["Dados pessoais e reset", "Evidência M1: V7"] }) })}
        ${Card({ accent: "pink", title: "FX3 · Cesta e pedido", children: Bullets({ size: 22, accent: "pink", items: ["Dados de compra e comprovante", "Evidências M1: V3, V4, V5"] }) })}
        ${Card({ accent: "orange", title: "FX4 · Admin e contabilidade", children: Bullets({ size: 22, accent: "orange", items: ["Função privilegiada", "Vários titulares"] }) })}
      </div>
      <div class="apm-grid-3">
        ${Card({ title: "Critérios atendidos", children: Bullets({ size: 22, items: ["1 fluxo de autenticação (FX1)", "Fluxos com dado pessoal (FX2, FX3)", "Função privilegiada (FX4)"] }) })}
        ${Card({ title: "Rastreabilidade", children: Bullets({ size: 22, accent: "violet", items: ["Todos cruzam uma fronteira", "3 fluxos com achados da M1", "IDs T-FX&lt;n&gt;-&lt;seq&gt;"] }) })}
        ${Card({ title: "Volume", children: Bullets({ size: 22, accent: "pink", items: ["≥ 6 ameaças por fluxo", "25 cenários no total", "7 apoiados em 6 achados da M1"] }) })}
      </div>
      ${Highlight({ children: "Cobertura das seis categorias STRIDE em cada fluxo, com N/A justificado onde a categoria se aplica ao tipo mas não ao caso." })}
    </div>`,
});
