import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Chip } from "../kit.js";

export default () => SlideLayout({
  kicker: "Contexto · C1 a C10",
  title: "O ambiente analisado",
  content: `
    <div class="apm-stack-26">
      <div class="apm-grid-3">
        ${Card({ accent: "turquoise", title: "O sistema", children: Bullets({ items: [
          "OWASP <strong>Juice Shop</strong> v20.2.0, loja fictícia para treino de segurança",
          "SPA <strong>Angular</strong> + API <strong>Node/Express</strong>, dados em <strong>SQLite</strong> e MarsDB",
          "Autenticação por <strong>JWT</strong> (RS256); comprovantes em PDF",
        ] }) })}
        ${Card({ accent: "violet", title: "Implantação (M1)", children: Bullets({ accent: "violet", items: [
          "Imagem oficial fixada por <strong>tag + digest</strong>",
          "Publicada só em <strong>127.0.0.1:3000</strong> (loopback)",
          "Contêiner em rede Docker bridge isolada",
        ] }) })}
        ${Card({ accent: "pink", title: "Atores e ativos", children: Bullets({ accent: "pink", items: [
          "Visitante, cliente, <strong>admin</strong> e <strong>accounting</strong>",
          "Contas, credenciais, cesta, pedido, comprovante",
          "Dados pessoais à luz da <strong>LGPD</strong>",
        ] }) })}
      </div>
      <div style="display:flex;gap:16px;flex-wrap:wrap">
        ${Chip({ accent: "turquoise", children: "4 fluxos modelados: FX1–FX4" })}
        ${Chip({ accent: "violet", children: "Superfície: rede, UI, admin, integração, dados" })}
        ${Chip({ accent: "pink", children: "Continuidade com o Trabalho 1" })}
      </div>
      ${Highlight({ children: "Invertemos a perspectiva da M1: do teste de fora para dentro para a <strong>visão de projeto</strong>, de dentro para fora." })}
    </div>`,
});
