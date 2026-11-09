import { SlideLayout } from "../layout.js";
import { Bullets, Highlight, Figure, Source } from "../kit.js";

export default () => SlideLayout({
  kicker: "Validação · reprodução em laboratório",
  title: "Do papel para a instância",
  content: `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:36px;height:100%">
      <div class="apm-stack-26" style="justify-content:center">
        ${Source({ children: "Reprodução em 08/11/2026 · mesma imagem v20.2.0 (digest sha256:8739…526b) em 127.0.0.1:3000" })}
        ${Bullets({ size: 25, items: [
          "<strong>Injeção SQL</strong> no login → sessão admin (id 1)",
          "JWT com <code>password</code> (MD5), sem <code>exp</code>",
          "<strong>Cadastro role:admin</strong> aceito — T-FX2-06 reproduzida",
          "Leitura de <strong>cesta alheia</strong> (200) · sem token (401)",
          "Listagem anônima de <strong>/ftp/</strong>; reset com cota 100",
        ] })}
        ${Highlight({ children: "O próprio motor de desafios marcou <strong>Login Admin, Admin Registration e View Basket</strong> como resolvidos." })}
      </div>
      <div style="display:grid;grid-template-rows:1.25fr 1fr;gap:20px;min-height:0">
        ${Figure({ src: "assets/fig_m2_sqli.png", alt: "Sessão de administrador via injeção SQL", shot: true })}
        ${Figure({ src: "assets/fig_m2_ftp.png", alt: "Listagem anônima do diretório /ftp/", shot: true })}
      </div>
    </div>`,
});
