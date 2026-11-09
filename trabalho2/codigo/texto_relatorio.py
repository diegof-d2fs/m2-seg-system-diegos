"""Texto e quadros do relatório que complementam o registro no modelo JSON."""

RESUMO = """
Este trabalho modela ameaças do OWASP Juice Shop v20.2.0, aplicação de comércio eletrônico desenvolvida para ensino de segurança. O objetivo é identificar em quais pontos do sistema os dados e as permissões ficam expostos e propor controles verificáveis para a arquitetura analisada. O modelo utiliza diagramas de fluxo de dados de contexto e detalhado, com recortes de login e sessão, cadastro e recuperação de senha, cesta e pedido, administração e contabilidade. A análise aplica STRIDE por elemento e prioriza os cenários pelo método DREAD. As evidências HTTP e as capturas do Trabalho 1 foram comparadas com o código da versão e seus testes publicados. O registro reúne 25 cenários, dos quais sete se apoiam em evidências do laboratório anterior e 18 permanecem plausíveis. A injeção SQL no login obteve a maior pontuação, 9,8, por permitir a entrada como administrador a partir de uma requisição anônima. A análise também apontou falhas de titularidade na cesta, exposição de hash em token, recuperação de senha por resposta previsível e verificações de papel desiguais entre rotas administrativas e contábeis. O plano de tratamento associa requisitos do OWASP ASVS 5.0.0 e critérios de aceite a cada cenário, considerando a proteção de dados pessoais nos fluxos analisados.
"""

INTRO = """
Uma falha na autenticação altera as condições sob as quais a loja protege os dados. Na avaliação do Trabalho 1, uma requisição ao login do Juice Shop obteve sessão administrativa sem apresentar a senha correta. Em outro ensaio, o token válido de um cliente permitiu consultar a cesta de outra conta. O primeiro resultado afetou a identidade atribuída à sessão e o segundo mostrou que reconhecer uma sessão não assegura, por si só, a titularidade do recurso. A modelagem parte dessa diferença para determinar onde cada controle precisa atuar (SILVA et al., 2026).

O objetivo geral é identificar e priorizar ameaças em quatro funções da versão v20.2.0 e transformar os cenários de maior risco em requisitos de segurança com critérios de aceite. Para isso, o trabalho descreve a implantação, classifica os dados, representa as fronteiras de confiança e relaciona os achados da M1 às rotas e aos componentes examinados. A questão que orienta a análise é em quais pontos a aplicação aceita uma identidade, um identificador ou uma operação controlada pelo cliente sem verificar a permissão exigida pelo ativo.

O recorte abrange login local e sessão, cadastro e recuperação, cesta e pedido, administração e contabilidade. O ambiente de referência é a implantação local descrita no Compose da M1. O login externo, o chatbot e outros pontos de entrada aparecem na contextualização como parte da superfície conhecida. A exploração, a observação de tráfego e a reprodução de cenários só se aplicam a instâncias de teste autorizadas.

A fundamentação define os critérios usados para modelar e priorizar. A contextualização fixa a versão e os limites do laboratório. Os capítulos seguintes documentam o método, os diagramas e as fichas dos quatro fluxos. A visão consolidada organiza o tratamento, e a validação relaciona evidências, hipóteses e testes pendentes.
"""

