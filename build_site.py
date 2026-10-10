"""Bundle Python's actual learned model and activity definitions for static inference."""
import json
from planner import ROOT,load_model,ACTIVITIES,FEATURES,VALUES

def build():
    site=ROOT/'site';site.mkdir(exist_ok=True)
    data={'model':load_model(),'activities':ACTIVITIES,'features':FEATURES,'values':VALUES}
    (site/'model-data.mjs').write_text('export const DATA = '+json.dumps(data,indent=2)+';\n',encoding='utf-8',newline='\n')
    return data
if __name__=='__main__':
    build();print('Bundled actual Python model and definitions for static browser inference.')
