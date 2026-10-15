from pathlib import Path
import json,random,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
# Independently encoded protocol fixtures, no captured location data.
def vi(n):
 n&=(1<<64)-1; out=[]
 while n>127:out.append((n&127)|128);n>>=7
 return bytes(out+[n])
def f(i,b):return vi(i*8+2)+vi(len(b))+b
def integer(i,n):return vi(i*8)+vi(n)
def arpc(pb):return b'\0\1'+b'\0\0'*3+(1).to_bytes(4,'big')+len(pb).to_bytes(4,'big')+pb
random.seed(20261015)
v=[]
for i in range(512):
 lat=random.randint(-9000000000,9000000000);lon=random.randint(-18000000000,18000000000)
 if i<5:lat,lon=[(0,0),(9000000000,18000000000),(-9000000000,-18000000000),(1,-1),(-1,1)][i]
 altitude=random.randint(-12000,100000);h=random.randint(0,1000000);acc=random.randint(0,1000000)
 loc=b''.join(integer(k,x) for k,x in [(1,lat),(2,lon),(3,h),(4,3),(5,altitude),(6,acc),(11,63),(12,467)])
 wifi=f(1,b'02:00:00:00:00:01')+integer(99,-1)
 n=[1,2,20,100][i%4]; unknown=f(103,b'preserved')
 body=arpc(f(2,wifi)*n+integer(3,4)+integer(4,6)+f(33,b'')+unknown)
 pb=f(2,wifi+f(2,loc))*n+unknown
 expected=(bytes([0,1,0,0,0,1,0,0])+len(pb).to_bytes(2,'big')+pb).hex()
 arg=f'enabled=true&lat={lat/1e8:.8f}&lon={lon/1e8:.8f}&altitude={altitude}&hacc={h}&vacc={acc}'
 v.append({'body':list(body),'arg':arg,'expected':expected})
for i in range(256):
 t=v[i];cut=random.randrange(len(t['body']));v.append({'body':t['body'][:cut],'arg':t['arg'],'expected':None})
source=(ROOT/'wloc.js').read_text()
harness='const vectors='+json.dumps(v)+';const source='+json.dumps(source)+''';
let ok=0;
const run=new Function('$request','$argument','$done','console',source);
for(const t of vectors){let r,c=0; run({method:'POST',url:'https://gs-loc.apple.com/clls/wloc',headers:{},body:new Uint8Array(t.body)},t.arg,x=>{r=x;c++},{log:()=>{}});
const actual=r.response?Array.from(r.response.body).map(x=>x.toString(16).padStart(2,'0')).join(''):null;
if(c!==1||actual!==t.expected)throw Error('case '+ok+' failed');ok++;}
console.log('PASS '+ok+' seeded independent coordinate/size/truncation cases');
if(typeof $done==='function')$done({});
'''
with tempfile.TemporaryDirectory() as d:
 path=Path(d)/'stress.js';path.write_text(harness)
 subprocess.run(['node',str(path)],check=True)
 result=subprocess.run(['/Applications/Surge.app/Contents/Applications/surge-cli','script','evaluate',str(path),'generic','20'],text=True,capture_output=True)
 print(result.stdout);print(result.stderr)
 if result.returncode or 'PASS 768' not in result.stdout:raise SystemExit('Surge runtime verification failed')