THEORY = [
("2.1 MODELAGEM DE AMEAÇAS NO SSDLC", """
A modelagem de ameaças identifica condições em que um agente pode comprometer ativos durante o uso previsto de um sistema. No ciclo de vida de desenvolvimento seguro de software, ou Secure Software Development Life Cycle (SSDLC), ela transforma características de projeto em requisitos e casos de verificação. No Secure Software Development Framework (SSDF), Souppaya, Scarfone e Dodson (2022) recomendam, na prática PW.1.1, modelar ameaças e superfícies e considerar relatórios anteriores de vulnerabilidades. Neste estudo, esses relatórios sustentam a análise de pontos do Juice Shop cujo comportamento já foi observado.

Shostack (2014) organiza o trabalho em quatro perguntas. A primeira descreve o sistema construído, a segunda identifica o que pode dar errado, a terceira define o tratamento e a quarta verifica se o modelo e as decisões atendem ao objetivo. Tuma, Çalikli e Scandariato (2018) comparam métodos de análise e identificam limitações na definição de procedimentos e na garantia de qualidade dos resultados. A distinção entre evidência de execução, inspeção de código e hipótese de ataque responde a esse problema no recorte adotado. Ela também indica que tipo de teste pode mudar a conclusão de cada cenário.
"""),
("2.2 DFD E FRONTEIRAS DE CONFIANÇA", """
O Diagrama de Fluxo de Dados (DFD) representa entidades externas, processos, armazenamentos e transferências. A entidade fornece ou recebe informações fora do sistema modelado. O processo as transforma e o armazenamento conserva dados, em memória ou em disco. As setas identificam a informação que passa entre elementos. Uma fronteira de confiança marca a mudança nas garantias com que os dados podem ser usados ou nas permissões necessárias para acessá-los (HERNAN et al., 2006).

O nível 0 concentra a aplicação em um processo e explicita suas interfaces externas. O nível 1 mantém essas interfaces e decompõe a operação interna. No laboratório, a separação entre a SPA no navegador e a API no contêiner implica duas verificações distintas. A primeira diz respeito à origem não confiável dos dados. A segunda descreve por onde a rede entrega a requisição. A passagem para SQLite, memória e arquivos marca uma fronteira lógica. Esses recursos compartilham permissões do processo da aplicação.
"""),
("2.3 STRIDE POR ELEMENTO", """
STRIDE reúne seis categorias de ameaça, apresentadas no Quadro 1. A classificação orienta o analista a verificar de que modo a autenticidade, a integridade, o não repúdio, a confidencialidade, a disponibilidade ou a autorização podem ser comprometidos (HERNAN et al., 2006). A classificação do cenário descreve a propriedade afetada em primeiro plano. Por exemplo, alterar a consulta SQL do login é adulteração no processo, com uma consequência de elevação de privilégio. A modelagem registra esse mecanismo uma vez para o ranking.

O roteiro aplica S e R a entidades, as seis categorias a processos e T, I e D a fluxos e armazenamentos. A categoria R também se aplica ao armazenamento de logs. Scandariato, Wuyts e Joosen (2015) avaliaram a técnica em termos de produtividade, ameaças incorretas e ameaças omitidas. O preenchimento de uma matriz fornece cobertura de análise. A verificação de uma ameaça depende, além disso, da aderência do cenário à rota, ao papel do agente e à evidência disponível.
"""),
("2.4 SUPERFÍCIE DE ATAQUE E PRIORIZAÇÃO", """
A superfície de ataque compreende os canais, métodos e dados com que um agente consegue interagir. Manadhata e Wing (2011) tratam esses elementos como recursos que contribuem para a exposição de um sistema. No Juice Shop, uma rota, um parâmetro do corpo, um token ou um diretório podem ampliar a superfície por permitir operações diferentes. Uma rota alcançável compõe o inventário. A demonstração de uma falha depende do que o servidor aceita ou devolve por essa rota.

O DREAD organiza a avaliação em potencial de dano, reprodutibilidade, explorabilidade, usuários afetados e facilidade de descoberta (MEIER et al., 2003). Alves et al. (2024) aplicam STRIDE e DREAD a um sistema IoT, com identificação e priorização em momentos distintos. Neste estudo, as notas de 1 a 10 expressam julgamento situado no laboratório e seguem a escala do roteiro. A metodologia explicita critérios e desempates. O resultado serve para ordenar a análise e planejar o tratamento. Na M1, a equipe usou CVSS 3.1 para caracterizar a severidade dos achados reproduzidos (SILVA et al., 2026). O NIST (2012) também distingue avaliação de risco de inventário de vulnerabilidades ao considerar condições, impacto e probabilidade.
"""),
("2.5 REQUISITOS DE SEGURANÇA E DADOS PESSOAIS", """
O OWASP Application Security Verification Standard (ASVS) fornece requisitos verificáveis para decisões como validar um token ou restringir acesso por objeto. O Common Weakness Enumeration (CWE) descreve tipos de fraqueza. O OWASP Top 10:2021 conserva a classificação histórica usada na M1 (OWASP FOUNDATION, 2021). Os guias da OWASP detalham práticas de implementação (OWASP FOUNDATION, [s. d.]). O registro usa cada referência segundo essa finalidade (MITRE, [s. d.]). Os números de verificação seguem a versão 5.0.0 do ASVS (OWASP FOUNDATION, 2025).

O art. 5º da Lei Geral de Proteção de Dados Pessoais (LGPD) define dado pessoal e estabelece categorias específicas para dados pessoais sensíveis. O princípio da necessidade do art. 6º, III orienta a redução do conteúdo em respostas, tokens e logs. O art. 46 prevê medidas técnicas e administrativas para a proteção contra acesso não autorizado e eventos acidentais ou ilícitos. Carneiro, Kudo e Bulcão Neto (2024) propõem transformar disposições da LGPD em padrões de requisitos de software. Na aplicação modelada, esse vínculo aparece em critérios concretos, como verificar o titular antes de devolver um PDF de pedido e omitir o hash das respostas de recuperação (BRASIL, 2018).
"""),
]

STRIDE_ROWS = [
("S / Spoofing","Falsificação de identidade","Autenticidade"),
("T / Tampering","Alteração indevida de dados ou lógica","Integridade"),
("R / Repudiation","Contestação de autoria sem evidência suficiente","Não repúdio"),
("I / Information Disclosure","Exposição de informação a agente indevido","Confidencialidade"),
("D / Denial of Service","Indisponibilidade ou degradação da operação","Disponibilidade"),
("E / Elevation of Privilege","Acesso a função ou recurso além da permissão","Autorização"),
]

