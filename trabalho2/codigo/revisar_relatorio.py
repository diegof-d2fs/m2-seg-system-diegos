"""Revisa o Word recebido e completa o template a partir do modelo validado.

Uso: python revisar_relatorio.py --entrada arquivo.docx --saida revisado.docx
O original não é sobrescrito. A paginação final deve ser conferida no Word/PDF.
"""
import argparse
from collections import Counter
from contextlib import nullcontext
from copy import deepcopy
import json
from pathlib import Path
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from gerar_relatorio import Report, font, FONT
from texto_relatorio import BIB, PLAN
from validar_modelo import ROOT, validate, media, risco, QUESTION_IDS


def clean(text):
    return re.sub(r'\s*\u2014\s*', ': ', str(text))


class CompactReport(Report):
    def p(self, text='', style='Normal'):
        return super().p(clean(text), style)

    def table(self, headers, rows, widths, **kwargs):
        t = super().table(headers, rows, widths, **kwargs)
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = row is t.rows[0]
                    p.paragraph_format.line_spacing = Pt(10.6)
                    for run in p.runs:
                        font(run, FONT, 9.5)
        return t

    def quadro(self, title, headers, rows, widths, **kwargs):
        return super().quadro(title, headers, rows, widths, **kwargs)

    def flow(self, n, fid, f):
        self.heading(f'6.{n} {fid}: {f["nome"]}', 2)
        self.paras(f['descricao'])
        self.quadro(f'Ficha e dados do {fid}', ('Campo', 'Descrição'), [
            ('Responsável / revisor previstos', f['responsavel_previsto']+' / '+f['revisor_previsto']),
            ('Ator e gatilho', f['ator_gatilho']), ('Pré-condições', f['precondicoes']),
            ('Resultado', f['resultado']),
            *[(r[0], r[1]+'; '+r[2]+'; propriedade crítica: '+r[3]+'.') for r in f['dados']],
            *[('Controle: '+r[1], r[0]+'. Base: '+r[2]) for r in f['controles']],
        ], (3.4, 12.6))
        self.picture(n+2, f'Recorte do DFD do {fid}', self.figs/(fid.lower()+'.png'), 'elaboração própria.', width=13.8)
        self.quadro(f'Requisições e base de observação do {fid}', ('Método e rota', 'Base e observação'),
            [(r[0], r[1]+'. '+re.sub(r'Figuras? [\d e]+ e extrato A\d\.', '', r[2])) for r in f['requisicoes']], (6,10))
        self.quadro(f'Transferências de dados do {fid}', ('F', 'Origem > destino', 'Dados', 'Protocolo / fronteira'),
            [(eid, self.edges[eid]['origem']+' > '+self.edges[eid]['destino'], self.edges[eid]['dados'],
              self.edges[eid]['protocolo']+'; '+(', '.join(self.edges[eid]['fronteiras']) or 'sem travessia')) for eid in f['arestas']],
            (1.1,2.7,7.5,4.7))
        self.quadro(f'Matriz STRIDE completa do {fid}', ('Elemento', 'S', 'T', 'R', 'I', 'D', 'E'),
            [(eid, *[', '.join(v.replace('T-'+fid+'-', '') if v.startswith('T-') else 'N/A '+v[2:] for v in row[c]) for c in 'STRIDE'])
             for eid,row in f['matriz'].items()], (2.2,2.3,2.3,2.3,2.3,2.3,2.3), compact=True)
        self.p(f'Na matriz, 01 significa T-{fid}-01, e assim sucessivamente. Célula vazia: categoria inaplicável ao tipo. Os códigos N/A remetem às justificativas após os quatro fluxos.', 'Fonte M2')
        self.p('Questionário do fluxo', 'Heading 3')
        for prefix in ['Q', *'STRIDE', 'V']:
            keys = [k for k in QUESTION_IDS if k.startswith(prefix)]
            label = {'Q':'Compreensão', 'S':'Falsificação de identidade', 'T':'Adulteração', 'R':'Repúdio',
                     'I':'Divulgação de informação', 'D':'Disponibilidade', 'E':'Elevação de privilégio', 'V':'Fechamento'}[prefix]
            p = self.p(label+'. '+' '.join(k+': '+f['questionario'][k] for k in keys), 'Questão M2')
            p.paragraph_format.first_line_indent = Pt(0)
        ts = [t for t in self.m['ameacas'] if t['fluxo']==fid]
        self.quadro(f'Registro de ameaças do {fid}, identificação',
            ('ID / elementos', 'Categoria / propriedade / classificação', 'Cenário e evidência'),
            [(t['id']+'\n'+', '.join(t['elementos']),
              t['stride']+' / '+t['propriedade']+'\nCWE-'+', CWE-'.join(t['cwe'])+' / '+t['owasp_top10_2021']+'\n'+status(t),
              t['cenario']+'\nBase: '+t['evidencia']) for t in ts], (2.8,3.5,9.7))
        self.quadro(f'Registro de ameaças do {fid}, tratamento',
            ('ID / DREAD / risco', 'Controle existente', 'Mitigação, camada, referência e aceite'),
            [(t['id']+'\n'+', '.join(map(str,t['notas']))+'\n'+score(t)+' / '+risco(t)+'\n'+t['decisao'],
              t['controle_existente'], t['mitigacao']+'\n'+t['tipo_camada']+'. ASVS 5.0.0: '+', '.join(t['asvs_5_0_0'])+
              '; guia '+t['cheat_sheet']+('; LGPD, art. 46.' if t['lgpd_art46'] else '.')+'\nAceite: '+t['criterio_aceite']) for t in ts], (2.8,3.5,9.7))
        self.p('Nas notas DREAD, a ordem é dano, reprodutibilidade, explorabilidade, usuários afetados e descoberta. As justificativas abaixo seguem essa ordem.', 'Fonte M2')
        self.quadro(f'Justificativas das notas do {fid}', ('ID', 'Justificativa de cada dimensão'),
            [(t['id'], ' '.join(label+' ('+str(note)+'): '+reason for label,note,reason in
              zip(['Dano','Reprodutibilidade','Explorabilidade','Usuários','Descoberta'],t['notas'],t['justificativas']))) for t in ts], (2.3,13.7))
        self.p('Conclusão e risco residual', 'Heading 3')
        self.paras(' '.join(f['conclusao']))


