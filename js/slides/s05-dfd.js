import { SlideLayout } from "../layout.js";
import { Bullets, Highlight } from "../kit.js";

export default () => SlideLayout({
  kicker: "Modelo do sistema · o fio condutor",
  title: "DFD nível 1 e fronteiras de confiança",
  content: `
    <div style="display:grid;grid-template-columns:1fr 1.05fr;gap:40px;height:100%">
      <div class="apm-stack-26" style="justify-content:center">
        ${Bullets({ size: 26, items: [
          "<strong>P2–P6</strong>: responsabilidades do mesmo serviço Express (identidade, cadastro, cesta, privilégios, arquivos)",
          "<strong>D1 SQLite</strong>, D2 mapa de sessões, D3 pedidos, D4 /ftp/, D5 logs",
          "<strong>TB-01</strong> cliente | servidor · <strong>TB-02</strong> host | contêiner · <strong>TB-03</strong> aplicação | armazenamentos",
        ] })}
        ${Highlight({ children: "Todo fluxo analisado cruza ao menos uma fronteira: é onde a confiança muda e a atenção redobra." })}
      </div>
      <div class="apm-figure" style="background:#fff;padding:14px">
        <img src="assets/dfd/dfd_nivel_1.svg" alt="DFD nível 1 do OWASP Juice Shop com fronteiras de confiança">
      </div>
    </div>`,
});
