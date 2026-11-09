"""Reaplica formatação ABNT e melhora a leitura das 112 respostas."""
from pathlib import Path
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "M2_Relatorio_Final_diego_e_equipe_revisado.docx"
TEMP = ROOT / ".revisao_m2" / "relatorio_formatado.docx"
sys.path.insert(0, str(ROOT / "m2-seg-system-diegos" / "trabalho2" / "codigo"))
from texto_relatorio import BIB

CATEGORIES = {
    "Compreensão": [f"Q{i}" for i in range(1, 8)],
    "Falsificação de identidade": [f"S{i}" for i in range(1, 4)],
    "Adulteração": [f"T{i}" for i in range(1, 4)],
    "Repúdio": [f"R{i}" for i in range(1, 4)],
    "Divulgação de informação": [f"I{i}" for i in range(1, 4)],
    "Disponibilidade": [f"D{i}" for i in range(1, 4)],
    "Elevação de privilégio": [f"E{i}" for i in range(1, 4)],
    "Fechamento": [f"V{i}" for i in range(1, 4)],
}


def set_font(run, size=12):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    fonts = rpr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
        fonts.set(qn("w:" + attr), "Times New Roman")


def add_bold_text(p, label, answer):
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0)
    p.paragraph_format.right_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_together = True
    a = p.add_run(label)
    a.bold = True
    set_font(a)
    b = p.add_run(answer)
    set_font(b)


def split_category(text, keys):
    matches = []
    cursor = 0
    for key in keys:
        m = re.search(r"(?<!\S)" + re.escape(key) + r":\s*", text[cursor:])
        if not m:
            raise ValueError(f"Resposta {key} não encontrada em: {text[:100]}")
        start = cursor + m.start()
        answer_start = cursor + m.end()
        matches.append((key, start, answer_start))
        cursor = answer_start
    out = []
    for i, (key, start, answer_start) in enumerate(matches):
        end = matches[i + 1][1] if i + 1 < len(matches) else len(text)
        answer = text[answer_start:end].strip()
        if i + 1 < len(matches):
            answer = answer.rstrip()
        out.append((key, answer))
    return out


def format_questionnaires(doc):
    paras = list(doc.paragraphs)
    starts = [i for i, p in enumerate(paras) if p.text.strip() == "Questionário do fluxo"]
    if len(starts) != 4:
        raise ValueError(f"Esperados 4 questionários, encontrados {len(starts)}")
    total = 0
    for start in reversed(starts):
        stop = next((i for i in range(start + 1, len(paras))
                     if paras[i].text.startswith("Quadro ") and "Registro de ameaças" in paras[i].text), len(paras))
        block = paras[start + 1:stop]
        existing_answers = [p for p in block if re.match(r"^(?:Q[1-7]|[STRIDE][1-3]|V[1-3]): ", p.text)]
        if existing_answers:
            for p in block:
                if p.text.strip() in CATEGORIES:
                    p.style = "Heading 4"
                    p.paragraph_format.keep_with_next = True
                elif re.match(r"^(?:Q[1-7]|[STRIDE][1-3]|V[1-3]): ", p.text):
                    p.paragraph_format.keep_together = True
                    if p.runs:
                        p.runs[0].bold = True
            total += len(existing_answers)
            continue
        rows = []
        for p in block:
            txt = p.text.strip()
            for category, keys in CATEGORIES.items():
                if txt.startswith(category + "."):
                    rows.append((p, category, split_category(txt, keys)))
                    break
        if len(rows) != len(CATEGORIES):
            raise ValueError(f"Questionário incompleto: {len(rows)} categorias")
        for old, category, answers in reversed(rows):
            old.text = category
            old.style = "Heading 4"
            old.paragraph_format.keep_with_next = True
            old.paragraph_format.keep_together = True
            for r in old.runs:
                set_font(r)
                r.bold = True
            anchor = old._p
            inserted = []
            for key, answer in answers:
                new_p = OxmlElement("w:p")
                anchor.addnext(new_p)
                anchor = new_p
                paragraph = Paragraph(new_p, old._parent)
                add_bold_text(paragraph, key + ": ", answer)
                inserted.append(paragraph)
                total += 1
    if total != 112:
        raise ValueError(f"Esperadas 112 respostas; formatadas {total}")


