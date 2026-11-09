import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Table } from "../kit.js";

export default () => SlideLayout({
  kicker: "FX4 · Administração e contabilidade",
  title: "Função privilegiada e vários titulares",
  content: `
    <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:36px;height:100%">
      <div class="apm-stack-26">
        ${Card({ accent: "orange", title: "T-FX4-04 · Consulta de usuários (8,6)", children: Bullets({ size: 23, accent: "orange", items: [
          "Rota de listagem de contas sem verificação de papel",
          "Conta comum acessaria dados de <strong>muitos titulares</strong>",
          "Plausível · CWE-284 · A01",
        ] }) })}
        ${Card({ accent: "turquoise", title: "T-FX4-06 · Exclusão de feedback (8,2)", children: Bullets({ size: 23, items: [
          "DELETE de feedback sem exigir papel admin",
          "Verificação de função desigual entre rotas",
          "Plausível · CWE-285 · A01",
        ] }) })}
      </div>
      <div class="apm-stack-26">
        ${Table({ head: ["Outros cenários", "Risco"], rows: [
          ["T-FX4-05 listagem sem limite de volume", "6,6"],
          ["T-FX4-02 entrega baseada em estado do cliente", "6,4"],
          ["T-FX4-01 reuso de sessão após desligamento", "6,0"],
          ["T-FX4-03 repúdio de moderação/entrega", "5,4"],
        ] })}
        ${Highlight({ accent: "orange", children: "Matriz de papéis no servidor para cada rota privilegiada; negar por padrão e registrar a ação." })}
      </div>
    </div>`,
});
