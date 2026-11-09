"""Reconstrói o relatório Word editável a partir dos textos, modelo e figuras."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from texto_relatorio import (RESUMO, INTRO, THEORY, STRIDE_ROWS, CONTEXT, ACTORS,
    ASSETS, SURFACE, DEPS, CANDIDATES, METHOD, ANCHORS, MODEL_CONTEXT,
    MODEL_DETAIL, MODEL_BOUNDARIES, PLAN, CONSOLIDATED, VALIDATION, CONCLUSION, BIB)
from validar_modelo import ROOT, by_id, media, risco, validate

FONT = "Times New Roman"
AUTHORS = ["Diego Fonseca da Silva","Leonardo Pacheco B Dias",
           "Gustavo Gonçalves Trindade","João Victor Rodrigues Santos"]
M1_URL = "https://github.com/diisilva/m1-seg-system-diegos"
JS_URL = "https://github.com/juice-shop/juice-shop"
GROUPS = [
    ("Compreensão do fluxo","Q",7),("Spoofing","S",3),("Tampering","T",3),
    ("Repudiation","R",3),("Information Disclosure","I",3),("Denial of Service","D",3),
    ("Elevation of Privilege","E",3),("Fechamento do fluxo","V",3),
]
DREAD = ("Dano","Reprodutibilidade","Explorabilidade","Usuários afetados","Descoberta")
DREAD_SHORT = ("D","R","E","A","D")
WIDTH = 16

def xml(tag, **attrs):
    el = OxmlElement(tag)
    for key,value in attrs.items():
        el.set(qn("w:"+key),str(value))
    return el

def font(obj, name, size=None, bold=None):
    obj.font.name = name
    obj.font.color.rgb = RGBColor.from_string("000000")
    if size is not None:
        obj.font.size = Pt(size)
    if bold is not None:
        obj.font.bold = bold
    rpr=obj._element.get_or_add_rPr()
    rfonts=rpr.find(qn("w:rFonts"))
    for attr in ("asciiTheme","hAnsiTheme","eastAsiaTheme","cstheme"):
        rfonts.attrib.pop(qn("w:"+attr), None)
    for attr in ("ascii","hAnsi","eastAsia","cs"):
        rfonts.set(qn("w:"+attr),name)
    if rpr.find(qn("w:lang")) is None:
        rpr.append(xml("w:lang",val="pt-BR"))

def runs(p, content, *, bold=False):
    for piece in re.split(r"(\*\*[^*]+\*\*|et al\.|In:|\[S\. l\.\])",str(content)):
        if not piece:
            continue
        r=p.add_run(piece[2:-2] if piece.startswith("**") else piece)
        if bold or piece.startswith("**"):
            r.bold=True
        if piece in ("et al.","In:","[S. l.]"):
            r.italic=True

def field(p, instr, cached):
    b=p.add_run()._r
    b.append(xml("w:fldChar",fldCharType="begin"))
    it=xml("w:instrText")
    it.set("{http://www.w3.org/XML/1998/namespace}space","preserve")
    it.text=" "+instr+" "
    b.append(it)
    b.append(xml("w:fldChar",fldCharType="separate"))
    p.add_run(str(cached))
    p.add_run()._r.append(xml("w:fldChar",fldCharType="end"))

class Report:
    def __init__(self, model, extract, figs, pages):
        self.m=model
        self.ranked=validate(model)
        self.nodes=by_id(model["elementos"])
        self.edges=by_id(model["arestas"])
        self.extract=extract
        self.figs=figs
        self.pages=pages
        self.doc=Document()
        self.doc.core_properties.title="Modelagem de ameaças no OWASP Juice Shop"
        self.doc.core_properties.author="; ".join(AUTHORS)
        self.doc.core_properties.subject="Segurança de Sistemas Computacionais | UNIVALI"
        self.doc.core_properties.keywords="DFD, STRIDE, DREAD, OWASP Juice Shop"
        self.quadros=[]
        self.figures=[]
        self.toc=[]
        self.qn=0
        self.bn=0
        self.set_styles()
        self.section_geometry(self.doc.sections[0])

    def section_geometry(self,s):
        s.page_width=Cm(21)
        s.page_height=Cm(29.7)
        s.left_margin=Cm(3)
        s.right_margin=Cm(2)
        s.top_margin=Cm(3)
        s.bottom_margin=Cm(2)
        s.header_distance=Cm(1.9)
        s.footer_distance=Cm(1.1)

    def style(self,name,size,align,space,line,indent=0,base="Normal",bold=False):
        styles=self.doc.styles
        s=styles[name] if name in styles else styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
        if name!="Normal":
            s.base_style=styles[base]
        font(s,FONT,size,bold)
        p=s.paragraph_format
        p.alignment=align
        p.space_before=Pt(space[0])
        p.space_after=Pt(space[1])
        p.line_spacing=Pt(line)
        p.first_line_indent=Cm(indent)
        p.widow_control=True
        return s

    def set_styles(self):
        a=WD_ALIGN_PARAGRAPH
        self.style("Normal",12,a.JUSTIFY,(0,0),20.7,1.25)
        self.style("Heading 1",16,a.LEFT,(0,12),19,bold=True)
        self.style("Heading 2",14,a.LEFT,(17,8),16.2,bold=True)
        self.style("Heading 3",12,a.LEFT,(12,4),14.4,bold=True)
        self.style("Heading 4",11,a.LEFT,(8,3),13,bold=True)
        self.style("Título central",16,a.CENTER,(0,18),19,bold=True)
        title = self.style("Title",14,a.CENTER,(0,0),16.1,bold=True)
        pr = title._element.get_or_add_pPr()
        for border in pr.findall(qn("w:pBdr")):
            pr.remove(border)
        self.style("Capa",14,a.CENTER,(0,0),16.1)
        self.style("Legenda M2",11,a.LEFT,(6,4),13)
        self.style("Fonte M2",10,a.LEFT,(3,7),11.5)
        self.style("Célula M2",10.5,a.LEFT,(0,0),12.1)
        self.style("Índice M2",11,a.LEFT,(0,0),12.15)
        self.style("Referência M2",12,a.LEFT,(0,12),13.8)
        self.style("Questão M2",12,a.JUSTIFY,(0,3),20.7,1.25)
        self.style("Justificativa M2",11,a.LEFT,(0,2),14)
        self.style("Código M2",9.5,a.LEFT,(0,0),12)
        font(self.doc.styles["Código M2"],"Courier New",9.5)
        for name in ("Heading 1","Heading 2","Heading 3","Heading 4","Legenda M2"):
            self.doc.styles[name].paragraph_format.keep_with_next=True
            self.doc.styles[name].paragraph_format.keep_together=True
        self.doc.styles["Índice M2"].paragraph_format.tab_stops.add_tab_stop(
            Cm(15.92),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
        for name in ("Normal","Capa","Célula M2","Justificativa M2","Fonte M2","Referência M2"):
            self.doc.styles[name].paragraph_format.keep_with_next=False

    def bookmark(self,p,key):
        self.bn+=1
        p._p.insert(1 if p._p.pPr is not None else 0,xml("w:bookmarkStart",id=self.bn,name=key))
        p._p.append(xml("w:bookmarkEnd",id=self.bn))

    def p(self,text,style="Normal"):
        p=self.doc.add_paragraph(style=style)
        runs(p,text)
        return p

    def paras(self, text):
        for p in re.split(r"\n\s*\n",text.strip()):
            if p:
                self.p(" ".join(p.split()))

    def heading(self,text,level=1,*,key=None,listed=False,page=False,center=False):
        p=self.p(text, "Título central" if center else f"Heading {level}")
        p.paragraph_format.page_break_before=page
        if key:
            self.bookmark(p,key)
        if listed:
            self.toc.append((key,text,level))
        return p

    def front(self):
        p=self.p("UNIVERSIDADE DO VALE DO ITAJAÍ\nESCOLA POLITÉCNICA\nCURSO DE CIÊNCIA DA COMPUTAÇÃO","Capa")
        p.runs[0].bold=True
        p.paragraph_format.space_after=Pt(17)
        p=self.p("Segurança de Sistemas Computacionais","Capa")
        p.paragraph_format.space_after=Pt(65)
        p=self.p("\n".join(AUTHORS),"Capa")
        p.paragraph_format.space_after=Pt(80)
        p=self.p("MODELAGEM DE AMEAÇAS NO OWASP JUICE SHOP","Title")
        p.paragraph_format.space_after=Pt(12)
        p=self.p("TRABALHO 2","Capa")
        p.paragraph_format.space_after=Pt(8)
        p=self.p("Relatório final de modelagem com DFD e STRIDE","Capa")
        p.paragraph_format.space_after=Pt(88)
        p=self.p("Professor Ramicés dos Santos Silva","Capa")
        p.paragraph_format.space_after=Pt(96)
        p=self.p("Itajaí (SC)","Capa")
        p.paragraph_format.space_after=Pt(8)
        self.p("Novembro de 2026","Capa")

        self.heading("RESUMO",page=True,center=True)
        p=self.p(RESUMO.strip())
        p.paragraph_format.first_line_indent=Pt(0)
        p=self.p("**Palavras-chave**  modelagem de ameaças. DFD. STRIDE. DREAD. OWASP Juice Shop.")
        p.paragraph_format.first_line_indent=Pt(0)
        p.paragraph_format.space_before=Pt(11)

        self.heading("QUADRO DE PARTICIPAÇÃO",page=True,center=True)
        items = [
            (AUTHORS[0],"FX1","Fundamentação teórica, implantação, atores, ativos e pontos de entrada (C3 a C6)."),
            (AUTHORS[1],"FX2","Inventário e justificativa dos fluxos candidatos (C8)."),
            (AUTHORS[2],"FX3","Dependências, premissas, relação com a M1 e revisão de C6 e C8."),
            (AUTHORS[3],"FX4","Identificação, arquitetura e fundamentação do DFD inicial (C1 e C2)."),
        ]
        self.table(("Integrante","Fluxo proposto","Contribuição documentada na fundamentação"),items,(4.4,2.4,9.2))
        self.paras("A distribuição dos fluxos para a revisão final segue a proposta do Quadro de Participação. As contribuições anteriores foram mantidas conforme o registro da pesquisa inicial. A confirmação da atribuição final e da revisão cruzada cabe à equipe.")

        self.anchors={}
        for key,title in (("figures","LISTA DE FIGURAS"),("quadros","LISTA DE QUADROS"),("toc","SUMÁRIO")):
            self.heading(title,page=True,center=True)
            self.anchors[key]=self.p("",style="Índice M2")
        s=self.doc.add_section(WD_SECTION_START.NEW_PAGE)
        self.section_geometry(s)
        s.header.is_linked_to_previous=False
        p=s.header.paragraphs[0]
        p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.first_line_indent=Pt(0)
        p.paragraph_format.line_spacing=Pt(12)
        field(p,"PAGE",self.pages.get("cap1",7))
        for r in p.runs:
            font(r,FONT,10)

    def index(self):
        for name, entries in (("figures",self.figures),("quadros",self.quadros),("toc",self.toc)):
            anchor=self.anchors[name]
            for key,label,level in entries:
                p=anchor.insert_paragraph_before(style="Índice M2")
                if level>1:
                    p.paragraph_format.left_indent=Cm(.65)
                runs(p,label)
                p.add_run("\t")
                field(p,f"PAGEREF {key} \\h",self.pages.get(key,""))
            anchor._p.getparent().remove(anchor._p)
        settings=self.doc.settings.element
        settings.append(xml("w:updateFields",val="true"))

    def table(self,headers,rows,widths,*,center=(),compact=False,source=None):
        t=self.doc.add_table(rows=1,cols=len(headers))
        t.alignment=WD_TABLE_ALIGNMENT.CENTER
        t.autofit=False
        for col,w in zip(t.columns,widths):
            col.width=Cm(w*WIDTH/sum(widths))
        pr=t._tbl.tblPr
        borders=xml("w:tblBorders")
        for side in ("top","left","bottom","right","insideH","insideV"):
            borders.append(xml("w:"+side,val="single",sz="8",color="777777"))
        pr.append(borders)
        pad=xml("w:tblCellMar")
        for side, val in (("top",58 if compact else 83),("bottom",58 if compact else 83),
                          ("left",39 if compact else 78),("right",39 if compact else 78)):
            pad.append(xml("w:"+side,w=val,type="dxa"))
        pr.append(pad)
        rows=list(rows)
        for i,vals in enumerate([headers]+rows):
            row=t.rows[0] if i==0 else t.add_row()
            trpr=row._tr.get_or_add_trPr()
            trpr.append(xml("w:cantSplit"))
            if i==0:
                trpr.append(xml("w:tblHeader",val="1"))
            for j,(c,v,w) in enumerate(zip(row.cells,vals,widths)):
                c.width=Cm(w*WIDTH/sum(widths))
                c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                p=c.paragraphs[0]
                p.style="Célula M2"
                p.paragraph_format.keep_with_next=i==0 or (bool(source) and i==len(rows))
                if j in center:
                    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                if i==0:
                    c._tc.get_or_add_tcPr().append(xml("w:shd",fill="E7E6E6"))
                runs(p,v,bold=i==0)
        if source:
            self.p("Fonte: "+source,"Fonte M2")
        return t

    def quadro(self,title,headers,rows,widths,*,source="elaboração própria.",**kwargs):
        self.qn+=1
        key=f"qua{self.qn}"
        label=f"Quadro {self.qn} - {title}"
        p=self.p(label,"Legenda M2")
        self.bookmark(p,key)
        self.quadros.append((key,label,1))
        self.table(headers,rows,widths,source=source,**kwargs)
        return self.qn

    def picture(self,n,title,path,source,width=WIDTH):
        key=f"fig{n}"
        label=f"Figura {n} - {title}"
        p=self.p(label,"Legenda M2")
        self.bookmark(p,key)
        self.figures.append((key,label,1))
        p=self.doc.add_paragraph(style="Fonte M2")
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing=1.0
        p.paragraph_format.space_before=Pt(0)
        p.paragraph_format.space_after=Pt(1)
        p.paragraph_format.keep_with_next=True
        p.add_run().add_picture(str(path),width=Cm(width))
        p._p.xpath(".//wp:docPr")[0].set("descr",title)
        self.p("Fonte: "+source,"Fonte M2")

    def chapter(self,num,title,*,page=True):
        return self.heading(f"{num} {title}",key=f"cap{num}",listed=True,page=page)

    def chapters_1_to_4(self):
        self.chapter(1,"INTRODUÇÃO",page=False)
        self.paras(INTRO)
        self.chapter(2,"FUNDAMENTAÇÃO TEÓRICA")
        for i,(head,text) in enumerate(THEORY):
            self.heading(head,2)
            self.paras(text)
            if i==2:
                self.quadro("Categorias STRIDE e propriedades de segurança",
                    ("Categoria","Significado","Propriedade"),STRIDE_ROWS,(4.6,7.1,4.3),
                    source="adaptado de Hernan et al. (2006).")
        self.chapter(3,"CONTEXTUALIZAÇÃO DO AMBIENTE")
        data = {
            4:("Atores e permissões esperadas",("Ator ou papel","Funções e limites"),ACTORS,(4.5,11.5),"OWASP Juice Shop (2026) e Silva et al. (2026)."),
            5:("Ativos e classificação de dados",("Conjunto de dados","Conteúdo","Classificação"),ASSETS,(3.4,6.3,6.3),"Brasil (2018), OWASP Juice Shop (2026) e Silva et al. (2026)."),
            6:("Superfície de ataque por categoria",("Categoria","Entradas e evidência"),SURFACE,(4,12),"OWASP Juice Shop (2026) e Silva et al. (2026)."),
            7:("Dependências e funções de segurança",("Componente","Versão declarada","Relevância"),DEPS,(4.15,3.45,8.4),"manifests da tag v20.2.0, em OWASP Juice Shop (2026)."),
            8:("Fluxos candidatos e critérios de seleção",("ID","Funcionalidade","Seleção","Justificativa"),CANDIDATES,(1.25,4.1,2.15,8.5),"OWASP Juice Shop (2026) e Silva et al. (2026)."),
        }
        for i,(head,content) in enumerate(CONTEXT,1):
            self.heading(head,2)
            self.paras(content)
            if i==1:
                self.p(self.m["digest_m1"],"Código M2")
            if i in data:
                title,headers,rows,widths,source=data[i]
                self.quadro(title,headers,rows,widths,source=source)
            if i==10:
                self.quadro("Rastreabilidade dos achados da M1",
                    ("ID","OWASP e CVSS 3.1","Efeito observado","Localização e registro na M2"),
                    [(x["id"],x["owasp"]+" / "+x["cvss"],x["achado"],x["localizacao"]+". "+x["relacao"]) for x in self.m["evidencias_m1"]],
                    (1.2,2.65,6,6.15),source="Silva et al. (2026) e elaboração própria.")
        self.chapter(4,"METODOLOGIA",page=False)
        for i,(head,content) in enumerate(METHOD,1):
            self.heading(head,2)
            self.paras(content)
            if i==3:
                self.quadro("Âncoras para atribuição das notas DREAD",
                    ("Dimensão","1 a 3","4 a 6","7 a 10"),ANCHORS,(3.2,4.25,4.25,4.3),
                    source="elaboração própria, com base em Meier et al. (2003) e no roteiro da disciplina.")

    def chapter_5(self):
        self.chapter(5,"MODELO DO SISTEMA")
        self.heading("5.1 DFD DE CONTEXTO",2)
        self.paras(MODEL_CONTEXT)
        self.picture(1,"DFD de contexto do OWASP Juice Shop",self.figs/"dfd_nivel_0.png","elaboração própria.")
        self.heading("5.2 DFD DE NÍVEL 1",2,page=True)
        self.paras(MODEL_DETAIL)
        self.picture(2,"DFD detalhado e fronteiras de confiança",self.figs/"dfd_nivel_1.png","elaboração própria.")
        self.heading("5.3 INVENTÁRIO DE ELEMENTOS E FRONTEIRAS",2)
        self.quadro("Inventário dos elementos do DFD",
            ("ID","Tipo","Responsabilidade","Tecnologia"),
            [(e["id"],e["tipo"],e["nome"]+". "+e["descricao"],e["tecnologia"]) for e in self.m["elementos"]],
            (1,3,7.5,4.5),source="OWASP Juice Shop (2026) e elaboração própria.")
        self.paras(MODEL_BOUNDARIES)
        self.quadro("Fronteiras de confiança",
            ("ID","Lados da fronteira","Mudança de confiança","Transferências"),
            [(x["id"],x["separa"],x["interpretacao"],x["fluxos"]) for x in self.m["fronteiras"]],
            (1.55,3.6,6.45,4.4))
        self.heading("5.4 SUPERFÍCIE DE ATAQUE DO MODELO",2)
        self.paras("O Quadro 4 reúne pontos de entrada do laboratório. No modelo, P2 e P3 recebem entradas públicas de identidade, P4 opera dados vinculados a cliente, P5 concentra funções privilegiadas e P6 dá acesso a arquivos. O Quadro 11 associa as entradas a processos e setas. O Quadro 10 indica as fronteiras correspondentes. Cada ficha de fluxo detalha as setas, os dados e os formatos empregados.")
        self.quadro("Entradas do recorte e elementos afetados",("Canal","Processos e setas","Dados controlados"),
            [("Identidade e recuperação","P2 e P3. F09 a F12.","Senha, e-mail, token, pergunta, ID e papel no cadastro."),
             ("Compra e consulta","P4. F13 e F14.","JWT, IDs, quantidade, endereço, cartão sintético e campos de pedido."),
             ("Administração e contabilidade","P5. F15 e F16.","JWT, identificadores, comandos de moderação e status de entrega."),
             ("Arquivos HTTP","P6. F17 e F18.","Nome de documento, listagem e resposta com bytes do arquivo.")],(4,4,8))

    def flow_section(self,num,fid,f):
        self.heading(f"6.{num} {fid} {f['nome'].upper()}",2,key=f"fx{num}",listed=True)
        self.paras(f["descricao"])
        self.heading(f"6.{num}.1 Ficha do fluxo",3)
        self.quadro(f"Identificação e condições do {fid}",("Campo","Descrição"),
            [("ID e função",fid+" / "+f["nome"]),
             ("Responsável e revisor propostos",f["responsavel_previsto"]+" / "+f["revisor_previsto"]),
             ("Ator e gatilho",f["ator_gatilho"]),
             ("Pré-condições",f["precondicoes"]),("Resultado esperado",f["resultado"])],(4.1,11.9))
        self.picture(num+2,f"Recorte do DFD do {fid}",self.figs/(fid.lower()+".png"),"elaboração própria.")
        self.quadro(f"Requisições e evidências do {fid}",("Método e rota","Base","Observação"),
            f["requisicoes"],(5.2,3.6,7.2),
            source="OWASP Juice Shop (2026), Silva et al. (2026) e elaboração própria.")
        rows=[]
        for i,edge in enumerate(f["arestas"],1):
            e=self.edges[edge]
            rows.append((i,e["origem"],e["destino"],edge,e["dados"],e["protocolo"],
                         "\n".join(e["fronteiras"]) if e["fronteiras"] else "Sem travessia"))
        self.quadro(f"Elementos percorridos no {fid}",
            ("Nº","De","Para","Seta","Dados trafegados","Protocolo e formato","Fronteira"),
            rows,(.75,1.35,1.45,1.25,5.25,3.4,2.55),center=(0,1,2,3,6))
        self.quadro(f"Classificação dos dados no {fid}",("Dado","Classificação","Localização","CID crítica"),
                    f["dados"],(4.1,4.4,5,2.5),source="Brasil (2018), OWASP Juice Shop (2026) e elaboração própria.")
        self.quadro(f"Controles identificados no {fid}",("Controle","Elemento","Base de constatação"),
                    f["controles"],(6,2.8,7.2),source="OWASP Juice Shop (2026) e Silva et al. (2026).")
        self.heading(f"6.{num}.2 Matriz STRIDE por elemento",3)
        self.paras(f"Os códigos NA1 a NA13 remetem às justificativas do Apêndice A. Cada célula preenchida vincula uma ameaça do {fid} ou registra N/A para a categoria aplicável ao tipo. O detalhamento das setas consta do quadro de percurso.")
        rows=[]
        for key,row in f["matriz"].items():
            name=key+" "+self.nodes[key]["nome"] if key in self.nodes else key
            items=["\n".join(("N/A "+v[2:] if v.startswith("NA") else v) for v in row[c])
                   for c in "STRIDE"]
            rows.append((name,*items))
        self.quadro(f"Matriz STRIDE do {fid}",("Elemento","S","T","R","I","D","E"),rows,
                    (3.3,2.1,2.1,2.1,2.1,2.1,2.1),center=(1,2,3,4,5,6),compact=True)
        self.heading(f"6.{num}.3 Questionário do fluxo",3)
        for head,cat,n in GROUPS:
            self.heading(head,4)
            for i in range(1,n+1):
                key=f"{cat}{i}"
                self.p(f"**{key}**  {f['questionario'][key]}","Questão M2")
        self.heading(f"6.{num}.4 Registro de ameaças",3)
        items=[t for t in self.m["ameacas"] if t["fluxo"]==fid]
        def status(t):
            return t["status"]+(f" ({t['evidencia'].split('.')[0]})" if t["status"]=="Confirmada no T1" else "")
        def tags(t):
            return ", ".join("CWE-"+x for x in t["cwe"])+"\n"+t["owasp_top10_2021"]
        self.quadro(f"Parte A do {fid}  Identificação das ameaças",
            ("ID e elementos principais","STRIDE e propriedade","Cenário","CWE e OWASP 2021","Status"),
            [(t["id"]+"\n"+", ".join(t["elementos"][:3]),
              t["stride"]+" / "+t["propriedade"],t["cenario"],tags(t),status(t)) for t in items],
            (2.4,2.75,6.85,2.05,1.95))
        self.p("D, R, E, A e D indicam dano, reprodutibilidade, explorabilidade, usuários afetados e descoberta. Os números de controle pertencem ao ASVS 5.0.0. Os códigos de guias da OWASP remetem ao Apêndice A.")
        def treatment(t):
            refs=", ".join(t["asvs_5_0_0"])
            return (t["mitigacao"]+"\n"+t["tipo_camada"]+". ASVS "+refs
                    +". Guia "+t["cheat_sheet"]+(". LGPD, art. 46." if t["lgpd_art46"] else "."))
        self.quadro(f"Parte B do {fid}  Priorização e tratamento",
            ("ID","Controle existente",*DREAD_SHORT,"Média","Mitigação, camada e referências","Decisão"),
            [(t["id"],t["controle_existente"],*t["notas"],self.score(t)+"\n"+risco(t),
              treatment(t),t["decisao"]) for t in items],
            (1.65,2.68,.54,.54,.54,.54,.54,1.18,6.31,1.48),center=(2,3,4,5,6,7,9),compact=True)
        self.heading(f"6.{num}.5 Justificativas e critérios de aceite",3)
        for t in items:
            self.heading(t["id"]+"  "+t["titulo"],4)
            p=self.p("**Evidência**  "+t["evidencia"],"Justificativa M2")
            p.paragraph_format.keep_with_next=True
            for dim,note,reason in zip(DREAD,t["notas"],t["justificativas"]):
                p=self.p(f"**{dim} ({note})**  {reason}","Justificativa M2")
                p.paragraph_format.keep_with_next=True
            self.p("**Aceite**  "+t["criterio_aceite"],"Justificativa M2")
        self.heading(f"6.{num}.6 Conclusão do fluxo",3)
        for p in f["conclusao"]:
            self.paras(p)

    @staticmethod
    def score(t):
        return f"{media(t):.1f}".replace(".",",")

    def chapter_7(self):
        self.chapter(7,"VISÃO CONSOLIDADA",page=False)
        self.heading("7.1 DEZ AMEAÇAS PRIORITÁRIAS",2)
        self.paras(CONSOLIDATED)
        self.quadro("Top 10 por média DREAD e ordem de tratamento",
            ("Nº","ID","Cenário e elemento principal","DREAD","Status","Frente do plano"),
            [(i,t["id"],t["titulo"]+" ("+t["elementos"][0]+")",self.score(t),
              "T1 "+t["evidencia"].split(".")[0] if t["status"]=="Confirmada no T1" else "Plausível",
              str(next((row[0] for row in PLAN if t["id"] in self.plan_ids(row[2])),"6")))
             for i,t in enumerate(self.ranked[:10],1)],
            (1.25,1.85,6.15,1.65,2.35,2.75),center=(0,3,5))
        self.heading("7.2 DISTRIBUIÇÃO POR CATEGORIA E ELEMENTO",2)
        self.paras("Cada cenário é contado uma vez por categoria principal e uma vez pelo primeiro elemento do registro. Um cenário que aparece em várias células da matriz continua sendo um único registro. A distribuição não mede a severidade de um tipo de elemento por quantidade.")
        counts=Counter((t["fluxo"],t["stride"]) for t in self.ranked)
        self.quadro("Distribuição STRIDE por fluxo",("Fluxo","S","T","R","I","D","E","Total"),
            [(fid,*(counts[fid,k] for k in "STRIDE"),sum(counts[fid,k] for k in "STRIDE")) for fid in self.m["fluxos"]]
            +[("Total",*(sum(counts[f,k] for f in self.m["fluxos"]) for k in "STRIDE"),len(self.ranked))],
            (2.5,1.8,1.8,1.8,1.8,1.8,1.8,2.7),center=range(1,8))
        prim=Counter(t["elementos"][0] for t in self.ranked)
        self.quadro("Distribuição por elemento principal do DFD",("Elemento","Tipo","Ameaças"),
            [(key+" / "+(self.nodes[key]["nome"] if key in self.nodes else self.edges[key]["dados"]),
              self.nodes[key]["tipo"] if key in self.nodes else "Fluxo",n)
             for key,n in sorted(prim.items(),key=lambda item:(-item[1],item[0]))],
            (10,3.8,2.2),center=(2,))
        totals=Counter((self.nodes[t["elementos"][0]]["tipo"] if t["elementos"][0] in self.nodes else "Fluxo")
                       for t in self.ranked)
        self.paras(f"Dos cenários, {totals['Processo']} têm processo como elemento principal, {totals['Armazenamento']} têm armazenamento e {totals['Fluxo']} têm seta. A concentração em processos reflete a localização de decisões de autenticação, autorização e tratamento de dados.")
        self.heading("7.3 PLANO DE MITIGAÇÃO",2)
        self.paras("O plano agrupa cenários com causas ou controles compartilhados. Os grupos de autenticação, cadastro e autorização precedem as medidas de contenção porque alteram a identidade, o papel ou a titularidade usada nas demais verificações. Os controles de auditoria podem começar em paralelo para preservar evidências durante o tratamento.")
        self.quadro("Frentes de tratamento e critérios de aceite",
            ("Frente","Área e ameaças","Tratamento","Aceite"),
            [(n,title+"\n"+ids,treatment,accept) for n,title,ids,treatment,accept in PLAN],
            (1.2,5.1,5.4,4.3),center=(0,))

    @staticmethod
    def plan_ids(raw):
        ids=[]
        prefix=None
        for part in re.findall(r"T-FX\d-\d\d|\b\d\d\b",raw):
            if part.startswith("T-"):
                prefix=part[:-2]
                ids.append(part)
            elif prefix:
                ids.append(prefix+part)
        return ids

    def last_chapters(self):
        self.chapter(8,"VALIDAÇÃO E LIMITAÇÕES")
        for i,(head,content) in enumerate(VALIDATION,1):
            self.heading(head,2)
            self.paras(content)
            if i==2:
                self.quadro("Revisão cruzada por fluxo",("ID","Responsável proposto","Revisor proposto","Situação"),
                    [(fid,f["responsavel_previsto"],f["revisor_previsto"],"A confirmar pela equipe")
                     for fid,f in self.m["fluxos"].items()],(1.25,5.45,5.45,3.85))
        self.chapter(9,"CONCLUSÃO")
        self.paras(CONCLUSION)
        self.heading("REFERÊNCIAS",page=True,center=True,key="refs",listed=True)
        for ref in BIB:
            p=self.p(ref,"Referência M2")
            p.paragraph_format.keep_together=True

    def appendices(self):
        self.heading("APÊNDICE A  ARQUIVOS E FONTES DO MODELO",page=True,key="apa",listed=True)
        self.paras("O arquivo editável DFD_Juice_Shop.drawio contém as seis páginas do DFD. O arquivo modelo_ameacas.json reúne elementos, setas, fronteiras, questionário, matriz e ameaças. Os scripts de geração de diagramas, validação, extração de metadados da M1 e reconstrução do relatório acompanham a pasta trabalho2/. O CSV de priorização é derivado das notas do modelo.")
        self.heading("A.1 Repositórios de referência",2)
        self.p("Trabalho 1, commit "+self.m["commit_m1"]+".","Fonte M2")
        self.p(M1_URL+"/tree/"+self.m["commit_m1"],"Fonte M2")
        self.p("OWASP Juice Shop v20.2.0, commit "+self.m["commit_juice_shop"]+".","Fonte M2")
        self.p(JS_URL+"/tree/"+self.m["commit_juice_shop"],"Fonte M2")
        self.heading("A.2 Guias técnicos citados no registro",2)
        self.quadro("Guias da OWASP por código",("Código","Guia"),
            [(k,v["titulo"]) for k,v in self.m["cheat_sheets"].items()],(2.8,13.2),
            source="OWASP Foundation ([s. d.]). Os endereços completos constam de modelo_ameacas.json.")
        self.heading("A.3 Justificativas de não aplicabilidade",2)
        self.quadro("Justificativas de não aplicabilidade nas matrizes",("Código","Justificativa"),
            [(f"N/A {code[2:]}",reason) for code,reason in self.m["justificativas_na"].items()],(1.7,14.3))
        self.heading("APÊNDICE B  CAPTURAS E EXTRATOS DE EVIDÊNCIA",page=True,key="apb",listed=True)
        self.paras("As imagens reproduzem recortes de capturas históricas da M1. As ocultações retiram valores de credenciais. Os extratos exibem metadados e nomes de campos selecionados dos arquivos HTTP e identificam a inspeção estática nas rotas sem captura local.")
        self.heading("B.1 Login e sessão",2)
        self.picture(7,"Sessão administrativa obtida no ensaio V1",
                     ROOT/"evidencias"/"figura_07.png","Silva et al. (2026), evidencias/image.png.",width=11)
        self.picture(8,"Campo de hash no JWT da evidência V2",
                     ROOT/"evidencias"/"figura_08.png","Silva et al. (2026), evidencias/image-3.png. Valores ocultados.",width=10)
        self.heading("A1  Extrato de V1, V2 e V6",3)
        entries=[(x["achado"],"POST /rest/user/login",x["resposta"],x["alg"]+". Chaves: "+", ".join(x["claims"])+". Campo password presente.")
                 for x in self.extract["jwt"]]
        entries += [("V6","POST /rest/user/login","15 × HTTP 401 e 1 × HTTP 200","Arquivos 02 a 16 e 17 de V6. A última requisição usou a credencial correta.")]
        self.quadro("Extrato histórico de autenticação",("ID","Requisição","Resposta","Leitura"),entries,(1.4,4.1,3.6,6.9),
                    source="Silva et al. (2026), pares HTTP de V1, V2 e V6.")
        self.heading("B.2 Cadastro e recuperação",2)
        self.heading("A2  Extrato de V7",3)
        reset=self.extract["reset"]
        self.quadro("Extrato HTTP do cadastro e do reset",
            ("Par","Requisição","Resposta","Cota e saldo"),
            [(x["arquivo"],x["requisicao"].replace("http://127.0.0.1:3000",""),x["resposta"],
              x["X-RateLimit-Limit"]+" / "+x["X-RateLimit-Remaining"] if "X-RateLimit-Limit" in x else "Sem cabeçalho no par") for x in reset],
            (1.25,6.8,4.25,3.7),source="Silva et al. (2026), evidencias/V7-reset-senha-pergunta-seguranca/http/.")
        self.paras("A resposta da tentativa 09 inclui o campo password no objeto user. O valor do hash foi omitido deste extrato. A associação duplicada e o reset subsequente recusado constam da tabela de achados da M1.")
        self.heading("B.3 Cesta, tratamento de erros e arquivos",2)
        self.picture(9,"Resposta de cesta alheia no ensaio V3",
                     ROOT/"evidencias"/"figura_09.png","Silva et al. (2026), evidencias/image-4.png.")
        self.picture(10,"Detalhes do framework em resposta de erro V4",
                     ROOT/"evidencias"/"figura_10.png","Silva et al. (2026), captura v4-erro-verboso.png. Recorte da requisição e do corpo.")
        self.picture(11,"Diretório público identificado no ensaio V5",
                     ROOT/"evidencias"/"figura_11.png","Silva et al. (2026), captura v5-listagem-diretorio.png.")
        self.heading("A3  Extrato da leitura de cesta",3)
        cross=self.extract["cesta"]
        self.paras(f'No ensaio complementar de V3, o login vinculou a conta A à cesta {cross["cesta_conta_a"]} e a conta B à cesta {cross["cesta_conta_b"]}. A requisição 06 usou a sessão da conta B para pedir a cesta {cross["cesta_lida"]}, retornada com {cross["resposta"]}. A Figura 9 corresponde à captura original, com IDs de uma execução diferente (SILVA et al., 2026).')
        self.heading("B.4 Evidência documental de administração e contabilidade",2)
        self.heading("A4  Inspeção do código e de testes da versão",3)
        self.quadro("Trilha documental do FX4",("Ponto","Arquivo na tag v20.2.0","Resultado da leitura"),
            [("Listagem administrativa","frontend/src/app/Services/user.service.ts e routes/authenticatedUsers.ts",
              "A SPA chama authentication-details. O handler lê contas, consulta o mapa de sessões e mascara dois campos."),
             ("Proteção de função","server.ts e lib/insecurity.ts",
              "Listagens de contas e DELETE de feedback usam autenticação. Rotas de pedidos verificam papel accounting."),
             ("Teste publicado pelo projeto","test/api/authenticated-users.test.ts, user.test.ts e order-history.test.ts",
              "Há casos de listagem com token e de separação entre admin, cliente e accounting nas rotas de pedidos.")],
             (3.5,5.8,6.7),source="OWASP Juice Shop (2026). Casos upstream consultados como código.")
        self.paras("A captura funcional de checkout completo, moderação de feedback e alteração de entrega depende de nova observação no laboratório. Para confrontar a implementação, o critério registra papel da sessão, método, rota, status e alteração do recurso com dados de teste.")

    def build(self,out):
        self.front()
        self.chapters_1_to_4()
        self.chapter_5()
        self.chapter(6,"ANÁLISE DOS FLUXOS",page=False)
        self.paras("A análise aplica a ficha, a matriz STRIDE, o questionário e o registro a quatro funções. Em cada caso, a primeira referência identifica o principal elemento afetado. As fontes de execução e as hipóteses de código aparecem separadas.")
        for n,(fid,f) in enumerate(self.m["fluxos"].items(),1):
            self.flow_section(n,fid,f)
        self.chapter_7()
        self.last_chapters()
        self.appendices()
        self.index()
        self.doc.save(out)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida",type=Path,default=ROOT/"M2_Relatorio_Final.docx")
    parser.add_argument("--figuras",type=Path,default=ROOT/"modelo")
    parser.add_argument("--paginas",type=Path,default=ROOT/"modelo"/"paginas.json")
    args=parser.parse_args()
    m=json.loads((ROOT/"modelo"/"modelo_ameacas.json").read_text(encoding="utf-8"))
    e=json.loads((ROOT/"evidencias"/"extratos_m1.json").read_text(encoding="utf-8"))
    pages=json.loads(args.paginas.read_text(encoding="utf-8")) if args.paginas.is_file() else {}
    with tempfile.TemporaryDirectory() as tmp:
        temp=Path(tmp)
        for file in args.figuras.glob("*.svg"):
            raster=args.figuras/(file.stem+".png")
            if raster.exists():
                shutil.copyfile(raster,temp/raster.name)
            else:
                subprocess.run(["inkscape",str(file),"--export-filename="+str(temp/raster.name),
                                "--export-width=2000"],check=True)
        Report(m,e,temp,pages).build(args.saida)
    print(args.saida)

if __name__=="__main__":
    main()
