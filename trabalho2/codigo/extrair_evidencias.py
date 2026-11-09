"""Extrai metadados e campos seguros dos registros HTTP históricos da M1."""
import argparse
import base64
import json
from pathlib import Path

from validar_modelo import ROOT

def exchange(m1, folder, n):
    base = m1/"evidencias"/folder/"http"
    req = (base/f"{n:02}-request.http").read_text(encoding="utf-8")
    res = (base/f"{n:02}-response.http").read_text(encoding="utf-8")
    req_first = req.splitlines()[0]
    if "?" in req_first:
        req_first = req_first.split("?",1)[0]+"?email=[omitido]"
    head, _, body = res.partition("\n\n")
    headers = dict(line.split(": ",1) for line in head.splitlines()[1:] if ": " in line)
    data = {"arquivo": f"{n:02}", "requisicao":req_first, "resposta":head.splitlines()[0]}
    for h in ("X-RateLimit-Limit","X-RateLimit-Remaining"):
        if h in headers:
            data[h] = headers[h]
    return data, body

def decoded(part):
    padded = part+"="*(-len(part)%4)
    return json.loads(base64.urlsafe_b64decode(padded))

def extract(m1):
    tokens = []
    for label,folder,n in (("V1","V1-sqli-login",1),("V2","V2-hash-senha-jwt",2)):
        meta, raw=exchange(m1,folder,n)
        jwt=json.loads(raw)["authentication"]["token"]
        h,p,_=jwt.split(".")
        claims=decoded(p)
        tokens.append({
            "achado":label,**meta,"alg":decoded(h)["alg"],"claims":list(claims),
            "password_presente":"password" in claims["data"]
        })
    logins = [exchange(m1,"V6-bruteforce-login",n)[0] for n in range(2,18)]
    reset = [exchange(m1,"V7-reset-senha-pergunta-seguranca",n)[0] for n in range(1,11)]
    _,body=exchange(m1,"V7-reset-senha-pergunta-seguranca",9)
    reset_exposes_hash = "password" in json.loads(body)["user"]
    v3_folder="V3-idor-cesta"
    _,body_a=exchange(m1,v3_folder,2)
    _,body_b=exchange(m1,v3_folder,4)
    cross,raw=exchange(m1,v3_folder,6)
    a=json.loads(body_a)["authentication"]["bid"]
    b=json.loads(body_b)["authentication"]["bid"]
    read=json.loads(raw)["data"]["id"]
    cross["cesta_conta_a"],cross["cesta_conta_b"],cross["cesta_lida"]=a,b,read
    return {"jwt":tokens,"login":logins,"reset":reset,"reset_expoe_hash":reset_exposes_hash,"cesta":cross}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("m1",type=Path,help="Diretório da cópia local do Git da M1.")
    parser.add_argument("--saida",type=Path,default=ROOT/"evidencias"/"extratos_m1.json")
    args=parser.parse_args()
    args.saida.write_text(json.dumps(extract(args.m1),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(args.saida)

if __name__=="__main__":
    main()