CONTEXT = [
("3.1 IDENTIFICAÇÃO E VERSÃO C1", """
O OWASP Juice Shop é uma loja fictícia criada para treinamento em segurança de aplicações web. O projeto é mantido por colaboradores da OWASP e reúne desafios deliberados em uma interface de comércio eletrônico. A M1 implantou a imagem oficial bkimminich/juice-shop:v20.2.0. O README da equipe registra o digest abaixo, obtido durante a inspeção inicial da imagem. O Compose fixa a tag e permite conferir o digest em uma nova implantação (OWASP JUICE SHOP, 2026). O registro da equipe conserva o identificador histórico (SILVA et al., 2026).
"""),
("3.2 ARQUITETURA E COMUNICAÇÃO C2", """
A interface é uma aplicação de página única (SPA), construída em Angular e TypeScript. O Node.js executa o servidor Express e fornece operações HTTP em JSON, incluindo recursos gerados por finale-rest e rotas implementadas diretamente. O SQLite é acessado por Sequelize. A configuração normal abre data/juiceshop.sqlite, enquanto o código prevê uma opção em memória. A coleção de pedidos usa MarsDB no processo. A cesta e os registros de conta ficam em SQLite. O comprovante do pedido é um PDF gravado no diretório ftp/ (OWASP JUICE SHOP, 2026).

A autenticação local emite JSON Web Token (JWT) assinado. A SPA o guarda em localStorage e cookie e envia o bearer pelo interceptor, enquanto o servidor mantém um mapa de tokens e usuários autenticados. A presença desse mapa importa para a leitura de cesta e de perfil. Socket.IO atende notificações e funcionalidades do projeto. O código também contém Google OAuth, API de pedidos B2B e chatbot. Essas integrações integram o inventário de entradas, com análise detalhada restrita aos quatro fluxos escolhidos.
"""),
("3.3 IMPLANTAÇÃO DO LABORATÓRIO C3", """
Na M1, o host Windows com Docker Desktop executou o contêiner juice-shop na bridge labnet. O Compose publica a porta interna 3000 em 127.0.0.1 na porta configurável JUICESHOP_HTTP_PORT, cujo padrão é 3000. A implantação usa HTTP sem TLS definido no Compose. A rede vulnerable-web-application_labnet e a sub-rede 172.19.0.0/16 constam do registro histórico. O Compose não fixa a sub-rede. A documentação do Docker distingue o endereço publicado no host, o alcance dentro da bridge e as conexões de saída (DOCKER, [s. d.]). Por isso, o vínculo ao loopback limita a publicação no host e deve ser tratado separadamente do acesso de outros serviços na bridge e da política de saída.

O serviço usa restart: unless-stopped. A verificação HTTP de saúde é feita pelo Node.js em intervalo de 10 segundos, com timeout de 5 segundos, seis falhas consecutivas e período inicial de 20 segundos. O Compose não declara volume, e o servidor inicializa a base com sincronização forçada no código dessa versão. A disponibilidade do histórico depende do ciclo de vida dos armazenamentos e da instância. A análise da implantação é documental e preserva o digest histórico como dado da M1 (SILVA et al., 2026). O Dockerfile da tag indica execução como UID 65532 (OWASP JUICE SHOP, 2026).
"""),
("3.4 ATORES E PERMISSÕES C4", """
O Quadro 2 separa o papel esperado na loja dos controles observados em cada rota. O operador do host tem capacidades sobre o ambiente de execução. Os papéis de cliente, administrador e contabilidade são atributos da aplicação. O código aplica controles próprios a rotas de pedidos contábeis, e as guardas Angular definem a navegação do painel (OWASP JUICE SHOP, 2026).
"""),
("3.5 ATIVOS E CLASSIFICAÇÃO DE DADOS C5", """
Os ativos que sustentam as quatro funções incluem contas, credenciais, sessão, cesta, pedido e comprovante. O quadro identifica os dados que seriam pessoais quando se referissem a pessoa natural identificada ou identificável. Os registros examinados foram de teste ou demonstração. O art. 5º, II, da LGPD reserva a classe sensível a categorias determinadas, entre elas saúde, origem racial ou étnica e biometria vinculada à pessoa. Senha, token e cartão exigem proteção pelo risco e pela finalidade. Esses campos, em si, não se enquadram nas categorias legais sensíveis (BRASIL, 2018).
"""),
("3.6 PONTOS DE ENTRADA C6", """
A superfície do laboratório inclui HTTP, a SPA, APIs e arquivos. As interfaces administrativas compartilham a porta do serviço. O fragmento de URL usado pelo Angular seleciona uma tela no navegador e a tela faz requisições HTTP distintas à API. As entradas evidenciadas na M1 e as interfaces localizadas somente no código estão diferenciadas no Quadro 4 (SILVA et al., 2026). O inventário considera canais e dados no sentido de Manadhata e Wing (2011) e da orientação da OWASP (OWASP FOUNDATION, [s. d.]).
"""),
("3.7 DEPENDÊNCIAS RELEVANTES C7", """
O Quadro 5 relaciona as dependências declaradas nos manifests da tag v20.2.0 e seu papel na análise. O circunflexo indica a faixa declarada. A versão resolvida na imagem da M1 depende de inspeção da imagem. O relatório usa o comportamento e as evidências da rota para caracterizar fraquezas. A presença de uma dependência, por si só, não constitui diagnóstico de CVE.
"""),
("3.8 INVENTÁRIO E SELEÇÃO DE FLUXOS C8", """
Foram identificadas cinco funcionalidades candidatas. O Quadro 6 registra os quatro recortes analisados e um fluxo de reserva. A seleção cobre sessão em FX1, dados pessoais em FX2 e FX3 e ações privilegiadas em FX4. Todos os fluxos selecionados atravessam a interface cliente-servidor e chegam a pelo menos um armazenamento. Três contêm evidência do Trabalho 1.
"""),
("3.9 PREMISSAS E DELIMITAÇÃO C9", """
O agente modelado é uma pessoa com acesso ao laboratório, com ou sem conta, ou um operador de papel definido. A capacidade de controlar o próprio cliente e a entrada da API faz parte do cenário. O host, o motor do Docker e o ambiente de rede local são assumidos íntegros. A possibilidade de roubo ou reuso de token é avaliada com a obtenção da credencial como precondição. O modelo não mede ataques de rede volumétricos, comprometimento do host, segurança física, terceiros externos, infraestrutura de nuvem ou a totalidade dos desafios da plataforma.

O código de Google OAuth, chatbot, B2B, métricas e upload ajuda a delimitar a superfície. O recorte detalhado não depende de credenciais de terceiro, de dados reais de cartão ou de transações externas. Os testes de carga, exploração de hipóteses e validação das mitigações propostas requerem execução própria em instância controlada.
"""),
("3.10 RELAÇÃO COM OS ACHADOS DO TRABALHO 1 C10", """
O Quadro 7 vincula os sete achados históricos ao DFD e ao registro. A pontuação CVSS 3.1 vem da M1 e mantém a classificação histórica. V4 ocorreu no tratamento do cabeçalho em uma rota de cesta. V5 comprova a exposição do diretório e de documento de exemplo, sustentando uma hipótese distinta sobre PDFs de pedido. Os registros de V7 mostram sucesso no quinto palpite e a cota informada de 100 solicitações. A evidência não caracteriza tentativas ilimitadas. Injeção NoSQL, XSS e upload inseguro não figuram entre V1 e V7 no repositório da M1.
"""),
]

