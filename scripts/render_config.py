"""Generate reviewable candidates. No installs, network, source or client writes."""
import argparse,json,re,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('machine');p.add_argument('--out',required=True);a=p.parse_args()
m=json.loads(Path(a.machine).read_text(encoding='utf-8-sig'))
keys=['gateway','workspace','knowledge','skills','memory','python','workspace_id','transport']
for k in keys:
 if not isinstance(m.get(k),str) or not m[k].strip():p.error('Missing string: '+k)
for k in ['gateway','workspace','knowledge','skills','memory','python']:
 v=m[k]
 if not (v.startswith('/') or re.match(r'^[A-Za-z]:[\\/]',v)):p.error(k+' must be absolute')
 if any(c in v for c in ['\n','\r','\x00','"','%']):p.error('Unsupported launcher character in '+k)
if not re.fullmatch(r'[a-z][a-z0-9-]*',m['workspace_id']):p.error('workspace_id must be lowercase slug')
if m['workspace_id'] in {'memory','skills','gpt-knowledge'}:p.error('reserved workspace ID')
if m['transport'] not in {'stdio','http'}:p.error('transport must be stdio or http')
out=Path(a.out)
if out.exists():p.error('Output already exists; choose a fresh directory')
out.mkdir(parents=True)
def write(n,x):
 (out/n).write_text(json.dumps(x,indent=2)+'\n' if not isinstance(x,str) else x,encoding='utf-8')
ex=['.git','node_modules','dist','build','coverage','.venv','__pycache__','.pytest_cache','.env','state','eye_Databa']
def root(i,path,cl):return dict(id=i,path=path,**{'class':cl},enabled=True,index=True,hash='sha256',git=False,exclusions=ex)
w=root(m['workspace_id'],m['workspace'],'workspace');w['git']=True
k=root('gpt-knowledge',m['knowledge'],'knowledge')
s=root('skills',m['skills'],'knowledge')
h=root('memory',m['memory'],'memory');h.update(source_class='historical-memory',authority='historical',sources=[])
write('config.json',{'schema_version':2,'roots':[w,k,h,s]})
write('eye_workspace.json',{'roots':[w,k]})
for name,obj in [('memory',h),('skills',s)]:write('eye_'+name+'.json',{'schema_version':1,'kind':'eye_'+name,'root':obj})
g=m['gateway'].rstrip('/\\');py=m['python'];state=g+'/state'
def psq(x):return "'"+x.replace("'","''")+"'"
for name,script,args in [('stdio','mcp_server.py',' --stdio'),('http','http_mcp_server.py','')]:
 body="$ErrorActionPreference = 'Stop'\nSet-Location -LiteralPath "+psq(g)+"\n$env:BIRDEYE_STATE_ROOT = "+psq(state)+"\n$env:SKILLS_ROOT = "+psq(m['skills'])+"\n& "+psq(py)+' '+psq(g+'/'+script)+args+"\nexit $LASTEXITCODE\n"
 write('start-'+name+'.ps1',body)
 import shlex
 body='#!/bin/sh\nset -eu\ncd '+shlex.quote(g)+'\nexport BIRDEYE_STATE_ROOT='+shlex.quote(state)+'\nexport SKILLS_ROOT='+shlex.quote(m['skills'])+'\nexec '+shlex.quote(py)+' '+shlex.quote(g+'/'+script)+args+'\n'
 write('start-'+name+'.sh',body)
# Set client cwd through a wrapper; wrapper location must be changed after copying.
write('mcp-client.stdio.example.json',{'mcpServers':{'birdeye':{'command':'pwsh','args':['-NoLogo','-NoProfile','-File',str((out/'start-stdio.ps1').resolve())]}}})
write('mcp-client.posix.example.json',{'mcpServers':{'birdeye':{'command':'sh','args':[str((out/'start-stdio.sh').resolve())]}}})
write('REVIEW_REQUIRED.txt','Candidates only. Compare with selected source loaders. Client wrapper paths refer to this output directory; adjust if moved. Use Windows PowerShell executable instead of pwsh if that is the installed host. No config was applied.\n')
print('Generated candidates in '+str(out.resolve()))
