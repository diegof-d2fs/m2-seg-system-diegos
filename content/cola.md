# Roteiro do apresentador — Modelagem de Ameaças (OWASP Juice Shop)

Apresentação do Trabalho 2 de Segurança de Sistemas Computacionais (UNIVALI, 2026/2). Alvo de **15 minutos**: contexto (2), DFD e fronteiras (3), fluxos e ameaças (7), Top 10 e mitigações (2), lições (1). Comece pelo DFD como fio condutor. Cada integrante conduz o(s) fluxo(s) sob sua responsabilidade. Navegue com as setas; `S` abre o sumário; `F` entra em tela cheia.

### Slide 1: Capa

Abertura rápida (15 s). Apresentar a equipe e o objetivo: modelar ameaças do mesmo laboratório da M1, agora **de dentro para fora**, como na fase de projeto. Não é nova exploração: é modelagem.

### Slide 2: O que veremos

Mapa da fala (15 s). Seis blocos: contexto e método, modelo e DFD, os quatro fluxos, visão consolidada, validação e conclusão. Avisar que o DFD é o fio condutor.

### Slide 3: Contexto do ambiente

**~2 min.** Responde C1 a C10 de forma enxuta.

- **O sistema:** Juice Shop v20.2.0, SPA Angular + API Node/Express, SQLite e MarsDB, JWT RS256.
- **Implantação:** imagem fixada por tag e digest, publicada só em `127.0.0.1:3000`, em rede bridge isolada. Conduta: nada apontado para terceiros.
- **Atores e ativos:** visitante, cliente, admin e accounting; contas, credenciais, cesta, pedido e comprovante, com leitura à luz da LGPD.

Fonte: relatório da equipe e documentação do projeto.

### Slide 4: Método: DFD, STRIDE e DREAD

**~1 min.** As quatro perguntas de Shostack guiam o trabalho. DFD descreve o sistema; STRIDE por elemento identifica o que pode dar errado; DREAD prioriza de 1 a 10 com cada nota justificada. Fechar: cada ameaça liga-se a um requisito **ASVS 5.0**, a um **CWE** e, havendo dado pessoal, ao **art. 46 da LGPD**.

### Slide 5: Modelo do sistema e fronteiras

**~3 min — o coração da fala.** Percorra o DFD nível 1 da direita: entidades externas, os processos P2 a P6 do mesmo serviço Express, e os armazenamentos D1 a D5. Destaque as três fronteiras de confiança: **TB-01** cliente|servidor, **TB-02** host|contêiner e **TB-03** aplicação|armazenamentos. Mensagem: todo fluxo analisado cruza ao menos uma fronteira — é ali que a confiança muda.

### Slide 6: Os quatro fluxos

**~30 s.** Justificar a seleção: FX1 cobre a sessão; FX2 e FX3 tratam dados pessoais; FX4 é função privilegiada. Todos cruzam fronteira e três trazem achados da M1. Total: 25 cenários, com ≥ 6 por fluxo e cobertura das seis categorias STRIDE.

### Slide 7: FX1 · Login e sessão

**~1 min 45.** Ameaça mais grave do modelo: **T-FX1-02 injeção SQL (DREAD 9,8)** — e-mail concatenado à consulta, entrada anônima vira sessão de administrador (confirmada no T1, V1). Em seguida **T-FX1-04**: o JWT serializa a conta inteira, incluindo o hash **MD5 sem sal**, e não expira (V2). Mitigação: consulta parametrizada, claims restritos e Argon2id.

### Slide 8: FX2 · Cadastro e recuperação

**~1 min 45.** **T-FX2-06 (9,0):** o cadastro aceita `role: admin` do cliente (mass assignment) e cria a conta já como administrador — reproduzida ao vivo na M2. **T-FX2-01 (8,8):** pergunta de segurança consultável por e-mail e redefinição no 5º palpite dentro da cota (V7). Mitigação: papel só no servidor e recuperação de uso único.

### Slide 9: FX3 · Cesta, checkout e pedido

**~1 min 45.** **T-FX3-06 (8,4):** com um JWT válido lê-se a cesta de outra conta (IDOR); sem token, a rota recusa (V3). Reforçar a ideia: reconhecer a sessão não garante a titularidade do objeto. Apoio: comprovante exposto pelo diretório `/ftp/` (V5) e erro verboso (V4). Mitigação: autorização por objeto e servir arquivos só via API.