ACTORS = [
("E1 / visitante","Sem sessão. Usa cadastro, recuperação, login, catálogo e arquivos públicos."),
("E2 / customer e deluxe","Opera a própria cesta e pedidos. Deluxe tem benefícios condicionados ao papel e ao token de associação."),
("E3 / admin","Consulta usuários e modera feedbacks pela interface prevista. A análise verifica a permissão na API separadamente."),
("E4 / accounting","Consulta pedidos e modifica entrega em rotas com verificação de papel. A alteração de estoque, fora do recorte detalhado, também usa filtro de IP no servidor."),
("Operador do host","Gerencia rede, processo, contêiner e arquivos. Sua integridade é premissa do laboratório."),
("Serviços externos","Google OAuth e API de modelo para chatbot aparecem em configuração. O Compose não provisiona esses serviços."),
]
ASSETS = [
("Identificação e contato","E-mail, nome, endereço, telefone, IP quando vinculável.","Dados pessoais quando se referem a titular identificável."),
("Credenciais e sessão","Senhas, hashes, resposta de segurança, JWT e segredo TOTP quando configurado.","Segredos de autenticação. Alguns também se vinculam ao titular."),
("Cesta e pedido","Itens, valores, endereço, estado de entrega e comprovante.","Dados pessoais quando associados à conta. A operação exige integridade."),
("Cartão e carteira","Número, nome, validade e saldo na simulação.","Dados de pagamento. Cartões do laboratório são fictícios."),
("Catálogo, feedback e arquivos","Preços públicos, conteúdo de avaliação e documentos de demonstração.","A classificação depende da finalidade, do vínculo pessoal e do conteúdo."),
("Disponibilidade e trilha","Capacidade de atender login, compra e operações privilegiadas. Registros de acesso.","Ativos operacionais. Os registros podem conter dados pessoais."),
]
SURFACE = [
("Rede","HTTP TCP 3000 em loopback e serviço na bridge. Socket.IO integra o servidor. TB-01 e TB-02."),
("Interface de usuário","Login, cadastro, recuperação, busca, itens, checkout. F09 a F14. A M1 registra login, reset e leitura de cesta."),
("Administrativa","/#/administration, /#/accounting e respectivas APIs. F15 e F16. /metrics existe no código e fica fora dos quatro recortes."),
("Integração externa","Google OAuth e proxy auxiliar, /b2b/v2/orders, /rest/chat e URL local de API de modelo. Código e configuração, sem uso comprovado na M1."),
("Dados e arquivos","Corpos JSON, parâmetros, cookies, JWT, SQLite e PDFs. /file-upload consta do código. /ftp/ é caminho HTTP e a M1 comprovou sua listagem em V5."),
]
DEPS = [
("Angular","^22.0.1","Interface e guardas de navegação. Chamadas diretas continuam sujeitas à API."),
("Express e finale-rest","^4.22.1 e ^1.2.2","Middlewares e CRUD. A autorização depende da rota e da configuração do recurso."),
("Sequelize e sqlite3","^6.37.3 e ^5.1.7","Persistência local. A consulta bruta de login não usa a proteção de parâmetros do ORM."),
("jsonwebtoken e express-jwt","0.4.0 e 0.1.3","Emissão e validação de JWT. Opções e claims precisam ser coerentes com a implementação usada."),
("express-rate-limit","^7.5.1","Cota de reset. A chave de IP e a confiança no proxy afetam o controle."),
("MarsDB e Socket.IO","^0.6.11 e ^3.1.2","Coleções em memória e comunicação em tempo real, respectivamente."),
("Morgan, serve-index e PDFKit","Manifests da tag","Registro HTTP, listagem de arquivos e geração de comprovantes."),
]
CANDIDATES = [
("FX1","Login e uso da sessão","Selecionado","F09 e F10. Sustenta a identidade das demais funções. V1, V2 e V6."),
("FX2","Cadastro e recuperação de senha","Selecionado","F11 e F12. Grava dados de conta e expõe mecanismo de recuperação. V7."),
("FX3","Cesta, checkout e pedido","Selecionado","F13, F14, F17 e F18. Trata dados de compra e comprovante. V3 e V4. V5 apoia análise de arquivos."),
("FX4","Administração e contabilidade","Selecionado","F15 e F16. Permissões de função e de acesso a dados de vários titulares."),
("FX5","Login com Google OAuth","Reserva","Depende de provedor e redirecionamento externo. O Compose do laboratório não comprova sua operação."),
]