def score(t):
    return f'{media(t):.1f}'.replace('.', ',')


def status(t):
    if t['id']=='T-FX2-06':
        return 'Plausível na análise inicial; reproduzida na M2 (08/11/2026)'
    if t['id']=='T-FX4-04':
        return 'Plausível na análise inicial; reproduzida na M2 por HTTP'
    return t['status']+(f' ({t["evidencia"].split(".")[0]})' if t['status']=='Confirmada no T1' else '')


REWRITES = [
('Neste Trabalho 2 a perspectiva se inverte: o mesmo sistema é observado de dentro para fora, como na fase de projeto,', 'Neste Trabalho 2, a equipe analisa a estrutura do mesmo sistema sob a perspectiva de projeto,'),
('cumprem exatamente esse papel: orientam a análise para os pontos', 'orientam a análise dos pontos'),
('o que garante a rastreabilidade entre', 'o que permite rastrear as relações entre'),
('Todo fluxo que cruza uma fronteira merece atenção redobrada, porque é ali que um dado antes considerado confiável passa a ser suspeito, ou vice-versa.', 'Em cada fluxo que cruza uma fronteira, a análise deve verificar quais dados e permissões precisam ser validados pelo componente de destino.'),
('É sobre o nível 1 que os fluxos são recortados para a análise.', 'A análise dos fluxos utiliza recortes do DFD de nível 1.'),
('A terceira pergunta de Shostack exige mitigações concretas e verificáveis, e não recomendações vagas.', 'A terceira pergunta de Shostack orienta a definição de mitigações concretas e verificáveis.'),
('propõem justamente transformar', 'propõem transformar'),
('do roteiro, de forma objetiva.', 'do roteiro.'),
('impedir que o cadastro atribua papéis', 'definir o papel das novas contas no servidor'),
('limitar o material emitido na sessão', 'reduzir os dados incluídos no JWT'),
('Os critérios de aceite permitem conferir cada medida com contas de teste; a lição central da passagem da M1 para a M2 é que reconhecer a sessão não garante a titularidade do recurso.', 'Os critérios de aceite permitem verificar cada medida com contas de teste. A análise mostrou a necessidade de verificar a titularidade do recurso após a validação da sessão.'),
]


