import { SlideLayout } from "../layout.js";
import { Card, Bullets, Highlight, Tradeoff } from "../kit.js";

export default () => SlideLayout({
  kicker: "Conclusão",
  title: "O que o modelo mostrou",
  content: `
    <div class="apm-stack-26">
      <div class="apm-grid-3">
        ${Card({ accent: "turquoise", title: "Onde o controle falha", children: Bullets({ size: 23, items: [
          "A injeção altera a consulta que define a identidade",
          "O hash vaza na serialização da conta no JWT",
          "A cesta alheia é lida depois que a sessão foi aceita",
        ] }) })}
        ${Card({ accent: "violet", title: "Prioridades", children: Bullets({ size: 23, accent: "violet", items: [
          "Corrigir autenticação e limitar o token",
          "Impedir que o cadastro atribua papéis",
          "Autorização por objeto em APIs e arquivos",
        ] }) })}
        ${Card({ accent: "pink", title: "Lição da M1 → M2", children: Bullets({ size: 23, accent: "pink", items: [
          "Reconhecer a sessão não garante a titularidade",
          "Evidência de execução, código e hipótese separadas",
          "Modelar de dentro para fora complementa o teste",
        ] }) })}
      </div>
      ${Tradeoff({ left: "Resultados observados na M1 e na M2", right: "Hipóteses ainda sem reprodução" })}
      ${Highlight({ children: "Revisão documental concluída; as mitigações propostas exigem implantação e verificação dos critérios de aceite." })}
    </div>`,
});
