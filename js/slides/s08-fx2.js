import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Table } from "../kit.js";

export default () => SlideLayout({
  kicker: "FX2 · Cadastro e recuperação de senha",
  title: "Dados pessoais e recuperação frágil",
  content: `
    <div style="display:grid;grid-template-columns:1.1fr .9fr;gap:36px;height:100%">
      <div class="apm-stack-26">
        ${Card({ accent: "orange", title: "T-FX2-06 · Papel no cadastro (DREAD 9,0)", children: Bullets({ size: 23, accent: "orange", items: [
          "<code>role: admin</code> aceito do cliente (mass assignment)",
          "Conta criada já com <strong>privilégio de administrador</strong>",
          "CWE-915 · A01 · reproduzida na M2 (ver Validação)",
        ] }) })}
        ${Card({ accent: "turquoise", title: "T-FX2-01 · Resposta previsível (8,8)", children: Bullets({ size: 23, items: [
          "Pergunta de segurança consultável por e-mail",
          "Redefinição no 5º palpite dentro da cota (V7)",
          "Confirmada no T1 · CWE-640 · A07",
        ] }) })}
      </div>
      <div class="apm-stack-26">
        ${Table({ head: ["Outros cenários", "Risco"], rows: [
          ["T-FX2-04 pergunta exposta por e-mail", "7,4"],
          ["T-FX2-02 associação indevida de resposta", "6,6"],
          ["T-FX2-05 cadastros automatizados", "5,8"],
          ["T-FX2-03 repúdio da redefinição", "5,2"],
        ] })}
        ${Highlight({ accent: "orange", children: "Atribuir papel só no servidor; recuperação de <strong>uso único</strong> e resposta uniforme (sem enumerar contas)." })}
      </div>
    </div>`,
});
