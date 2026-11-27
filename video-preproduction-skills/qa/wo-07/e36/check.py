"""Bind independently produced EX-02 design responses to a throwaway ledger."""
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

package = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent

def run(tool, root, *args):
    return subprocess.run([sys.executable, str(package/'scripts'/f'{tool}.py'), '--project', str(root), *args], capture_output=True, text=True)

def result(root, name, expected):
    proc=run('index_lint',root,'--stage','bible','--json')
    assert proc.returncode==expected, proc.stderr
    findings=json.loads(proc.stdout)
    (out/f'{name}.json').write_text(proc.stdout)
    return findings

with TemporaryDirectory(prefix='cp2-e36-') as tmp:
    root=Path(tmp)
    source=package/'evals/design/fixtures/SCR-ex02.md'
    (root/'SCR.md').write_bytes(source.read_bytes())
    assert run('ledger',root,'register','SCR','SCR.md','1').returncode==0
    entries=[]
    files={'CHR-01':'e32-retry.md','CHR-02':'e32-retry.md','WRD-01a':'e33-trial.md','WRD-02a':'e33-trial.md','LOC-01':'e34-trial.md','SET-01':'e34-trial.md','ENV-01':'e34-trial.md'}
    for ident,file in files.items():
        text=(out.parent/file).read_text()
        headings=list(re.finditer(r'^#{1,2} .*$',text,re.M))
        start=next(i for i,m in enumerate(headings) if 'tmp:'+ident in m.group())
        depth=len(headings[start].group().split(' ',1)[0]); end=next((m.start() for m in headings[start+1:] if len(m.group().split(' ',1)[0])<=depth),len(text)); name=ident+'.md'; (root/name).write_text(text[headings[start].start():end])
        proc=run('ledger',root,'register',ident,name,'1','--consumes','SCR@v1'); assert proc.returncode==0, proc.stderr
        entries.append({'kind':ident.split('-')[0],'entity':ident,'ref':ident+'@v1'})
    # The production design has one shared Props section; bind exact rows, not newly invented design text.
    design=(out.parent/'e34-trial.md').read_text()
    for i, row in enumerate(re.findall(r'^\|[^\n]*tmp:PRP-\d+[^\n]*$', design,re.M),1):
        ident=re.search(r'PRP-\d+',row).group(); name=ident+'.md'; (root/name).write_text(row+'\n'); proc=run('ledger',root,'register',ident,name,'1','--consumes','SCR@v1'); assert proc.returncode==0, proc.stderr
        entries.append({'kind':'PRP','entity':ident,'ref':ident+'@v1'})
    assert any(e['kind']=='PRP' for e in entries)
    inventory=root/'bible-inventory.json'; payload={'screenplay':'SCR@v1','entries':entries}; inventory.write_text(json.dumps(payload))
    assert result(root,'baseline',0)==[]
    (root/'SCR-revised.md').write_text(source.read_text()+'\n동생이 황동 열쇠를 꺼내 계산대 위에 놓는다.\n')
    proc=run('ledger',root,'register','SCR','SCR-revised.md','2'); assert proc.returncode==0,proc.stderr
    for entry in entries:
        ident=entry['entity']; proc=run('ledger',root,'register',ident,ident+'.md','2','--consumes','SCR@v2'); assert proc.returncode==0,proc.stderr; entry['ref']=ident+'@v2'
    payload['screenplay']='SCR@v2';entries.append({'kind':'PRP','entity':'brass-key','ref':None});inventory.write_text(json.dumps(payload))
    findings=result(root,'missing-prop',1)
    assert [f['code'] for f in findings]==['IX01'] and findings[0]['target']=='brass-key',findings
print('CK-B baseline PASS; added unassigned brass key returns IX01 as expected')