METHOD = [
("4.1 ETAPAS E FONTES DE EVIDÊNCIA", """
A análise documental começou pelo Compose, pelo relatório e pelos artefatos da M1. O código e os testes upstream foram fixados na tag v20.2.0, com identificação dos commits no Apêndice A. Os registros históricos foram consultados para recuperar método, rota, status, conteúdo relevante e precondições dos ensaios. A validação de dados do modelo e o cálculo das médias foram feitos em Python. Os diagramas foram exportados para SVG e para um arquivo editável do diagrams.net. A reconstrução da arquitetura considerou rotas, modelos, serviços Angular, middlewares e arquivos de configuração.

O estado Confirmada no T1 é reservado ao comportamento observado em requisição, resposta ou captura histórica da equipe. Um achado pode sustentar mais de um cenário quando a evidência mostra efeitos distintos, como consulta da pergunta e tomada de conta em V7. Plausível identifica hipótese fundamentada em código, documentação, teste upstream ou mecanismo conhecido, sem reprodução pela equipe. O estado Tratada por controle existente se aplicaria quando houvesse evidência de que o controle cobre o cenário. Os controles que cobrem apenas uma variante, como a unicidade da resposta de segurança, permanecem documentados como limites da hipótese.
"""),
("4.2 CONVENÇÕES E APLICAÇÃO DO STRIDE", """
Os identificadores E, P, D, F e TB designam entidades, processos, armazenamentos, setas e fronteiras. Um identificador FX representa uma funcionalidade composta por várias setas F. As tabelas de percurso indicam as transferências que o recorte cobre, sem converter o DFD em uma sequência obrigatória de execução. Os identificadores T-FX<n>-<nn> identificam cenários e ligam a ficha, a matriz, o questionário e o registro. A primeira referência de cada ameaça indica o elemento principal usado na contagem consolidada.

A matriz contém uma linha para cada elemento e seta do recorte. O ID em uma célula indica a ameaça associada à propriedade examinada. As células com N/A remetem a justificativas de escopo ou aplicabilidade. Células vazias indicam que a categoria não se aplica ao tipo segundo a matriz do roteiro. Um cenário mantém uma categoria principal mesmo quando produz efeitos adicionais. As perguntas Q1 a Q7, S1 a E3 e V1 a V3 são respondidas em cada fluxo. Os V do questionário de fechamento pertencem ao formulário. Quando o texto menciona um achado da M1, identifica-o como tal.
"""),
("4.3 CRITÉRIOS DE PONTUAÇÃO DREAD", """
A média de cada cenário usa as cinco notas com pesos iguais. O cálculo soma dano, reprodutibilidade, explorabilidade, usuários afetados e descoberta, e divide o total por cinco. O Quadro 8 indica âncoras de julgamento comuns aos quatro fluxos. A escala efetiva vai de 1 a 10. Conforme o roteiro, resultados de 0 a 3,9 são classificados como baixos, de 4,0 a 6,9 como médios e de 7,0 a 10 como altos. Um valor zero não ocorre com a regra de notas adotada.

A média é exibida com uma casa decimal. O ranking usa a soma exata, equivalente à média para cinco notas inteiras. Empates são resolvidos pela confirmação histórica, pelo dano e, por fim, pelo ID. A ordem resulta de uma avaliação relativa no ambiente acadêmico. Mudanças de precondição, volume de dados, exposição ou evidência justificam revisar as notas. Os cenários foram pontuados na condição atual do laboratório. O risco residual após os controles foi descrito em termos qualitativos, pois os controles ainda exigem implantação e verificação.
"""),
("4.4 DIVISÃO DO TRABALHO E TRATAMENTO", """
O quadro de participação reúne as contribuições registradas e propõe uma divisão para a revisão final. Cada ameaça recebeu uma decisão, um tipo de controle, uma camada e um critério de aceite. O tratamento mantém a função de negócio e altera a implementação que gera exposição.
"""),
]

ANCHORS = [
("Dano","Impacto pontual, sem comprometimento de ativo relevante.","Dado ou operação de uma conta afetados, com possibilidade de correção.","Tomada de conta, ação privilegiada, perda ampla ou degradação relevante."),
("Reprodutibilidade","Exige condições raras e difíceis de manter.","Depende de estado específico, concorrência ou configuração.","A mesma sequência tende a produzir efeito em condição conhecida."),
("Explorabilidade","Exige acesso especial, material raro ou técnica avançada.","Exige uma conta, estado alvo ou algum conhecimento da API.","Rota alcançável e ação simples com ferramentas comuns."),
("Usuários afetados","Um evento isolado ou um recurso de uso restrito.","Parte dos titulares ou várias ocorrências de uma conta.","Vários titulares, uma classe de papéis ou a instância compartilhada."),
("Descoberta","Ponto obscuro com pouca observabilidade.","Inspeção da rota, do código ou dos registros.","Superfície pública ou campo evidente no contrato ou nas respostas."),
]

