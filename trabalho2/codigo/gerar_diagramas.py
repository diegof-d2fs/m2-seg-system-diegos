"""Gera os seis DFDs editáveis e suas versões SVG a partir do modelo."""
import argparse
from html import escape
import json
from pathlib import Path
from textwrap import wrap
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from validar_modelo import ROOT, by_id, validate

FILL = {"Processo":"#e9eef1", "Entidade externa":"#ffffff", "Armazenamento":"#f5f5f5"}
INK = "#263542"
RULE = "#556575"
TB_INK = "#655c6f"

class Diagram:
    def __init__(self, name, height):
        self.name = name
        self.width = 1020
        self.height = height
        self.model = Element("mxGraphModel", {
            "grid":"1","gridSize":"10","page":"1","pageScale":"1",
            "pageWidth":str(self.width),"pageHeight":str(height)
        })
        self.root = SubElement(self.model,"root")
        SubElement(self.root,"mxCell",id="0")
        SubElement(self.root,"mxCell",id="1",parent="0")
        self.svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" viewBox="0 0 {self.width} {height}">',
            f'<title>{escape(name)}</title>',
            f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>',
            f'<rect x="0" y="0" width="{self.width}" height="{height}" fill="white"/>',
        ]
        self.boxes = {}
        self.count = 0

    def id(self):
        self.count += 1
        return f"v{self.count}"

    def vertex(self, key, text, style, x, y, w, h):
        c = SubElement(self.root,"mxCell",id=key,value=text,style=style,vertex="1",parent="1")
        SubElement(c,"mxGeometry",{"x":str(x),"y":str(y),"width":str(w),"height":str(h),"as":"geometry"})

    def svg_text(self, lines, x, y, size, *, bold=False, align="middle", color=INK, halo=False):
        lines = list(lines)
        halo_style = ' style="paint-order:stroke;stroke:white;stroke-width:3px;stroke-linejoin:round;"' if halo else ""
        for i, line in enumerate(lines):
            self.svg.append(f'<text x="{x}" y="{y+i*(size+3)}" text-anchor="{align}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}"{halo_style}>{escape(line)}</text>')

    def text(self, label, x, y, w, size=17, bold=False, align="left"):
        self.vertex(self.id(),label,f"text;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;fontSize={size};fontColor={INK};fontStyle={int(bold)};",x,y-15,w,24)
        self.svg_text([label],x+(w/2 if align=="center" else 2),y+1,size,bold=bold,align="middle" if align=="center" else "start")

    def box(self,key,node,x,y,w,h):
        self.boxes[key] = (x,y,w,h)
        kind = node["tipo"]
        name = node["nome"]
        chunks = wrap(name, width=max(9,int(w/(8.0 if kind=="Armazenamento" else 11.5))), break_long_words=False)
        lines = [node["id"],*chunks]
        size = 21 if key=="P0" else (16 if kind=="Armazenamento" else 18)
        if kind=="Armazenamento":
            shape = "shape=partialRectangle;top=1;bottom=1;left=0;right=0;"
            self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{FILL[kind]}"/>')
            self.svg.append(f'<path d="M{x} {y} h{w} M{x} {y+h} h{w}" stroke="{RULE}" stroke-width="2"/>')
        else:
            radius = 12 if kind=="Processo" else 0
            shape = f"rounded={int(bool(radius))};arcSize=12;"
            self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{FILL[kind]}" stroke="{RULE}" stroke-width="2"/>')
        self.vertex(key,"\n".join(lines),f"{shape}whiteSpace=wrap;html=0;fillColor={FILL[kind]};strokeColor={RULE};fontColor={INK};fontSize={size};fontStyle=1;align=center;verticalAlign=middle;strokeWidth=2;",x,y,w,h)
        center = y+h/2-(len(lines)-1)*(size+3)/2+size*.35
        self.svg_text(lines,x+w/2,center,size,bold=True)

    def boundary(self,key,label,x,y,w,h):
        self.vertex(key,"",f"rounded=0;fillColor=none;dashed=1;dashPattern=7 5;strokeColor={TB_INK};strokeWidth=2;pointerEvents=0;",x,y,w,h)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{TB_INK}" stroke-width="2" stroke-dasharray="7 5"/>')
        if label:
            self.text(label,x+6,y-8,w-12,16,bold=True)

    def arrow(self, ident, label, src, dst, y, *, small=False, label_y=-7):
        sx, sy, sw, sh = self.boxes[src]
        dx, dy, dw, dh = self.boxes[dst]
        left_to_right = sx < dx
        start, end = (sx+sw,dx) if left_to_right else (sx,dx+dw)
        x_exit, x_entry = (1,0) if left_to_right else (0,1)
        e = SubElement(self.root,"mxCell",id=ident,value=label,source=src,target=dst,edge="1",parent="1",
                       style=f"endArrow=block;endFill=1;strokeColor={INK};strokeWidth=1.4;fontColor={INK};fontSize={14 if small else 16};exitX={x_exit};exitY={(y-sy)/sh:.5f};entryX={x_entry};entryY={(y-dy)/dh:.5f};exitPerimeter=0;entryPerimeter=0;labelBackgroundColor=#ffffff;")
        g = SubElement(e,"mxGeometry",{"relative":"1","as":"geometry"})
        SubElement(g,"mxPoint",{"x":"0","y":str(label_y-3),"as":"offset"})
        self.svg.append(f'<path d="M{start} {y} H{end}" fill="none" stroke="{INK}" stroke-width="1.55" marker-end="url(#a)"/>')
        self.svg_text([label],(start+end)/2,y+label_y,14 if small else 16,halo=True)

    def write(self, folder, slug):
        target = folder/(slug+".svg")
        target.write_text("\n".join(self.svg+["</svg>"])+"\n",encoding="utf-8")

