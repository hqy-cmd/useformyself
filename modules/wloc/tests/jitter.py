"""Deterministic full-script jitter checks; synthetic data, no location changes."""
from pathlib import Path
import json, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'wloc.js').read_text()
js='const source='+json.dumps(source)+';\n'+r'''
const run=new Function('$request','$argument','$done','console','Math',source);
// Independent minimal protobuf reader, including signed int64 coordinates.
function parse(a){let p=0,out=[];function v(){let n=0n,b=0n;for(;;){const x=a[p++];n|=BigInt(x&127)<<b;if(x<128)return n;b+=7n;}}
while(p<a.length){const k=Number(v()),id=k>>3,w=k&7;let value;if(w===0)value=BigInt.asIntN(64,v());else if(w===2){const n=Number(v());value=a.slice(p,p+n);p+=n;}else throw Error('wire');out.push([id,value]);}return out;}
const wifi=[18,5,10,3,102,97,107],pb=[...wifi,...wifi];
const body=new Uint8Array([0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,pb.length,...pb]);
function sample(lat,lon,radius,u,v){let result,calls=0;const math=Object.create(Math);let i=0;math.random=()=>[u,v][i++];
run({method:'POST',url:'https://gs-loc.apple.com/clls/wloc',headers:{},body},`enabled=true&lat=${lat}&lon=${lon}&altitude=0&hacc=10&vacc=10${radius===null?'':'&radiusKm='+radius}`,x=>{result=x;calls++;},{log:()=>{}},math);
if(calls!==1)throw Error('done count');if(!result.response)return null;
const points=parse(result.response.body.slice(10)).filter(x=>x[0]===2).map(x=>{const loc=parse(x[1]).find(x=>x[0]===2)[1];const f=parse(loc);return [Number(f.find(x=>x[0]===1)[1])/1e8,Number(f.find(x=>x[0]===2)[1])/1e8];});
if(JSON.stringify(points[0])!==JSON.stringify(points[1]))throw Error('WiFi disagreement');return points[0];}
function distance(a,b){const r=Math.PI/180,dlat=(b[0]-a[0])*r,dlon=(b[1]-a[1])*r;
const h=Math.sin(dlat/2)**2+Math.cos(a[0]*r)*Math.cos(b[0]*r)*Math.sin(dlon/2)**2;
return 6371.0088*2*Math.asin(Math.sqrt(Math.min(1,h)));}
let count=0;
for(const center of [[1.29167,103.85],[90,180],[-90,-180],[0,179.9999],[-33.5,-70.25]]){
for(const radius of [0.001,1,1000])for(let i=0;i<100;i++){
const u=(i+.5)/100,p=sample(...center,radius,u,(i*.61803398875)%1),d=distance(center,p);
if(!p.every(Number.isFinite)||Math.abs(p[0])>90||Math.abs(p[1])>180||d>radius+0.000002)throw Error('range');
// Inverse spherical cap area CDF should recover the chosen uniform variate.
const area=(Math.sin(d/6371.0088/2)/Math.sin(radius/6371.0088/2))**2;
if(Math.abs(area-u)>0.003)throw Error('area distribution');count++;
}
for(const radius of [null,0]){if(JSON.stringify(sample(...center,radius,.9,.4))!==JSON.stringify(center))throw Error('fixed regression');count++;}
for(const u of [0,1]){const p=sample(...center,1,u,0);if(Math.abs(distance(center,p)-u)>0.000002)throw Error('boundary');count++;}
}
for(const bad of ['-1','1001','NaN','Infinity','oops','']){if(sample(0,0,bad,.5,.5)!==null)throw Error('invalid radius');count++;}
console.log('PASS '+count+' jitter integration cases');if(typeof $done==='function')$done({});
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'jitter.js';p.write_text(js)
 subprocess.run(['node',str(p)],check=True)
 result=subprocess.run(['/Applications/Surge.app/Contents/Applications/surge-cli','script','evaluate',str(p),'generic','20'],capture_output=True,text=True)
 print(result.stdout);print(result.stderr)
 if result.returncode or 'PASS 1526' not in result.stdout:raise SystemExit('Surge jitter tests failed')
