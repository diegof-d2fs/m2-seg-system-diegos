import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Table } from "../kit.js";

export default () => SlideLayout({
  kicker: "FX3 · Cesta, checkout e registro do pedido",
  title: "Autorização por objeto, não só por sessão",
  content: `
    <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:36px;height:100%">
      <div class="apm-stack-26">
        ${Card({ accent: "orange", title: "T-FX3-06 · Cesta de outro titular (8,4)", children: Bullets({ size: 23, accent: "orange", items: [
          "JWT válido lê a cesta de <strong>outra conta</strong> (IDOR)",
          "Sem token, a mesma rota recusa (HTTP 401)",
          "Confirmada no T1 (V3) · CWE-639 · A01",
        ] }) })}
        ${Card({ accent: "turquoise", title: "T-FX3-02 / T-FX3-07", children: Bullets({ size: 23, items: [
          "Checkout com referências de cesta alheia (7,8)",
          "Comprovante exposto pelo diretório /ftp/ (V5)",
          "Autorização deve ocorrer no ponto que lê o recurso",
        ] }) })}
      </div>
      <div class="apm-stack-26">
        ${Table({ head: ["Outros cenários", "Risco"], rows: [
          ["T-FX3-04 erro verboso com detalhes (V4)", "6,0"],
          ["T-FX3-05 saturação por comprovantes", "6,8"],
          ["T-FX3-01 reutilização de sessão", "6,2"],
          ["T-FX3-03 pedido sem correlação de eventos", "5,6"],
        ] })}
        ${Highlight({ accent: "orange", children: "Política de <strong>titularidade</strong> em cesta, pedido, endereço, pagamento e comprovante; servir arquivos só via API autorizada." })}
      </div>
    </div>`,
});