CONTEXT_LABELS = [
    ("Credenciais, cadastro e recuperação","Sessão, respostas e conteúdo público"),
    ("Sessão, cesta e dados de compra","Perfil, pedido e comprovante"),
    ("Consulta de contas e moderação","Listas e resultado da moderação"),
    ("Consulta de pedidos e entrega","Pedidos e situação da entrega"),
]
STORE_LABELS = {
    21:"Conta e cesta",22:"Perfil e ID",
    23:"Grava ou lê JWT",24:"Perfil e cesta",
    25:"Cadastro e reset",26:"Dados e resultado",
    27:"Cesta e checkout",28:"Dados e gravações",
    29:"Pedido e histórico",30:"Pedido ou confirmação",
    31:"Consulta e modera",32:"Contas e feedback",
    33:"Consulta de sessão",34:"Titular e cesta",
    35:"Lista e atualiza",36:"Pedidos e retorno",
    37:"Grava o PDF",38:"Conclusão ou erro",
    39:"Lista ou lê arquivo",40:"Índice ou arquivo",
    41:"Log do login",42:"Log do reset",
    43:"Log da compra",44:"Log administrativo",
    45:"Token por conta",46:"Ref. de sessão",
}
WIRE_LABELS = {
    9:"Credenciais",10:"Sessão e perfil",11:"Cadastro e reset",12:"Confirmação",
    13:"Itens e pedido",14:"Cesta e pedido",15:"JWT e ação",16:"Listas e status",
    17:"Nome de arquivo",18:"Índice ou PDF",19:"Grava",20:"Lê",
}
def context(nodes):
    d = Diagram("DFD nível 0",557)
    d.boundary("TB-01","TB-01  Interface externa da solução",583,65,421,415)
    d.box("P0",nodes["P0"],640,92,300,375)
    for index,(out,back) in enumerate(CONTEXT_LABELS,1):
        y = 112+(index-1)*98
        eid = f"E{index}"
        d.box(eid,nodes[eid],28,y,185,67)
        n = index*2-1
        d.arrow(f"F{n:02}",f"F{n:02}  {out}",eid,"P0",y+25)
        d.arrow(f"F{n+1:02}",f"F{n+1:02}  {back}","P0",eid,y+53)
    d.text("Entidades externas",30,53,190,18,True)
    d.text("P0 agrega a interface e os serviços da loja. As setas representam dados em cada sentido.",29,528,950,17)
    return d

