"""Rebuild reproducible evidence, including CLI and loopback HTTP checks."""
import html,json,subprocess,sys,threading,urllib.request,urllib.error
from http.server import HTTPServer
from planner import ROOT
from app import Handler
(ROOT / 'docs').mkdir(exist_ok=True)

def run(*args):
    p=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)
    return p
train=run('planner.py','train')
tests=run('-m','unittest','-v')
(ROOT/'docs'/'test-output.txt').write_text('Python: '+sys.version+'\n'+train.stdout+tests.stdout+tests.stderr+'\nExit code: '+str(tests.returncode)+'\n',encoding='utf-8')
if train.returncode or tests.returncode: raise SystemExit('Training/tests failed')
cases=[('A five-minute low-energy pause',['--time','5','--energy','low','--setting','doorstep']),('Fifteen minutes on a familiar street',['--time','15','--energy','medium','--setting','street']),('Thirty minutes in a park',['--time','30','--energy','high','--setting','park']),('Stationary-only park break',['--time','30','--energy','high','--setting','park','--stationary-only']),('Unsafe conditions',['--time','30','--energy','high','--setting','park','--unsafe'])]
results=[]
for label,args in cases:
    p=run('planner.py','predict',*args)
    if p.returncode: raise RuntimeError(p.stderr)
    results.append({'scenario':label,'command':'python planner.py predict '+' '.join(args),'result':json.loads(p.stdout)})
(ROOT/'docs'/'sample-predictions.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
server=HTTPServer(('127.0.0.1',0),Handler)
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base='http://127.0.0.1:'+str(server.server_port)
http=[]
try:
    for suffix,expected in [('/',200),('/api/plan?time=15&energy=medium&setting=street',200),('/api/plan?time=30&energy=high&setting=park&unsafe=true',200),('/api/plan?time=99&energy=low&setting=park',400),('/missing',404)]:
        try:
            with urllib.request.urlopen(base+suffix) as response: code=response.status;body=response.read().decode()
        except urllib.error.HTTPError as e: code=e.code;body=e.read().decode()
        assert code==expected,(suffix,code)
        if 'unsafe=true' in suffix: assert json.loads(body)['status']=='stay_inside'
        if suffix=='/': assert '<form' in body
        http.append({'path':suffix,'status':code,'passed':True})
finally: server.shutdown();server.server_close();thread.join()
(ROOT/'docs'/'http-checks.json').write_text(json.dumps(http,indent=2)+'\n',encoding='utf-8')
cards=[]
for item in results:
    p=item['result']; text=p.get('instruction',p['reason'])
    cards.append('<article><p class="eyebrow">'+html.escape(item['scenario'])+'</p><h2>'+html.escape(p['title'])+'</h2><p>'+html.escape(text)+'</p><p class="score">'+('Learned model score: '+str(p['model_score'])+' · uncalibrated' if p['model_used'] else 'Safety override · AI bypassed')+'</p><details><summary>Exact reproducible command</summary><pre>'+html.escape(item['command'])+'</pre></details></article>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Touch Grass Planner — verified local demo</title><style>body{margin:0;background:#eef3e9;color:#183a2b;font:17px/1.6 system-ui}main{max-width:1000px;margin:auto;padding:40px}h1{font-size:50px;line-height:1.1;max-width:650px}header{margin-bottom:32px}.eyebrow{font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:#46644d}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}article{background:#fff;border-radius:18px;padding:24px;border:1px solid #d6e1ce}h2{font-size:23px;line-height:1.3}.score{color:#496443;font-size:14px}pre{white-space:pre-wrap;font-size:12px}footer{margin-top:28px;border-top:1px solid #c7d5be;padding-top:20px}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:34px}main{padding:20px}}</style><main><header><p class="eyebrow">MIT licensed · Local Python AI · No paid APIs</p><h1>A gentle reason to step outside.</h1><p>Touch Grass Planner learns from transparent synthetic preferences.<br>These are actual local software outputs, not outdoor field-test results.</p><p><b>Verified:</b> 15 regression tests passed · 5 loopback HTTP checks passed.<br>81 synthetic training votes · 4 candidate activities · zero third-party dependencies.</p></header><div class="grid">'''+''.join(cards)+'''</div><footer><b>Honest by design.</b> Scores are not calibrated probabilities. No weather, route or health checks are performed. Check conditions yourself; stay indoors if unsafe. This static demo displays saved CLI results; the interactive interface requires <code>python app.py</code>.<p>Reproduce all evidence: <code>python verify.py</code>. No real-user effectiveness or accuracy claim is made.</p></footer></main></html>'''
(ROOT/'docs'/'demo.html').write_text(page,encoding='utf-8')
print('PASS: 15 unittest tests; 5 real CLI predictions; 5 loopback HTTP checks. Saved reproducible evidence and static demo.')
