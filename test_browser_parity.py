"""Run real JavaScript via Node and compare all outputs with Python."""
import itertools,json,subprocess,unittest
from planner import ROOT,FEATURES,VALUES,load_model,recommend,score
from build_site import build
class BrowserParityTests(unittest.TestCase):
    def test_python_javascript_full_matrix(self):
        build();m=load_model();cases=[];expected=[]
        for vals in itertools.product(*(VALUES[f] for f in FEATURES)):
            f=dict(zip(FEATURES,vals))
            for unsafe,stationary in itertools.product((False,True),repeat=2):
                cases.append({'features':f,'unsafe':unsafe,'stationary':stationary})
                expected.append({'recommendation':recommend(m,f,unsafe,stationary),'scores':None if unsafe else score(m,f)})
        for feature,bad in [('time','99'),('energy','unknown'),('setting','forest'),('time',None)]:
            f=dict(time='5',energy='low',setting='doorstep');f[feature]=bad
            cases.append({'features':f,'unsafe':False,'stationary':False})
            try: recommend(m,f)
            except ValueError as e: expected.append({'error':str(e)})
        proc=subprocess.run(['node',str(ROOT/'parity_runner.mjs')],input=json.dumps(cases),capture_output=True,text=True,cwd=ROOT,check=True)
        actual=json.loads(proc.stdout)
        self.assertEqual(len(actual),112)
        def compare(a,b):
            if isinstance(a,float): self.assertAlmostEqual(a,b,places=12)
            elif isinstance(a,dict):
                self.assertEqual(set(a),set(b))
                for k in a: compare(a[k],b[k])
            elif isinstance(a,list):
                self.assertEqual(len(a),len(b))
                for x,y in zip(a,b): compare(x,y)
            else: self.assertEqual(a,b)
        for a,b in zip(expected,actual): compare(a,b)
        (ROOT/'docs').mkdir(exist_ok=True)
        (ROOT/'docs'/'browser-parity.json').write_text(json.dumps({'passed':True,'valid_context_modifier_cases':108,'invalid_cases':4,'total_cases':112,'comparison':'All recommendation fields, safety bypass, stationary constraints, explanations, ranking and raw probabilities; numeric tolerance 1e-12. Actual Node execution, not a claimed equivalence.','node_version':subprocess.check_output(['node','--version'],text=True).strip()},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':unittest.main(verbosity=2)