MODEL_CONTEXT = """
A Figura 1 concentra o recorte em P0. As entidades são atores humanos externos ao sistema lógico. A interface mais próxima de cada ator se mantém na Figura 2, que detalha a SPA em P1, executada sob controle do navegador. O operador do Docker aparece no contexto do laboratório. Seus comandos de gestão e integrações fora dos quatro fluxos não são setas do DFD.
"""
MODEL_DETAIL = """
No nível 1, P2 a P6 representam responsabilidades do mesmo serviço Express. SQLite, mapa de sessões, pedidos, arquivos e logs aparecem como armazenamentos distintos. A duplicação visual de D1, D2, D3, D4 e D5 facilita a leitura e conserva o mesmo ID para o mesmo recurso. As setas F01 a F08 preservam as interfaces de P0. As demais setas detalham a transferência entre interface, API e armazenamento.
"""
MODEL_BOUNDARIES = """
A separação lógica em TB-03 não cria uma conexão de banco pela rede nem uma conta de serviço por módulo. A confiabilidade da resposta depende do filtro e da autorização aplicados no processo antes da consulta. De modo semelhante, TB-01 e TB-02 descrevem propriedades diferentes da mesma passagem de rede. A validação de entrada pertence ao servidor, e o isolamento de rede pertence à implantação. A SPA e seu armazenamento permanecem do lado cliente.
"""

PLAN = [
("1","Autenticação, emissão e segredos","T-FX1-02, 04 e 06","Parametrizar consulta, restringir claims, migrar hash de senha e rotacionar chave com revogação de JWT antigo.","A entrada V1 falha. Nenhum JWT ou retorno de perfil contém hash. Chaves antigas são rejeitadas."),
("2","Cadastro e recuperação","T-FX2-06, 01, 02 e 04","Atribuir papel no servidor, substituir pergunta por recuperação de uso único e uniformizar respostas. Remover o vínculo público baseado em UserId.","Cadastro força customer. Reset não enumera contas e token de recuperação não pode ser reutilizado."),
("3","Autorização em P4 e P5","T-FX4-04 e 06, T-FX3-06, 02 e 07","Adotar política de função nas rotas privilegiadas e política de titularidade em cesta, pedido, endereço, pagamento e comprovante.","Matriz de papéis nega chamadas indevidas. Duas contas não acessam nem alteram recursos uma da outra."),
("4","Ciclo de sessão e contenção","T-FX1-01 e 05, T-FX3-01, T-FX4-01, T-FX2-05","Aplicar limites por conta e origem, expiração efetiva, revogação e validação atual de papéis. Tratar sessões e capacidade de armazenamento.","Replay após logout, expiração ou rebaixamento falha. Amostra com abuso controlado preserva operação legítima."),
("5","Integridade e disponibilidade de pedidos","T-FX3-02 e 05, T-FX4-02 e 05","Introduzir idempotência, controle de versão, quota de PDF, paginação e procedimento de compensação em falhas parciais.","Reenvio não duplica pedido. Escrita concorrente é detectada e listagens respeitam o limite."),
("6","Auditoria e retorno de erros","T-FX1-03, T-FX2-03, T-FX3-03 e 04, T-FX4-03","Centralizar eventos de autenticação, reset, compra e ações privilegiadas em trilha protegida. Remover versão e detalhes de erro do cliente.","Eventos correlacionáveis com dados mínimos. Resposta de falha sem detalhe interno."),
]

CONSOLIDATED = """
A ordenação agrega os 25 cenários com o mesmo critério. Das 25 ameaças, 18 atingiram risco alto e sete, risco médio. Sete registros se apoiam em seis achados da M1. O sétimo achado histórico, V5, fundamenta a exposição do canal de arquivos, enquanto a leitura de um comprovante de pedido permanece plausível. A maior pontuação, 9,8, é da injeção no login. A segunda, 9,0, corresponde à hipótese de atribuição de papel privilegiado no cadastro. O status acompanha a média porque uma evidência observada e uma hipótese podem receber valores próximos e exigir verificações distintas.

A consulta de usuários e a moderação de feedback requerem permissão de função. A cesta e o comprovante requerem permissão sobre o objeto. Parametrizar a autenticação corrige o mecanismo de injeção, mas as falhas de acesso ainda precisam de autorização no ponto que lê ou altera o recurso. O controle de sessão é compartilhado, e a implementação proposta deve ser verificada nas rotas que usam mecanismos distintos. A retenção e a minimização entram tanto no token e na resposta da API quanto na trilha de auditoria.
"""

