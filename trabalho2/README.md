# Modelagem de ameaças no OWASP Juice Shop

Trabalho 2 de Segurança de Sistemas Computacionais, UNIVALI, 2026/2. O relatório editável é distribuído no arquivo M2_Relatorio_Final.docx. Esta pasta pode ser incluída como `trabalho2/` no repositório da M1.

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `modelo/DFD_Juice_Shop.drawio` | DFD de contexto, DFD de nível 1 e recortes FX1 a FX4. Abra o arquivo no diagrams.net ou na aplicação desktop. |
| `modelo/modelo_ameacas.json` | Fonte de dados do modelo, com nós, setas, fronteiras, fichas, matrizes, questionário e registro de ameaças. |
| `modelo/*.svg` | Figuras vetoriais dos seis diagramas. |
| `modelo/priorizacao.csv` | Ordenação dos cenários calculada com as notas DREAD do JSON. |
| `modelo/paginas.json` | Paginação da versão entregue, usada nos campos das listas e do sumário. |
| `evidencias/` | Recortes de capturas da M1 e metadados HTTP selecionados. |
| `codigo/` | Validação, geração dos diagramas, extração de evidências históricas e reconstrução do relatório. |

## Verificação e geração

Execute a partir desta pasta com Python 3.10 ou posterior. Validação, exportação de diagramas e extração de evidências usam apenas a biblioteca padrão.

```sh
python codigo/validar_modelo.py --csv modelo/priorizacao.csv
python codigo/gerar_diagramas.py
```

O JSON é a fonte de dados para gerar os diagramas. As edições visuais feitas diretamente no Draw.io permanecem no arquivo .drawio. A geração substitui o .drawio e os SVGs no diretório de saída indicado. Use `--saida` para gerar em outro diretório e preservar alterações visuais.

Para gerar o DOCX, instale a dependência de Python e deixe o comando `inkscape` disponível no PATH. O relatório usa o modelo, as evidências sanitizadas e o texto de `codigo/texto_relatorio.py`.

```sh
python -m pip install -r codigo/requirements.txt
python codigo/gerar_relatorio.py
```

Depois de editar o documento, atualize os campos de página no Word. No Windows, selecione o conteúdo com Ctrl+A e pressione F9. Se alterar notas, escopo ou classificações no JSON, revise também os totais e conclusões escritos no texto.

Para reconstruir o extrato histórico a partir de uma cópia local da M1, use o commit `ce48201e0fac66b81b7abd8e6face308306f9387`. O script lê os arquivos gravados e extrai apenas metadados selecionados.

```sh
python codigo/extrair_evidencias.py caminho/para/copia-da-m1
```

A leitura do código do Juice Shop foi feita na tag `v20.2.0`, commit `5658473cf8814459bf89000ce373b20ed0b4eb37`. As evidências distinguem ensaios da M1, leitura do código e casos de teste do projeto. A revisão cruzada entre os integrantes e as novas capturas de checkout e administração estão indicadas no relatório.

- https://github.com/diisilva/m1-seg-system-diegos
- https://github.com/juice-shop/juice-shop/tree/v20.2.0
