import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight } from "../kit.js";

export default () => SlideLayout({
  kicker: "Visão consolidada · tratamento",
  title: "Plano de mitigação por frentes",
  content: `
    <div class="apm-stack-26">
      <div class="apm-grid-3">
        ${Card({ accent: "turquoise", title: "1 · Autenticação e segredos", children: Bullets({ size: 22, items: [
          "Consulta parametrizada e claims restritos",
          "MD5 → Argon2id; rotação de chave",
          "<span class='slide-caption'>Aceite: V1 falha; JWT sem hash</span>",
        ] }) })}
        ${Card({ accent: "violet", title: "2 · Cadastro e recuperação", children: Bullets({ size: 22, accent: "violet", items: [
          "Papel definido no servidor",
          "Reset de uso único e resposta uniforme",
          "<span class='slide-caption'>Aceite: cadastro força customer</span>",
        ] }) })}
        ${Card({ accent: "pink", title: "3 · Autorização (P4 e P5)", children: Bullets({ size: 22, accent: "pink", items: [
          "Política de função nas rotas privilegiadas",
          "Titularidade em cesta, pedido e comprovante",
          "<span class='slide-caption'>Aceite: contas não se cruzam</span>",
        ] }) })}
      </div>
      <div class="apm-grid-3">
        ${Card({ accent: "turquoise", title: "4 · Sessão e contenção", children: Bullets({ size: 22, items: ["Expiração efetiva e revogação", "Limites por conta e origem"] }) })}
        ${Card({ accent: "violet", title: "5 · Integridade do pedido", children: Bullets({ size: 22, accent: "violet", items: ["Idempotência e versão", "Quota de PDF e paginação"] }) })}
        ${Card({ accent: "orange", title: "6 · Auditoria e erros", children: Bullets({ size: 22, accent: "orange", items: ["Trilha protegida e correlacionável", "Erro sem detalhe interno"] }) })}
      </div>
      ${Highlight({ children: "Cada mitigação é <strong>verificável</strong>: ligada a um requisito ASVS 5.0, com critério de aceite e referência à LGPD (art. 46)." })}
    </div>`,
});