VALIDATION = [
("8.1 CONFERÊNCIA DOCUMENTAL E HISTÓRICA", """
A conferência comparou os pontos de entrada dos diagramas com server.ts e com os serviços da SPA. Na M1, os pares HTTP sustentam a SQL injection de login, a presença de hash no JWT, a leitura de cesta alheia, o erro verboso, a listagem em /ftp/, a sequência de falhas de autenticação e o reset com resposta previsível. O Apêndice B reúne capturas e extratos com valores de credenciais omitidos. As Figuras 7 a 11 são históricas. As verificações de checkout completo e de administração foram reconstruídas pelo código e pelos testes publicados na tag.

A leitura de dois JWTs históricos encontrou alg RS256 e as chaves data, bid e iat, sem exp. Na distribuição oficial inspecionada, jsonwebtoken 0.4.0 grava exp quando recebe expiresInMinutes. O código da aplicação fornece expiresIn. O prazo de oito horas configurado no cookie pela SPA tampouco demonstra validade no servidor. A análise conserva essas evidências separadas para que um novo teste possa verificar expiração por rota.

Os cabeçalhos de V7 diminuem de 99 para 95 nas cinco solicitações de reset. O último retorno foi HTTP 200, seguido de login com a nova senha. O teste negativo de associação duplicada recebeu HTTP 400. A primeira evidência demonstra que a cota não impediu um palpite correto nessa amostra. A segunda restringe a hipótese de adulteração às condições em que ainda exista uma associação elegível ou insuficientemente protegida. O comportamento após a cota e a influência de proxy seguem em aberto.

A validação estrutural verificou identificadores e tipos, ligação de setas a processos, consistência entre os níveis do DFD, presença de fronteira em cada recorte, correspondência das matrizes com os registros e presença de 28 respostas por fluxo. O ranking foi recalculado a partir das cinco notas de cada cenário. Essas verificações tratam da coerência do modelo e do vínculo com suas fontes.
"""),
("8.2 REVISÃO CRUZADA ENTRE INTEGRANTES", """
O quadro a seguir distribui uma revisão independente da pessoa indicada para cada recorte. O revisor deve conferir rotas e fronteiras na versão, testar a compatibilidade da ameaça com o papel do agente, verificar evidência e status e recalcular a pontuação. A revisão deve registrar o resultado e as correções por fluxo. A confirmação individual permanece pendente.
"""),
("8.3 LIMITAÇÕES E VERIFICAÇÕES PENDENTES", """
A base de observação direta corresponde aos artefatos da M1. A execução complementar não produziu novas capturas. A análise estática sustenta o percurso funcional de checkout, moderação e contabilidade, mas não documenta o resultado em uma nova execução da imagem do laboratório. Também não houve ensaio de carga, expiração, revogação ou concorrência, nem avaliação de todas as rotas privilegiadas. O digest, a rede e a porta da M1 são evidências da implantação histórica.

A próxima conferência no laboratório deve registrar, com dados fictícios, criação de conta e recuperação, checkout e download de comprovante, e chamadas administrativas por papel. Os testes de autorização devem usar duas contas de cliente e os papéis admin e accounting. A coleta deve preservar método, rota, status, versão e papel, omitir credenciais e distinguir chamadas permitidas das recusadas. Para mitigações de disponibilidade, critérios numéricos de capacidade dependem de medição na instância. A DREAD ordena cenários no recorte, sem estimar frequência de incidentes ou exposição em produção.
"""),
]

CONCLUSION = """
A análise localizou quatro funções nas quais uma decisão do servidor tem efeito direto sobre conta, cesta, pedido ou operação privilegiada. O uso de DFD e STRIDE por elemento mostrou que as evidências da M1 se concentram em pontos diferentes. A SQL injection altera a consulta que determina a identidade. O hash exposto decorre da serialização da conta no JWT. A leitura de cesta alheia ocorre depois que a sessão já foi aceita. A recuperação combina uma pergunta publicamente consultável com uma prova previsível. Essas diferenças determinam o controle e o teste adequados para cada caso.

A prioridade é corrigir a autenticação, limitar o material emitido na sessão e impedir que o cadastro público atribua funções reservadas. A correção do controle de acesso deve alcançar as APIs administrativas, as referências do checkout e a entrega de comprovantes. As medidas de auditoria, contenção e idempotência completam o tratamento ao reduzir contestação, degradação e efeitos de escritas repetidas.

O modelo registra 25 cenários, explicita os resultados observados na M1 e separa as hipóteses que ainda precisam de evidência de laboratório. Os critérios de aceite permitem conferir as medidas propostas com contas de teste e o mesmo conjunto de rotas. A revisão cruzada e a validação funcional das hipóteses são as próximas verificações que podem alterar o status ou a prioridade dos cenários.
"""

