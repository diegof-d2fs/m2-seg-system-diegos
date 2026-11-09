# Validação complementar em laboratório — Trabalho 2 (M2)

**Data:** 08/11/2026
**Alvo:** OWASP Juice Shop `bkimminich/juice-shop:v20.2.0`
**Digest:** `sha256:8739101ade29358abb5469ee66ae78e582c97ed0a5543a4ad102e5fa5193526b`
**Implantação:** mesmo `docker-compose.yml` da M1, publicado em `127.0.0.1:3000` (loopback), UID 65532.
**Escopo/conduta:** execução apenas na instância local autorizada; credenciais omitidas; nenhum sistema de terceiros envolvido.

## Cenários reproduzidos ao vivo

| Cenário | Requisição | Resultado observado |
|---|---|---|
| Injeção SQL no login (T-FX1-02, M1 V1) | `POST /rest/user/login` com e-mail `' OR 1=1--` | HTTP 200; token de sessão com papel **admin** (id 1, admin@juice-sh.op). JWT inclui o campo `password` (hash MD5 `0192023a...`) e **não** traz `exp`. |
| Hash de senha no JWT (T-FX1-04, M1 V2) | idem (inspeção do payload do JWT) | `data.password` presente no token; algoritmo RS256; claims `data, bid, iat`, sem `exp`. |
| Papel privilegiado no cadastro (T-FX2-06) | `POST /api/Users` com `role: admin` | HTTP 201; conta criada **já com papel admin** (mass assignment). Antes classificado como *plausível* — agora reproduzido. |
| Leitura de cesta de outro titular (T-FX3-06, M1 V3) | `GET /rest/basket/{id}` de outra conta com JWT válido | HTTP 200 com a cesta de outro titular; sem token, a mesma rota retorna HTTP 401. |
| Pergunta de segurança por e-mail (T-FX2-04) | `GET /rest/user/security-question?email=...` | HTTP 200; pergunta retornada a partir do e-mail. |
| Cota do reset de senha (T-FX2-01, M1 V7) | `POST /rest/user/reset-password` | HTTP 401; cabeçalho `X-RateLimit-Limit: 100`. |
| Listagem de diretório (apoio ao FX3, M1 V5) | `GET /ftp/` | HTTP 200; listagem anônima do diretório. Acesso direto a arquivo `.bak` retorna HTTP 403. |

Durante a sessão em navegador, o próprio motor de desafios da aplicação registrou como resolvidos
**Login Admin**, **Admin Registration**, **View Basket** e **Error Handling**, corroborando T-FX1-02,
T-FX2-06, T-FX3-06 e T-FX3-04 (ver `fig_m2_sqli.png`).

## Verificação de referências

As referências acadêmicas foram conferidas (título, autoria, veículo, páginas e DOI):
- Alves et al. (2024) — ERES/SBC, p. 218-227, DOI 10.5753/eres.2024.4319 — **confere**.
- Carneiro, Kudo, Bulcão Neto (2024) — CIBSE/SBC, p. 348-355, DOI 10.5753/cibse.2024.28460 — **confere**.
- Manadhata & Wing (2011), Tuma et al. (2018), Scandariato et al. (2015), Shostack (2014),
  Hernan et al. (2006), Meier et al. (2003), NIST SP 800-30 e SP 800-218 — obras canônicas, corretas.

Nenhuma referência inventada foi encontrada.

## Observação de implantação

A sub-rede da bridge na reexecução foi `172.24.0.0/16` (o relatório cita `172.19.0.0/16` como registro
histórico da M1; coerente, pois o Compose não fixa a sub-rede).

## Arquivos

- `fig_m2_sqli.png` — sessão de administrador via injeção SQL e desafios reconhecidos.
- `fig_m2_ftp.png` — listagem anônima do diretório `/ftp/`.

Estas imagens foram incorporadas ao relatório final (`relatorio/M2_Relatorio_Final_diego_e_equipe.pdf`, Apêndice B.5, Figuras 12 e 13).
Para incluir no repositório, podem ser copiadas para `trabalho2/evidencias/`.
