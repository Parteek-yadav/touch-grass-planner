"""Synthetic-only diagnostic. Context-group holdout avoids identical-input leakage."""
import json,random
from collections import Counter
from planner import ROOT,FEATURES,read_data,train,score

def evaluate():
    rows=read_data()
    contexts=sorted({tuple(row[f] for f in FEATURES) for row in rows})
    random.Random(20261010).shuffle(contexts)
    held=set(contexts[:9])
    test=[row for row in rows if tuple(row[f] for f in FEATURES) in held]
    training=[row for row in rows if tuple(row[f] for f in FEATURES) not in held]
    model=train(training)
    baseline=sorted(model['classes'],key=lambda c:(-model['classes'][c],c))[0]
    outcomes=[]
    for row in test:
        scores=score(model,row)
        prediction=sorted(scores,key=lambda c:(-scores[c],c))[0]
        outcomes.append({'features':{f:row[f] for f in FEATURES},'synthetic_label':row['activity'],'model':prediction,'majority_baseline':baseline})
    correct=sum(x['model']==x['synthetic_label'] for x in outcomes)
    base=sum(x['majority_baseline']==x['synthetic_label'] for x in outcomes)
    return {'scope':'Synthetic author-label agreement ONLY; not real-world accuracy, effectiveness, or safety. No hyperparameter tuning on this holdout.', 'split':'Seed 20261010; hold out 9 complete input contexts, train on other 18; no identical context in both sets. Same author-designed distribution remains a limitation.', 'training_rows':len(training),'held_out_rows':len(test),'held_out_contexts':len(held),'model_correct':correct,'majority_baseline_correct':base,'model_label_agreement':round(correct/len(test),4),'baseline_label_agreement':round(base/len(test),4),'production_model':'Separately trained on all 81 rows; this evaluation model is not saved over it. Scores evaluated before UI eligibility filters; baseline gets no filter either.', 'outcomes':outcomes}
if __name__=='__main__':
    report=evaluate()
    (ROOT/'docs'/'synthetic-evaluation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='outcomes'},indent=2))