### Slide 10: FX4 · Administração e contabilidade

**~1 min 45.** Função privilegiada sobre vários titulares. **T-FX4-04 (8,6):** consulta de usuários sem verificação de papel; **T-FX4-06 (8,2):** exclusão de feedback sem exigir admin. Verificação de função desigual entre rotas. Mitigação: matriz de papéis no servidor, negar por padrão e registrar.

### Slide 11: Top 10 por DREAD

**~1 min.** Ler a ordenação: a injeção lidera com 9,8; o cadastro privilegiado vem em segundo (9,0). Dezoito dos 25 cenários são de risco alto; sete se apoiam em achados da M1. Mensagem: parametrizar o login resolve o mecanismo de injeção, mas o controle de acesso ainda precisa agir em cada recurso.

### Slide 12: Plano de mitigação

**~1 min.** Seis frentes com causa comum: autenticação e segredos; cadastro e recuperação; autorização em P4/P5; sessão e contenção; integridade do pedido; auditoria e erros. Cada frente tem **critério de aceite** verificável (ex.: a entrada V1 falha; nenhum JWT contém hash; duas contas não acessam recursos uma da outra).

### Slide 13: Validação no laboratório

**~1 min.** Diferencial da entrega: a execução complementar **foi realizada** em 08/11/2026 na mesma imagem (digest conferido). Reproduzimos ao vivo a injeção no login, o hash no JWT, o **cadastro role:admin** (T-FX2-06, antes só plausível), a leitura de cesta alheia, a listagem `/ftp/` e a cota do reset. O motor de desafios do próprio Juice Shop marcou *Login Admin, Admin Registration e View Basket* como resolvidos.

### Slide 14: Conclusão e lições

**~1 min.** As evidências se concentram em pontos diferentes: identidade (injeção), serialização (hash), autorização (cesta), recuperação (resposta previsível). Prioridade: autenticação, limitar o token e impedir atribuição de papel no cadastro. Lição M1→M2: reconhecer a sessão não garante a titularidade; modelar de dentro para fora complementa o teste.

### Slide 15: Obrigado

Encerramento (15 s). Agradecer, indicar o repositório com relatório, modelo e scripts, e abrir para perguntas.

## Apêndice · Perguntas prováveis (Q&A)

#### Por que DREAD e não OWASP Risk Rating?
O roteiro permite ambos; adotamos DREAD pela simplicidade e aplicamos a **mesma** escala a todos os cenários, com cada nota justificada. É subjetivo, por isso documentamos as âncoras de julgamento.

#### A injeção não foi corrigida nas versões novas do Juice Shop?
É uma aplicação deliberadamente vulnerável, fixada na tag v20.2.0 por digest para reprodutibilidade. O objetivo é modelar, não corrigir o upstream.

#### Qual a diferença entre "Confirmada no T1" e "Plausível"?
Confirmada = comportamento observado em requisição/resposta/captura da M1. Plausível = hipótese fundamentada em código, documentação ou teste upstream, sem reprodução pela equipe. Alguns cenários plausíveis foram reproduzidos na M2 (ex.: T-FX2-06).

#### Como a LGPD entra no modelo?
Classificamos dados pessoais (C5) e ligamos mitigações ao art. 46 (medidas técnicas) e ao princípio da necessidade (art. 6º), por exemplo verificar o titular antes de devolver um comprovante.

## Apêndice · Referências principais

- SHOSTACK, A. *Threat Modeling: Designing for Security*. Wiley, 2014.
- HERNAN, S. et al. *Uncover security design flaws using the STRIDE approach*. MSDN, 2006.
- MEIER, J. D. et al. *Improving Web Application Security* (DREAD). Microsoft, 2003.
- MANADHATA, P.; WING, J. *An attack surface metric*. IEEE TSE, 2011.
- OWASP ASVS 5.0.0; OWASP Top 10:2021; MITRE CWE.
- BRASIL. Lei nº 13.709/2018 (LGPD), arts. 5º, 6º e 46.
- SILVA, D. F. et al. *Case prático 1* (Trabalho 1). UNIVALI, 2026.
