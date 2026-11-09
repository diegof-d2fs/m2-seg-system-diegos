# Modelagem de Ameaças no OWASP Juice Shop — Trabalho 2

Trabalho 2 de **Segurança de Sistemas Computacionais** (UNIVALI, Escola Politécnica, Ciência da Computação, 2026/2). Modelagem de ameaças do **OWASP Juice Shop v20.2.0** com **DFD + STRIDE + DREAD**.

**Equipe:** Diego Fonseca da Silva · Leonardo Pacheco B Dias · Gustavo Gonçalves Trindade · João Victor Rodrigues Santos
**Professor:** Ramicés dos Santos Silva

## Apresentação (GitHub Pages)

- **Slides:** https://diegof-d2fs.github.io/m2-seg-system-diegos/

Deck estático em HTML + CSS + JavaScript puro (ES modules), **sem build, sem framework**, publicado direto pelo GitHub Pages (*Deploy from a branch*, sem GitHub Actions). Teclas: `←`/`→` navega, `S` abre o sumário, `F` tela cheia. Deep link por `#slide-N`. Validação das invariantes com `?check` no console.

## Conteúdo do repositório

| Caminho | O que é |
| --- | --- |
| `index.html` | Apresentação (slides) |
| `css/`, `js/`, `assets/` | Motor do deck (ver `SDD` original) e slides |
| `relatorio/M2_Relatorio_Final_diego_e_equipe.pdf` | **Relatório final** (PDF), com Apêndice B.5 de validação |
| `trabalho2/modelo/` | Arquivo-fonte do modelo: `DFD_Juice_Shop.drawio`, `modelo_ameacas.json`, SVGs, `priorizacao.csv` |
| `trabalho2/codigo/` | Scripts de validação, geração de diagramas e do relatório |
| `trabalho2/evidencias/` | Capturas e extratos HTTP (M1) |
| `trabalho2/evidencias_M2_validacao/` | Reprodução complementar em laboratório (08/11/2026) |
| `docs-fonte/` | Roteiro do trabalho (requisitos) |

Base do Trabalho 1: https://github.com/diisilva/m1-seg-system-diegos

## Rodar localmente

ES modules e `fetch` não funcionam via `file://`. Use um servidor estático na raiz:

```sh
python -m http.server 8000
# abra http://localhost:8000/
```

## Publicação (GitHub Pages)

Settings → Pages → Build and deployment → **Deploy from a branch** → Branch `main` / `(root)`.
O arquivo `.nojekyll` desliga o Jekyll para que os arquivos sejam servidos como estão. Cada `git push` republica em cerca de 1 minuto.