def apply_academic_format(doc):
    # Corpo, títulos, legendas, fontes de quadros e células: Times New Roman 12,
    # espaçamento 1,5. Mantém o recuo de primeira linha do texto corrido.
    for style in doc.styles:
        if getattr(style, "type", None) == 1:
            style.font.name = "Times New Roman"
            style.font.size = Pt(12)
            try:
                style.paragraph_format.line_spacing = 1.5
            except Exception:
                pass
    for part in doc.part.package.parts:
        if not hasattr(part, "element"):
            continue
        for element in part.element.iter(qn("w:p")):
            p = Paragraph(element, part)
            text = p.text.strip()
            for r in p.runs:
                set_font(r)
            if not text:
                continue
            is_reference = p.style.name == "Referência M2"
            pf = p.paragraph_format
            pf.line_spacing = 1.0 if is_reference else 1.5
            pf.space_before = Pt(0)
            pf.space_after = Pt(12 if is_reference else 4)
            if is_reference:
                # ABNT NBR 6023: alinhamento à esquerda, espaço simples,
                # separação entre referências e sem recuo de parágrafo.
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                pf.left_indent = Cm(0)
                pf.first_line_indent = Cm(0)
            elif p.style.name == "Normal":
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                pf.left_indent = Cm(0)
                pf.first_line_indent = Cm(1.25)
            elif p.style.name.startswith("Heading"):
                pf.first_line_indent = Cm(0)
            elif p.style.name in ("Legenda M2", "Fonte M2", "Índice M2"):
                pf.first_line_indent = Cm(0)
    # Reaplica também à primeira linha de cabeçalhos de tabela e a cada célula.
    for table in doc.tables:
        table.allow_autofit = True
        for row in table.rows:
            for cell in row.cells:
                cell.vertical_alignment = 0
                for p in cell.paragraphs:
                    p.paragraph_format.line_spacing = 1.5
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.paragraph_format.left_indent = Cm(0)
                    p.paragraph_format.keep_together = True
                    for r in p.runs:
                        set_font(r)
    # Não limitar a altura de imagens: preserva a proporção e a figura inteira.
    for shape in doc.inline_shapes:
        shape._inline.xpath(".//a:srcRect")[0].getparent().remove(shape._inline.xpath(".//a:srcRect")[0]) if shape._inline.xpath(".//a:srcRect") else None


def restore_reference_emphasis(doc):
    references = [p for p in doc.paragraphs if p.style.name == "Referência M2"]
    if len(references) != len(BIB):
        raise ValueError(f"Lista bibliográfica divergente: {len(references)} parágrafos e {len(BIB)} fontes")
    for paragraph, source in zip(references, BIB):
        paragraph.clear()
        cursor = 0
        for match in re.finditer(r"\*\*(.+?)\*\*", source):
            if match.start() > cursor:
                run = paragraph.add_run(source[cursor:match.start()])
                set_font(run)
            run = paragraph.add_run(match.group(1))
            run.bold = True
            set_font(run)
            cursor = match.end()
        if cursor < len(source):
            run = paragraph.add_run(source[cursor:])
            set_font(run)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.line_spacing = 1.0
        paragraph.paragraph_format.space_after = Pt(12)
        paragraph.paragraph_format.left_indent = Cm(0)
        paragraph.paragraph_format.first_line_indent = Cm(0)


def main():
    doc = Document(SOURCE)
    format_questionnaires(doc)
    # O ponto de interrogação público usa e-mail como parâmetro; remove a
    # elipse usada como placeholder no quadro e deixa uma rota exemplificada.
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if "security-question?email=" in cell.text and chr(0x2026) in cell.text:
                    cell.text = cell.text.replace(chr(0x2026), "exemplo")
    for p in doc.paragraphs:
        if p.text.startswith("Figura 7:"):
            p.text = "Figura 7: Recorte da interface após autenticação por injeção SQL (reprodução M2)"
        elif p.text.startswith("Figura 8:"):
            p.text = "Figura 8: Recorte do painel de administração (reprodução M2)"
    apply_academic_format(doc)
    restore_reference_emphasis(doc)
    for part in doc.part.package.parts:
        if hasattr(part, "element"):
            for node in part.element.iter(qn("w:t")):
                if node.text:
                    node.text = node.text.replace(chr(0x2014), ": ").replace(chr(0x2013), " a ")
    TEMP.parent.mkdir(exist_ok=True)
    doc.save(TEMP)
    # Confere o conteúdo antes de substituir a entrega.
    check = Document(TEMP)
    assert len([p for p in check.paragraphs if re.match(r"^(Q[1-7]|[STRIDE][1-3]|V[1-3]): ", p.text)]) == 112
    assert all(chr(0x2014) not in p.text and chr(0x2013) not in p.text for p in check.paragraphs)
    print(f"{TEMP}: respostas separadas=112, imagens={len(check.inline_shapes)}, quadros={len(check.tables)}")


if __name__ == "__main__":
    main()