def set_text(p, value):
    if not p.runs:
        p.add_run(value)
    else:
        p.runs[0].text = value
        for r in p.runs[1:]:
            r.text = ''


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--entrada', type=Path, required=True)
    ap.add_argument('--saida', type=Path, required=True)
    args=ap.parse_args()
    if args.entrada.resolve()==args.saida.resolve():
        raise ValueError('Use um novo arquivo de saída.')
    d=Document(args.entrada)
    m=json.loads((ROOT/'modelo/modelo_ameacas.json').read_text(encoding='utf-8'))
    ranked=validate(m)
    compact_questions=ROOT/'codigo'/'questionario_conciso.json'
    if compact_questions.exists():
        concise=json.loads(compact_questions.read_text(encoding='utf-8'))
        for fid in m['fluxos']:
            assert set(concise[fid])==set(QUESTION_IDS)
            m['fluxos'][fid]['questionario']=concise[fid]
    nodes={x['id']:x for x in m['elementos']}
    orig_paras=list(d.paragraphs)
    body=d.element.body
    cap6=next(p._p for p in orig_paras if p.text=='6 ANÁLISE DOS FLUXOS')
    cap7=next(p._p for p in orig_paras if p.text=='7 VISÃO CONSOLIDADA')
    work=args.saida.resolve().parent/'.revisao_m2'/'figuras'
    work.mkdir(parents=True,exist_ok=True)
    with nullcontext(work) as tmp:
        figs=Path(tmp)
        for shape,name in zip(d.inline_shapes, ['dfd_nivel_0','dfd_nivel_1','fx1','fx2','fx3','fx4','m2_sqli','m2_admin']):
            rel=shape._inline.xpath('.//a:blip')[0].get(qn('r:embed'))
            (figs/(name+'.png')).write_bytes(d.part.related_parts[rel].blob)
        report=CompactReport(m,{},figs,{})
        existing_ids={s.style_id for s in d.styles}
        for style in report.doc.styles:
            if style.style_id not in existing_ids and style.name not in d.styles:
                d.styles.element.append(deepcopy(style.element))
        report.doc=d
        report.qn=8
        old_end=list(body)[-1]
        report.chapter(6,'ANÁLISE DOS FLUXOS',page=False)
        report.paras('Cada fluxo reúne ficha, transferências, classificação de dados, controles, matriz completa, respostas às 28 perguntas e registro de identificação e tratamento. As notas e justificativas seguem modelo_ameacas.json. A revisão documental final conferiu os quatro fluxos e conciliou os registros com o arquivo-fonte.')
        for n,(fid,f) in enumerate(m['fluxos'].items(),1):
            f=deepcopy(f)
            if fid=='FX2':
                f['precondicoes']='Para cadastro, e-mail válido e aplicação acessível. Para recuperação, conta e pergunta de segurança previamente associada.'
                f['questionario']['V1']='T-FX2-06 tem média 9,0 e permite criar conta privilegiada por um campo do cadastro. O cenário foi reproduzido na M2.'
                f['questionario']['V2']='T-FX2-01 e T-FX2-04 se apoiam em V7 da M1. T-FX2-06 foi reproduzida em 08/11/2026; as demais hipóteses aguardam ensaio.'
            report.flow(n,fid,f)
        report.heading('6.5 Justificativas de não aplicabilidade e guias',2)
        report.table(('Código','Justificativa'), [(k.replace('NA','N/A '),v) for k,v in m['justificativas_na'].items()], (2,14))
        report.p('Guias da OWASP citados no tratamento: '+ '; '.join(k+': '+v['titulo'] for k,v in m['cheat_sheets'].items())+'. Os endereços completos constam do arquivo-fonte e da série OWASP Cheat Sheets nas referências.', 'Fonte M2')
        generated=[]
        cur=cap6
        while cur is not cap7:
            nxt=cur.getnext(); body.remove(cur); cur=nxt
        # Conteúdo gerado foi inserido antes do sectPr final pelo python-docx.
        all_children=list(body)
        old_last_index=all_children.index(old_end)
        # O último parágrafo antigo é a última referência; ele ancora o bloco novo.
        old_reference=next(p._p for p in orig_paras if p.text.startswith('TUMA, Katja;'))
        cur=old_reference.getnext()
        while cur is not None and cur.tag!=qn('w:sectPr'):
            nxt=cur.getnext(); generated.append(cur); body.remove(cur); cur=nxt
        for el in generated:
            cap7.addprevious(el)

    # Atualizações editoriais e conciliação com a fonte única de pontuações.
    for p in d.paragraphs:
        text=p.text
        for a,b in REWRITES:
            text=text.replace(a,b)
        if text.startswith('Este trabalho modela ameaças'):
            text='Este trabalho analisa ameaças do OWASP Juice Shop sob a perspectiva de projeto. A aplicação é representada por diagramas de fluxo de dados, com fronteiras de confiança, e examinada com STRIDE por elemento. A análise abrange login e sessão, cadastro e recuperação de senha, cesta e pedido, administração e contabilidade. As ameaças são priorizadas por DREAD e associadas a controles verificáveis do OWASP ASVS, a tipos de fraqueza CWE e à proteção de dados pessoais. As evidências mostram falhas na consulta de autenticação, na composição do JWT e na autorização por objeto. A reexecução do laboratório também reproduziu a atribuição de papel privilegiado no cadastro. O resultado é um plano de mitigação com critérios de aceite para verificar os controles propostos.'
        if text.startswith('A análise foi documental,'):
            text='A análise combinou os documentos e os artefatos da M1, a inspeção do código e dos testes da tag v20.2.0 e a reexecução local de 08/11/2026. E, P, D, F e TB identificam entidades, processos, armazenamentos, transferências e fronteiras; T-FX<n>-<seq> identifica ameaças. Confirmada no T1 designa observação histórica; Plausível designa hipótese ainda sem reprodução. T-FX2-06 conserva o estado histórico no arquivo-fonte e recebe a indicação adicional de reprodução na M2. A média DREAD soma as cinco notas e divide por cinco: baixo até 3,9; médio de 4,0 a 6,9; alto a partir de 7,0. Empates seguem confirmação histórica, dano e ID. Cada nota é justificada, e cada tratamento informa controle, camada, referência, decisão e aceite. Os códigos V1 a V3 do questionário de fechamento são distintos dos achados V1 a V7 da M1.'
        if text.startswith('O capítulo responde às perguntas C1'):
            text+=' A fundamentação e a contextualização retomam a Etapa 1 em versão revisada, conforme a estrutura do roteiro.'
        if text.startswith('O OWASP Juice Shop é uma loja fictícia mantida'):
            text=text.replace('em rede bridge isolada','em rede bridge do laboratório')+' O host é Windows com Docker Desktop. O Compose usa HTTP, não declara volume nem fixa a sub-rede; o alcance pela bridge e as conexões de saída dependem da configuração da rede. Os pedidos e o estado de entrega ficam na coleção orders de MarsDB (D3); D1 conserva os demais dados relacionais.'
        if text.startswith('Entre as dependências relevantes'):
            text+=' Os dados examinados não abrangem as categorias de dados pessoais sensíveis do art. 5º, II da LGPD; credenciais continuam exigindo proteção específica.'
        if text.startswith('A ordenação agrega os 25 cenários'):
            text='A ordenação reúne os 25 cenários do arquivo-fonte: 18 de risco alto e sete de risco médio. Sete registros se apoiam em seis achados da M1; V5 sustenta a hipótese adicional sobre comprovantes. T-FX2-06, inicialmente plausível, foi reproduzida na M2. A injeção no login tem a maior média (9,8), seguida do papel privilegiado no cadastro (9,0). As médias e as justificativas do capítulo 6 e do ranking usam as mesmas cinco notas. Parametrizar a consulta de autenticação corrige a injeção. A autorização por função e por objeto deve ser aplicada no ponto em que cada recurso é lido ou alterado.'
        if text.startswith('Distribuição por categoria STRIDE:'):
            types=Counter(nodes[t['elementos'][0]]['tipo'] if t['elementos'][0] in nodes else 'Fluxo' for t in ranked)
            text='Cada ameaça é contada uma vez pela categoria e pelo primeiro elemento do registro. Information Disclosure reúne cinco cenários; cada outra categoria, quatro. Por tipo principal, são '+str(types['Processo'])+' processos, '+str(types['Armazenamento'])+' armazenamentos e '+str(types['Fluxo'])+' transferências de dados.'
        if text.startswith('A conferência comparou os pontos de entrada'):
            text='A conferência comparou as entradas dos diagramas com o código e com os pares HTTP da M1, que sustentam injeção no login, hash no JWT, leitura de cesta alheia, erro verboso, listagem em /ftp/, falhas sucessivas de autenticação e recuperação por resposta previsível. Em 8 de novembro de 2026, a equipe reimplantou a mesma imagem em 127.0.0.1:3000. Foram registrados login administrativo por injeção, hash no JWT sem o campo exp, cadastro com papel privilegiado, cesta de outro titular (200 com token; 401 sem token), listagem anônima de /ftp/ e cota de 100 no reset. O motor de desafios registrou Login Admin, Admin Registration, View Basket e Error Handling. A ausência de exp foi observada nos tokens; a aceitação temporal por cada rota ainda depende de ensaio.'
        if text.startswith('Limitações. A base de observação direta'):
            text='Limitações. As evidências históricas foram complementadas por verificações HTTP diretas em 08/11/2026. Foram executados testes de autenticação, cadastro, recuperação, autorização de cesta, listagem de arquivos e consulta de usuários com papéis distintos. Os resultados estão em REVISAO_HTTP_FINAL.json. Os ensaios usaram baixo volume e contas temporárias; não mediram esgotamento, concorrência ou validade temporal em todas as rotas. A revisão documental final está concluída. Os controles e riscos residuais descritos representam o tratamento proposto, cuja eficácia exige implantação.'
        if p.text!=text:
            set_text(p,text)
    # Inventário: os detalhes de todas as setas aparecem nas fichas do capítulo 6.
    inventory=next(t for t in d.tables if t.cell(0,0).text=='ID' and t.cell(0,1).text=='Tipo')
    for row in inventory.rows[1:]:
        if row.cells[0].text=='D1':
            row.cells[2].text=nodes['D1']['descricao']
    known={r.cells[0].text for r in inventory.rows[1:]}
    for eid in ['P0','E1','E2','E3','E4','D0','D3']:
        if eid not in known:
            r=inventory.add_row()
            for c,v in zip(r.cells,[eid,nodes[eid]['tipo'],nodes[eid]['descricao'],nodes[eid]['tecnologia']]):
                c.text=v
    # Reescreve o plano com IDs e critérios já documentados no modelo.
    plan=next(t for t in d.tables if t.cell(0,0).text=='Frente')
    for row,values in zip(plan.rows[1:],PLAN):
        num,title,ids,treatment,accept=values
        row.cells[0].text=num+': '+title+'\n'+ids
        row.cells[1].text=treatment+' Aceite: '+accept
    # Estado adicional sem reclassificar a confirmação histórica do modelo.
    for table in d.tables:
        for row in table.rows:
            if any('T-FX2-06 Papel privilegiado' in c.text or 'T-FX4-04 Consulta' in c.text for c in row.cells):
                row.cells[-1].text='Reproduzida na M2'
    for p in d.paragraphs:
        if '*reproduzida na M2' in p.text:
            set_text(p,'Fonte: elaboração própria. T1 indica confirmação histórica na M1; M2 indica reprodução complementar em 08/11/2026.')
    # Referências eletrônicas completas, mantendo as obras do texto de entrada.
    ref_heading=next(p for p in d.paragraphs if p.text=='REFERÊNCIAS')
    for p in list(d.paragraphs):
        if p.style.name=='Referência M2':
            p._p.getparent().remove(p._p)
    for ref in BIB:
        p=d.add_paragraph(re.sub(r'\*\*','',ref),style='Referência M2')
    # Fonte editável e trilha de reprodução em parágrafo anterior às referências.
    p=ref_heading.insert_paragraph_before('Arquivo-fonte do modelo e evidências: https://github.com/diegof-d2fs/m2-seg-system-diegos/tree/main/trabalho2. O modelo editável é trabalho2/modelo/DFD_Juice_Shop.drawio; as notas e justificativas estão em modelo_ameacas.json. A revisão estrutural foi executada com validar_modelo.py.',style='Fonte M2')
    # Sumário automático; o Word atualiza os números durante a exportação.
    sum_head=next(p._p for p in d.paragraphs if p.text=='SUMÁRIO')
    cap1=next(p._p for p in d.paragraphs if p.text=='1 INTRODUÇÃO' and p.style.name=='Heading 1')
    cur=sum_head.getnext()
    while cur is not cap1:
        nxt=cur.getnext(); body.remove(cur); cur=nxt
    p=OxmlElement('w:p'); r=OxmlElement('w:r'); begin=OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'),'begin'); r.append(begin); p.append(r)
    r=OxmlElement('w:r'); instr=OxmlElement('w:instrText'); instr.text=' TOC \\o "1-2" \\h \\z \\u '; r.append(instr); p.append(r)
    r=OxmlElement('w:r'); end=OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'),'end'); r.append(end); p.append(r); sum_head.addnext(p)
    # Padronização visual compacta, sem reduzir o corpo abaixo de 11 pontos.
    for name,size,line in [('Normal',11,13.2),('Questão M2',10,11.5),('Célula M2',9.5,10.6),('Fonte M2',9,10.2),('Referência M2',10,11.5)]:
        if name in d.styles:
            s=d.styles[name]; font(s,FONT,size); s.paragraph_format.line_spacing=Pt(line)
            s.paragraph_format.space_after=Pt(3 if name=='Normal' else 2)
    for table in d.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.style='Célula M2'; p.paragraph_format.line_spacing=Pt(10.6)
                    for run in p.runs:
                        font(run,FONT,9.5)
    for p in d.paragraphs:
        if p.style.name=='Normal':
            p.paragraph_format.line_spacing=Pt(13.2)
            p.paragraph_format.space_after=Pt(3)
            for run in p.runs:
                font(run,FONT,11)
    # Numeração de legendas por ordem de ocorrência, após a inclusão dos quadros.
    count=0
    for p in d.paragraphs:
        if re.match(r'^Quadro \d+ [:\-—]',p.text):
            count+=1; set_text(p,re.sub(r'^Quadro \d+ [:\-—]\s*',f'Quadro {count}: ',p.text))
        elif re.match(r'^Figura \d+ [:\-—]',p.text):
            set_text(p,re.sub(r'^(Figura \d+) [:\-—]\s*',r'\1: ',p.text))
    for part in d.part.package.parts:
        if hasattr(part,'element'):
            for el in part.element.iter(qn('w:t')):
                if el.text and '\u2014' in el.text:
                    el.text=clean(el.text)
    settings=d.settings.element
    update=settings.find(qn('w:updateFields'))
    if update is None:
        update=OxmlElement('w:updateFields'); settings.append(update)
    update.set(qn('w:val'),'true')
    d.save(args.saida)
    print(args.saida)
    print(f'{len(ranked)} ameaças, {sum(len(f["questionario"]) for f in m["fluxos"].values())} respostas, {count} quadros.')


if __name__=='__main__':
    main()
