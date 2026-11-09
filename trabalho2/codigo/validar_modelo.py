"""Valida o modelo e gera estatísticas sem acesso à rede."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTION_IDS = [f"Q{i}" for i in range(1,8)] + [
    f"{category}{i}" for category in "STRIDEV" for i in range(1,4)
]

def media(threat):
    return sum(threat["notas"]) / 5

def risco(threat):
    value = media(threat)
    if value >= 7:
        return "Alto"
    return "Médio" if value >= 4 else "Baixo"

def ordem(threat):
    # A confirmação desempata a média. O dano desempata o status.
    return (-sum(threat["notas"]), threat["status"] != "Confirmada no T1",
            -threat["notas"][0], threat["id"])

def by_id(records):
    items = {entry["id"]: entry for entry in records}
    if len(items) != len(records):
        raise ValueError("Há identificadores repetidos.")
    return items

def check(condition, message):
    if not condition:
        raise ValueError(message)

def validate(model):
    nodes = by_id(model["elementos"])
    edges = by_id(model["arestas"])
    bounds = by_id(model["fronteiras"])
    threats = by_id(model["ameacas"])
    check(not (nodes.keys() & edges.keys()), "IDs colidem entre nós e setas.")
    check(len(model["fluxos"]) >= 4, "São necessários pelo menos quatro fluxos.")
    for fid, edge in edges.items():
        a, b = nodes[edge["origem"]], nodes[edge["destino"]]
        check(a["tipo"] == "Processo" or b["tipo"] == "Processo",
              f"{fid}: seta não liga um processo.")
        check(set(edge["fronteiras"]) <= bounds.keys(), f"{fid}: fronteira desconhecida.")
    all_edges = list(edges.values())
    for nid, node in nodes.items():
        if node["tipo"] == "Processo" and nid != model["contexto"]["processo"]:
            check(any(e["origem"] == nid for e in all_edges), f"{nid}: processo sem saída.")
            check(any(e["destino"] == nid for e in all_edges), f"{nid}: processo sem entrada.")
    context = model["contexto"]
    check(nodes[context["processo"]]["tipo"] == "Processo", "O contexto exige um processo.")
    check(context["fronteira"] in bounds, "A fronteira do contexto é desconhecida.")
    external = {n for n, node in nodes.items() if node["tipo"] == "Entidade externa"}
    external_edges = {eid for eid, e in edges.items() if {e["origem"],e["destino"]} & external}
    check(set(context["interfaces"]) == external_edges, "Níveis 0 e 1 não estão balanceados.")
    for fid, flow in model["fluxos"].items():
        this_flow = [t for t in threats.values() if t["fluxo"] == fid]
        check(len(this_flow) >= 6, f"{fid}: menos de seis ameaças.")
        check({t["stride"] for t in this_flow} == set("STRIDE"), f"{fid}: categoria ausente.")
        check(set(flow["questionario"]) == set(QUESTION_IDS), f"{fid}: questionário incompleto.")
        check(any(edges[e]["fronteiras"] for e in flow["arestas"]), f"{fid}: nenhuma fronteira cruzada.")
        expected = set(flow["arestas"]) | {
            edges[e][side] for e in flow["arestas"] for side in ("origem","destino")
        }
        check(set(flow["elementos"]) == set(flow["matriz"]) == expected, f"{fid}: cobertura divergente.")
        for eid, row in flow["matriz"].items():
            kind = nodes[eid]["tipo"] if eid in nodes else "Fluxo"
            applicable = model["regras_stride"][kind] + ("R" if eid=="D5" else "")
            check(set(row) == set("STRIDE"), f"{fid}/{eid}: matriz incompleta.")
            for category, values in row.items():
                check(bool(values) == (category in applicable), f"{fid}/{eid}/{category}: aplicabilidade incorreta.")
                for value in values:
                    if value in model["justificativas_na"]:
                        check(len(values)==1, f"{fid}/{eid}/{category}: N/A junto a ameaça.")
                        continue
                    t = threats[value]
                    check(t["fluxo"]==fid and eid in t["elementos"] and category==t["stride"],
                          f"{fid}/{eid}/{category}: ameaça incoerente.")
        for t in this_flow:
            tid, cat = t["id"], t["stride"]
            check(t["propriedade"] == model["stride"][cat], f"{tid}: propriedade incompatível.")
            check(tid.startswith(f"T-{fid}-"), f"{tid}: identificador incompatível.")
            check(bool(t["elementos"]) and all(tid in flow["matriz"][e][cat] for e in t["elementos"]),
                  f"{tid}: ameaça não inteiramente coberta na matriz.")
            check(len(t["notas"]) == len(t["justificativas"]) == 5, f"{tid}: DREAD incompleto.")
            check(all(type(s) is int and 1 <= s <= 10 for s in t["notas"]), f"{tid}: nota fora da escala.")
            check(all(t["justificativas"]), f"{tid}: justificativa vazia.")
            check(t["cheat_sheet"] in model["cheat_sheets"] and bool(t["asvs_5_0_0"]) and bool(t["cwe"]),
                  f"{tid}: referência de controle ausente.")
            check(t["status"] in {"Plausível","Confirmada no T1","Tratada por controle existente"},
                  f"{tid}: status não previsto.")
            if t["status"] == "Confirmada no T1":
                known = {e["id"] for e in model["evidencias_m1"] if tid in e["relacao"]}
                check(any(t["evidencia"].startswith(e + ".") for e in known),
                      f"{tid}: evidência histórica não localizada.")
    check({t["fluxo"] for t in threats.values()} == set(model["fluxos"]), "Há ameaças fora dos fluxos.")
    return sorted(threats.values(), key=ordem)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modelo", type=Path, default=ROOT/"modelo"/"modelo_ameacas.json")
    parser.add_argument("--csv", type=Path, help="Caminho opcional para exportar a priorização.")
    args = parser.parse_args()
    model = json.loads(args.modelo.read_text(encoding="utf-8"))
    ranked = validate(model)
    print(f'{len(model["fluxos"])} fluxos, {len(ranked)} ameaças, '
          f'{sum(len(f["questionario"]) for f in model["fluxos"].values())} respostas.')
    print("STRIDE:", dict(Counter(t["stride"] for t in ranked)))
    print("Risco:", dict(Counter(risco(t) for t in ranked)))
    print("Status:", dict(Counter(t["status"] for t in ranked)))
    for pos, t in enumerate(ranked[:10],1):
        print(f'{pos:2} {t["id"]:9} {media(t):.1f} {risco(t):5} {t["titulo"]}')
    if args.csv:
        with args.csv.open("w",encoding="utf-8-sig",newline="") as file:
            writer = csv.writer(file,delimiter=";")
            writer.writerow(("Ordem","ID","Fluxo","STRIDE","Título","Média","Risco","Status","Decisão"))
            writer.writerows((i,t["id"],t["fluxo"],t["stride"],t["titulo"],
                              f"{media(t):.1f}".replace(".",","),risco(t),t["status"],t["decisao"])
                             for i,t in enumerate(ranked,1))

if __name__ == "__main__":
    main()
