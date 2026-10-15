"""Independent Python wire encoder + Node and real Surge JS runtime checks.
Only synthetic BSSIDs; no network requests or location changes.
"""
from pathlib import Path
import json, subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]

def vi(n):
    n &= (1 << 64)-1
    b = bytearray()
    while n > 127:
        b.append((n & 127)|128); n >>= 7
    b.append(n)
    return bytes(b)

def field(i, value):
    return vi(i*8+2)+vi(len(value))+value

def integer(i, n): return vi(i*8)+vi(n)
def arpc(pb):
    return b'\x00\x01'+b''.join(len(s).to_bytes(2,'big')+s for s in [b'en_US', b'test', b'27.0.1'])+b'\x00\x00\x00\x01'+len(pb).to_bytes(4,'big')+pb

def envelope(pb): return bytes([0,1,0,0,0,1,0,0])+len(pb).to_bytes(2,'big')+pb
extra = field(100,b'unknown')
wifi = field(1,b'02:00:00:00:00:01')+field(2,integer(1,123))+integer(9,42)
pb = field(2,wifi)+integer(3,2)+integer(4,4)+field(33,b'')+extra
args = 'enabled=true&lat=-33.5&lon=-70.25&altitude=-5.5&hacc=10&vacc=20'
loc = b''.join(integer(k,v) for k,v in [(1,-3350000000),(2,-7025000000),(3,10),(4,3),(5,-6),(6,20),(11,63),(12,467)])
new_wifi = field(1,b'02:00:00:00:00:01')+integer(9,42)+field(2,loc)
expected = envelope(field(2,new_wifi)+extra)
vectors=[]
def add(name, body=None, argument=args, expected_hex=None, **request):
    vectors.append(dict(name=name, body=list(arpc(pb) if body is None else body), argument=argument, expected=expected_hex, request=request))
add('negative int64 + unknown fields + removal', expected_hex=expected.hex())
add('two wifi devices', arpc(field(2,wifi)*2), expected_hex=envelope(field(2,new_wifi)*2).hex())
add('disabled',argument=args.replace('true','false'))
add('unset coordinate',argument=args.replace('-33.5','UNSET'))
add('out of range',argument=args.replace('-33.5','91'))
add('fractional accuracy',argument=args.replace('hacc=10','hacc=1.5'))
add('wrong host',url='https://example.com/clls/wloc')
add('host suffix',url='https://gs-loc.apple.com.evil.test/clls/wloc')
add('wrong path',url='https://gs-loc.apple.com/clls/wloc/other')
add('wrong method',method='GET')
add('compressed request',headers={'Content-Encoding':'gzip'})
add('query and explicit port',url='https://gs-loc-cn.apple.com:443/clls/wloc?x=1',expected_hex=expected.hex())
add('empty body',b'')
add('truncated ARPC',arpc(pb)[:-1])
add('trailing ARPC data',arpc(pb)+b'X')
add('bad protobuf length',arpc(b'\x12\xff\xff\x7f'))
add('no wifi',arpc(extra))
add('unsupported group',arpc(b'\x0b'))
add('response length overflow',arpc(field(2,wifi)*1800))
add('64-bit unknown preserved',arpc(field(2,wifi)+integer(99,-1)),expected_hex=envelope(field(2,new_wifi)+integer(99,-1)).hex())
source=(ROOT/'wloc.js').read_text()
harness='const vectors='+json.dumps(vectors)+';\nconst source='+json.dumps(source)+';\n'+'''
let passed=0;
for (const t of vectors) {
  const req=Object.assign({url:'https://gs-loc.apple.com/clls/wloc',method:'POST',headers:{},body:new Uint8Array(t.body)},t.request);
  let result, calls=0;
  new Function('$request','$argument','$done',source)(req,t.argument,r=>{result=r;calls++;});
  if(calls!==1) throw Error(t.name+': done count');
  const hex=result.response ? Array.from(result.response.body).map(x=>x.toString(16).padStart(2,'0')).join('') : null;
  if(hex!==t.expected) throw Error(t.name+': response mismatch');
  passed++;
}
console.log('PASS '+passed+' independent protocol/runtime cases');
if(typeof $done==='function') $done({});
'''
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'wloc-test.js';path.write_text(harness)
    subprocess.run(['node',str(path)],check=True)
    result=subprocess.run(['/Applications/Surge.app/Contents/Applications/surge-cli','script','evaluate',str(path),'generic','10'],text=True,capture_output=True)
    print(result.stdout);print(result.stderr)
    if result.returncode or 'PASS 20' not in result.stdout: raise SystemExit('Surge runtime verification failed')