# Duplo asterisco indica a parte de destaque de cada referência.
BIB = [
"ALVES, Luis Fernando et al. Modelagem de ameaças com STRIDE e DREAD: uma análise preliminar aplicada a um sistema IoT. In: ESCOLA REGIONAL DE ENGENHARIA DE SOFTWARE, 8., 2024. **Anais [...]**. Porto Alegre: Sociedade Brasileira de Computação, 2024. p. 218-227. DOI 10.5753/eres.2024.4319. Disponível em: https://sol.sbc.org.br/index.php/eres/article/download/31855/31657/. Acesso em: 8 nov. 2026.",
"BRASIL. **Lei nº 13.709, de 14 de agosto de 2018**. Lei Geral de Proteção de Dados Pessoais (LGPD). Brasília, DF: Presidência da República, 2018. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm. Acesso em: 8 nov. 2026.",
"CARNEIRO, Cinara Gomes de Melo; KUDO, Taciana Novo; BULCÃO NETO, Renato de Freitas. Um método para transformação de requisitos legais em padrões de requisitos de software: um estudo com a LGPD. In: CONGRESSO IBERO-AMERICANO EM ENGENHARIA DE SOFTWARE, 27., 2024, Curitiba. **Anais [...]**. Porto Alegre: Sociedade Brasileira de Computação, 2024. p. 348-355. DOI 10.5753/cibse.2024.28460. Disponível em: https://sol.sbc.org.br/index.php/cibse/article/download/28460/28270/. Acesso em: 8 nov. 2026.",
"DOCKER. **Docker Engine networking**. Seções Bridge network driver e Port publishing and mapping. [S. l.]: Docker, [s. d.]. Disponível em: https://docs.docker.com/engine/network/drivers/bridge/ e https://docs.docker.com/engine/network/port-publishing/. Acesso em: 8 nov. 2026.",
"HERNAN, Shawn et al. Uncover security design flaws using the STRIDE approach. **MSDN Magazine**, nov. 2006. Disponível em: https://learn.microsoft.com/en-us/archive/msdn-magazine/2006/november/uncover-security-design-flaws-using-the-stride-approach. Acesso em: 8 nov. 2026.",
"MANADHATA, Pratyusa K.; WING, Jeannette M. An attack surface metric. **IEEE Transactions on Software Engineering**, v. 37, n. 3, p. 371-386, 2011. DOI 10.1109/TSE.2010.60. Disponível em: https://manadhata.github.io/pdf/tse11.pdf. Acesso em: 8 nov. 2026.",
"MEIER, J. D. et al. Threat modeling. In: MEIER, J. D. et al. **Improving web application security: threats and countermeasures**. [S. l.]: Microsoft, 2003. cap. 3. Disponível em: https://learn.microsoft.com/en-us/previous-versions/msp-n-p/ff648644(v=pandp.10). Acesso em: 8 nov. 2026.",
"MITRE. **Common Weakness Enumeration**. [S. l.]: MITRE, [s. d.]. Disponível em: https://cwe.mitre.org/. Acesso em: 8 nov. 2026.",
"NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY (NIST). **Guide for conducting risk assessments**. Gaithersburg: NIST, 2012. NIST SP 800-30, rev. 1. DOI 10.6028/NIST.SP.800-30r1. Disponível em: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf. Acesso em: 8 nov. 2026.",
"OWASP FOUNDATION. **OWASP Cheat Sheet Series**. [S. l.]: OWASP Foundation, [s. d.]. Disponível em: https://cheatsheetseries.owasp.org/. Acesso em: 8 nov. 2026.",
"OWASP FOUNDATION. **OWASP Top 10:2021**. [S. l.]: OWASP Foundation, 2021. Disponível em: https://owasp.org/Top10/2021/. Acesso em: 8 nov. 2026.",
"OWASP FOUNDATION. **OWASP Application Security Verification Standard**. Versão 5.0.0. [S. l.]: OWASP Foundation, 2025. Disponível em: https://github.com/OWASP/ASVS/releases/tag/v5.0.0. Acesso em: 8 nov. 2026.",
"OWASP JUICE SHOP. **OWASP Juice Shop**. Código-fonte e testes da versão v20.2.0. [S. l.]: OWASP, 2026. Disponível em: https://github.com/juice-shop/juice-shop/tree/v20.2.0. Acesso em: 8 nov. 2026.",
"SCANDARIATO, Riccardo; WUYTS, Kim; JOOSEN, Wouter. A descriptive study of Microsoft’s threat modeling technique. **Requirements Engineering**, v. 20, n. 2, p. 163-180, 2015. DOI 10.1007/s00766-013-0195-2. Disponível em: https://link.springer.com/article/10.1007/s00766-013-0195-2. Acesso em: 8 nov. 2026.",
"SHOSTACK, Adam. **Threat modeling: designing for security**. Indianapolis: Wiley, 2014. Disponível em: https://www.wiley.com/en-us/threat-modeling-designing-for-security-p-9781118809990. Acesso em: 8 nov. 2026.",
"SILVA, Diego Fonseca da et al. **Case prático 1: avaliação de vulnerabilidades em aplicação web**. Itajaí: Universidade do Vale do Itajaí, 2026. Relatório de disciplina, configuração e evidências do laboratório. Disponível em: https://github.com/diisilva/m1-seg-system-diegos. Acesso em: 8 nov. 2026.",
"SOUPPAYA, Murugiah; SCARFONE, Karen; DODSON, Donna. **Secure Software Development Framework (SSDF) version 1.1: recommendations for mitigating the risk of software vulnerabilities**. Gaithersburg: NIST, 2022. NIST SP 800-218. DOI 10.6028/NIST.SP.800-218. Disponível em: https://csrc.nist.gov/pubs/sp/800/218/final. Acesso em: 8 nov. 2026.",
"TUMA, Katja; ÇALIKLI, Gül; SCANDARIATO, Riccardo. Threat analysis of software systems: a systematic literature review. **Journal of Systems and Software**, v. 144, p. 275-294, 2018. DOI 10.1016/j.jss.2018.06.073. Disponível em: https://www.sciencedirect.com/science/article/pii/S0164121218301304. Acesso em: 8 nov. 2026.",
]
