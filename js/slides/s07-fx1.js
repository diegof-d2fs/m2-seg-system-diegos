import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Table } from "../kit.js";

export default () => SlideLayout({
  kicker: "FX1 · Login e uso da sessão",
  title: "A identidade que sustenta tudo",
  content: `
    <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:36px;height:100%">
      <div class="apm-stack-26">
        ${Card({ accent: "orange", title: "T-FX1-02 · Injeção SQL (DREAD 9,8)", children: Bullets({ size: 23, accent: "orange", items: [
          "E-mail concatenado à consulta de login (P2/F21)",
          "Entrada anônima vira <strong>sessão de administrador</strong>",
          "Confirmada no T1 (V1) · CWE-89 · A03",
        ] }) })}
        ${Card({ accent: "turquoise", title: "T-FX1-04 · Hash no JWT (8,6)", children: Bullets({ size: 23, items: [
          "Objeto de conta serializado inclui <code>password</code>",
          "<strong>MD5 sem sal</strong>, token sem expiração (exp)",
          "Confirmada no T1 (V2) · CWE-522/916 · A02",
        ] }) })}
      </div>
      <div class="apm-stack-26">
        ${Table({ head: ["Outros cenários", "Risco"], rows: [
          ["T-FX1-01 força bruta sem bloqueio (V6)", "8,0"],
          ["T-FX1-06 chave de assinatura embutida", "8,4"],
          ["T-FX1-05 exaustão do mapa de sessões", "6,8"],
          ["T-FX1-03 log sem correlação de autoria", "6,4"],
        ] })}
        ${Highlight({ accent: "orange", children: "Parametrizar a consulta, restringir os <em>claims</em> e migrar o hash para <strong>Argon2id</strong>." })}
      </div>
    </div>`,
});