def detail(nodes,edges,selected,title):
    active = [edges[e] for e in selected]
    present = {e[side] for e in active for side in ("origem","destino")}
    actors = sorted(p for p in present if p.startswith("E"))
    procs = sorted(p for p in present if p.startswith("P") and p!="P1")
    groups = {}
    for p in procs:
        grouped = {}
        for e in active:
            if e["origem"]==p and e["destino"].startswith("D"):
                grouped.setdefault(e["destino"],[]).append(e)
            if e["destino"]==p and e["origem"].startswith("D"):
                grouped.setdefault(e["origem"],[]).append(e)
        groups[p] = grouped
    y_start = 65
    bands = {}
    y = y_start
    for p in procs:
        h = max(69, sum(57 if len(es)>1 else 51 for es in groups[p].values()))
        bands[p] = (y,h)
        y += h+18
    left_end = y_start + 71*(len(actors)+int("D0" in present))
    end = max(y-18,left_end-14)
    d = Diagram(title,end+91)
    d.boundary("TB-02","TB-02  Contêiner Docker / labnet",395,y_start-10,614,end-y_start+20)
    d.boundary("TB-03","TB-03  Dados",827,y_start-10,176,end-y_start+20)
    d.boundary("TB-01","",371,y_start-10,17,end-y_start+20)
    d.text("TB-01",335,y_start-18,58,16,True)
    d.box("P1",nodes["P1"],213,y_start,143,end-y_start)
    for index,eid in enumerate(actors):
        py=y_start+71*index
        d.box(eid,nodes[eid],14,py,151,62)
        for e in active:
            if {e["origem"],e["destino"]}=={eid,"P1"}:
                d.arrow(e["id"],e["id"],e["origem"],e["destino"],py+(23 if e["origem"]==eid else 49),small=True,label_y=-5)
    if "D0" in present:
        py=y_start+71*len(actors)
        d.box("D0",nodes["D0"],14,py,151,58)
        d.arrow("F19","F19","P1","D0",py+21,small=True,label_y=-5)
        d.arrow("F20","F20","D0","P1",py+46,small=True,label_y=-5)
    for proc in procs:
        py,h = bands[proc]
        d.box(proc,nodes[proc],512,py,160,h)
        web = [e for e in active if {e["origem"],e["destino"]}=={"P1",proc}]
        for e in web:
            fid = e["id"]
            n = int(fid[1:])
            cy = py+h/2+(-14 if e["origem"]=="P1" else 16)
            d.arrow(fid,f"{fid}  {WIRE_LABELS[n]}",e["origem"],e["destino"],cy,small=True,label_y=-5)
        zy=py
        for store, connections in sorted(groups[proc].items()):
            block = 57 if len(connections)>1 else 51
            key = proc+"-"+store
            d.box(key,nodes[store],845,zy+2,145,block-4)
            for j,e in enumerate(sorted(connections,key=lambda entry:entry["id"])):
                fid=e["id"]
                a = key if e["origem"]==store else proc
                b = key if e["destino"]==store else proc
                cy=zy+(19+28*j if len(connections)>1 else 29)
                d.arrow(fid,f"{fid}  {STORE_LABELS[int(fid[1:])]}",a,b,cy,small=True,label_y=-4)
            zy+=block
    d.text("TB-01 separa cliente e servidor. TB-02 delimita a implantação. TB-03 indica a passagem lógica aos dados.",18,end+35,990,16)
    d.text("IDs repetidos de armazenamento representam o mesmo recurso. O inventário detalha dados e protocolos.",18,end+63,990,16)
    return d

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo",type=Path,default=ROOT/"modelo"/"modelo_ameacas.json")
    parser.add_argument("--saida",type=Path,default=ROOT/"modelo")
    args=parser.parse_args()
    args.saida.mkdir(parents=True,exist_ok=True)
    model=json.loads(args.modelo.read_text(encoding="utf-8"))
    validate(model)
    nodes,edges=by_id(model["elementos"]),by_id(model["arestas"])
    diagrams = [("dfd_nivel_0",context(nodes)),("dfd_nivel_1",detail(nodes,edges,list(edges),"DFD nível 1"))]
    diagrams += [(fid.lower(),detail(nodes,edges,f["arestas"],fid+" "+f["nome"])) for fid,f in model["fluxos"].items()]
    mxfile=Element("mxfile",host="app.diagrams.net",type="device")
    for slug,diagram in diagrams:
        SubElement(mxfile,"diagram",id=slug,name=diagram.name).append(diagram.model)
        diagram.write(args.saida,slug)
    indent(mxfile)
    (args.saida/"DFD_Juice_Shop.drawio").write_bytes(tostring(mxfile,encoding="utf-8",xml_declaration=True))
    print(f"{len(diagrams)} diagramas gravados em {args.saida}")

if __name__=="__main__":
    main()
