"""Exporta o conteúdo do Word local para PDF paginado sem serviços externos."""
import argparse
from html import escape
from pathlib import Path
import re

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table as WordTable
from docx.text.paragraph import Paragraph as WordParagraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents


class ReportPDF(SimpleDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f,Paragraph) and hasattr(f,'toc_level'):
            self.notify('TOCEntry',(f.toc_level,f.getPlainText(),self.page))
            self.heading_pages[f.getPlainText()]=self.page


def export(source, target, table_size=9.0):
    for name,file in [('TNR','times.ttf'),('TNR-Bold','timesbd.ttf'),('TNR-Italic','timesi.ttf'),('TNR-BoldItalic','timesbi.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
    pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-Bold',italic='TNR-Italic',boldItalic='TNR-BoldItalic')
    d=Document(source)
    styles={
        'normal':ParagraphStyle('normal',fontName='TNR',fontSize=11,leading=13.2,spaceAfter=4,alignment=TA_JUSTIFY,firstLineIndent=1.0*cm),
        'question':ParagraphStyle('question',fontName='TNR',fontSize=10,leading=11.2,spaceAfter=3,alignment=TA_JUSTIFY),
        'caption':ParagraphStyle('caption',fontName='TNR',fontSize=10,leading=11.5,spaceBefore=5,spaceAfter=4,keepWithNext=True),
        'source':ParagraphStyle('source',fontName='TNR',fontSize=9,leading=10.2,spaceAfter=5),
        'reference':ParagraphStyle('reference',fontName='TNR',fontSize=9.5,leading=10.5,spaceAfter=5,splitLongWords=True),
        'cell':ParagraphStyle('cell',fontName='TNR',fontSize=table_size,leading=table_size+1,spaceAfter=0,splitLongWords=True),
    }
    for level,size in [(1,14),(2,12),(3,11),(4,10)]:
        styles['h'+str(level)]=ParagraphStyle('h'+str(level),fontName='TNR-Bold',fontSize=size,leading=size+2,spaceBefore=10,spaceAfter=6,keepWithNext=True)
    center=ParagraphStyle('center',fontName='TNR',fontSize=14,leading=18,alignment=TA_CENTER)
    story=[]
    cover=['UNIVERSIDADE DO VALE DO ITAJAÍ','ESCOLA POLITÉCNICA','CURSO DE CIÊNCIA DA COMPUTAÇÃO','Segurança de Sistemas Computacionais',
      'Diego Fonseca da Silva','Leonardo Pacheco B Dias','Gustavo Gonçalves Trindade','João Victor Rodrigues Santos',
      'MODELAGEM DE AMEAÇAS NO OWASP JUICE SHOP','TRABALHO 2','Relatório final de modelagem com DFD e STRIDE','Professor Ramicés dos Santos Silva','Itajaí (SC)','Novembro de 2026']
    for i,t in enumerate(cover):
        if i in [4,8,11,12]: story.append(Spacer(1,23 if i!=8 else 38))
        story.append(Paragraph(escape(t),center))
    story.append(PageBreak())
    active=False
    def text(p):
        return escape(p.text).replace('\n','<br/>')
    for el in d.element.body:
        if el.tag==qn('w:p'):
            p=WordParagraph(el,d)
            if p.text=='RESUMO': active=True
            if not active: continue
            t=p.text.strip()
            if t=='SUMÁRIO':
                story.extend([PageBreak(),Paragraph('SUMÁRIO',styles['h1'])])
                toc=TableOfContents()
                toc.levelStyles=[ParagraphStyle('toc0',fontName='TNR',fontSize=10.5,leading=14,spaceBefore=2),
                                 ParagraphStyle('toc1',fontName='TNR',fontSize=10,leading=13,leftIndent=12)]
                story.append(toc)
                story.append(PageBreak())
                continue
            if t:
                name=p.style.name
                if name.startswith('Heading '):
                    level=int(name.split()[-1]); style=styles.get('h'+str(level),styles['h3'])
                    if t=='REFERÊNCIAS':
                        story.append(PageBreak())
                elif name=='Título central': style=styles['h1']
                elif name=='Legenda M2': style=styles['caption']
                elif name=='Fonte M2': style=styles['source']
                elif name=='Referência M2': style=styles['reference']
                elif name=='Questão M2': style=styles['question']
                else: style=styles['normal']
                flow=Paragraph(text(p),style)
                if name in ['Heading 1','Heading 2']:
                    flow.toc_level=int(name[-1])-1
                story.append(flow)
            for blip in el.xpath('.//a:blip'):
                from io import BytesIO
                blob=d.part.related_parts[blip.get(qn('r:embed'))].blob
                pic=Image(BytesIO(blob))
                max_w=16*cm; max_h=6.5*cm
                factor=min(max_w/pic.imageWidth,max_h/pic.imageHeight)
                pic.drawWidth=pic.imageWidth*factor; pic.drawHeight=pic.imageHeight*factor
                pic.hAlign='CENTER'
                story.append(pic)
        elif el.tag==qn('w:tbl') and active:
            tab=WordTable(el,d)
            rows=[]
            for idx,row in enumerate(tab.rows):
                cells=[]
                for c in row.cells:
                    val=escape(c.text).replace('\n','<br/>')
                    if idx==0: val='<b>'+val+'</b>'
                    cells.append(Paragraph(val,styles['cell']))
                rows.append(cells)
            widths=[col.width for col in tab.columns]
            total=sum(widths)
            widths=[w/total*16*cm for w in widths]
            table=Table(rows,colWidths=widths,repeatRows=1,hAlign='CENTER',splitInRow=1)
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#777777')),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),
                ('TOPPADDING',(0,0),(-1,-1),1.5),('BOTTOMPADDING',(0,0),(-1,-1),1.5)]))
            story.append(table)
    def footer(canvas,doc):
        canvas.setFont('TNR',9);canvas.drawRightString(19*cm,1.2*cm,str(doc.page))
    doc=ReportPDF(str(target),pagesize=A4,leftMargin=3*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=1.6*cm,
        title='Modelagem de ameaças no OWASP Juice Shop',author='Diego Fonseca da Silva e equipe')
    doc.heading_pages={}
    doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)
    # Preenche o sumário visível do Word com a paginação do PDF entregue.
    anchor=next(p for p in d.paragraphs if p.text=='SUMÁRIO')
    toc_xml=anchor._p.getnext()
    if toc_xml is not None and toc_xml.xpath('.//w:instrText'):
        for heading,page in doc.heading_pages.items():
            p=WordParagraph(toc_xml,d).insert_paragraph_before(heading+'\t'+str(page),style='Índice M2')
            p.paragraph_format.line_spacing=13
        toc_xml.getparent().remove(toc_xml)
        d.save(source)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('entrada',type=Path);ap.add_argument('saida',type=Path)
    ap.add_argument('--fonte-quadros',type=float,default=9.0)
    args=ap.parse_args();export(args.entrada,args.saida,args.fonte_quadros)
