"""Offline categorical Naive Bayes outdoor planner. Python 3.10+, stdlib only."""
import argparse, csv, json, math
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent
FEATURES = ('time', 'energy', 'setting')
VALUES = {'time': ('5', '15', '30'), 'energy': ('low', 'medium', 'high'), 'setting': ('doorstep', 'street', 'park')}
ACTIVITIES = {
    'pause': {'title': 'Outdoor sensory pause', 'minutes': 5, 'instruction': 'If safe, pause at an accessible outdoor spot. Notice three colors and two sounds. Sitting is fine.'},
    'observe': {'title': 'Nature noticing', 'minutes': 5, 'instruction': 'From an accessible outdoor spot, observe a plant, cloud, or bird without approaching wildlife. No plant or animal identification is required.'},
    'wander': {'title': 'Gentle accessible wander', 'minutes': 15, 'instruction': 'Choose a familiar, accessible route close to home. Walk or roll at your own pace; turn back early if needed.'},
    'explore': {'title': 'Longer park loop', 'minutes': 30, 'instruction': 'Use a familiar marked accessible park route. Walk or roll gently, stay near an exit, and skip any section that feels unsafe.'},
}
def read_data(filename=ROOT / 'data' / 'synthetic.csv'):
    with open(filename, encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows: raise ValueError('Training data cannot be empty')
    for row in rows:
        for feature in FEATURES:
            if row[feature] not in VALUES[feature]: raise ValueError('Invalid training feature: ' + feature)
        if row['activity'] not in ACTIVITIES: raise ValueError('Invalid activity label')
    return rows

def train(rows):
    classes = Counter(row['activity'] for row in rows)
    counts = {label: {f: dict(Counter(row[f] for row in rows if row['activity'] == label)) for f in FEATURES} for label in classes}
    return {'version': 1, 'provenance': 'Hand-authored synthetic preferences, not human observations', 'rows': len(rows), 'classes': dict(classes), 'counts': counts}

def validate(features):
    for f in FEATURES:
        if features.get(f) not in VALUES[f]: raise ValueError('Invalid ' + f + ': choose ' + ', '.join(VALUES[f]))

def score(model, features):
    validate(features)
    logs = {}
    for label, n in model['classes'].items():
        logp = math.log((n + 1) / (model['rows'] + len(model['classes'])))
        for f in FEATURES:
            logp += math.log((model['counts'][label][f].get(features[f], 0) + 1) / (n + len(VALUES[f])))
        logs[label] = logp
    top = max(logs.values())
    total = sum(math.exp(v - top) for v in logs.values())
    return {label: math.exp(v - top) / total for label, v in logs.items()}

def recommend(model, features, unsafe=False, accessible_only=False):
    validate(features)
    if unsafe:
        return {'status': 'stay_inside', 'title': 'Skip the outdoor plan today', 'reason': 'You marked conditions unsafe. This overrides the AI; stay inside and reassess later.', 'model_used': False}
    probabilities = score(model, features)
    eligible = [label for label in probabilities if ACTIVITIES[label]['minutes'] <= int(features['time']) and (label != 'explore' or features['setting'] == 'park') and (not accessible_only or label in ('pause', 'observe'))]
    if not eligible: raise ValueError('No eligible activities in model')
    ranked = sorted(eligible, key=lambda label: (-probabilities[label], label))
    chosen = ranked[0]
    p = probabilities[chosen]
    margin = p - probabilities[ranked[1]] if len(ranked) > 1 else p
    n = model['classes'][chosen]
    evidence = [{'feature': f, 'value': features[f], 'synthetic_matches_for_label': model['counts'][chosen][f].get(features[f], 0), 'label_rows': n} for f in FEATURES]
    return {'status': 'plan', 'activity': chosen, **ACTIVITIES[chosen], 'model_used': True,
        'model_score': round(p, 4), 'eligible_margin': round(margin, 4), 'ranking_note': 'Close call: eligible choices scored similarly.' if margin < 0.1 else 'A preference ranking, not a safety or usefulness guarantee.', 'evidence': evidence, 'uncertainty': 'This synthetic-model score is not a calibrated probability of usefulness or safety.',
        'reason': 'The learned model ranked this highest among eligible plans using time=' + features['time'] + ', energy=' + features['energy'] + ', setting=' + features['setting'] + '.',
        'constraints': 'Time and park requirements are hard filters. Safety is self-reported; there is no live weather or route check.',
        'alternatives': [{'activity': x, 'model_score': round(probabilities[x], 4)} for x in ranked[1:]],
        'reminder': 'Check weather, air quality, daylight and local access yourself. Avoid traffic, heat, storms and unsafe areas. No exercise or medical benefit is promised.'}

def load_model(filename=ROOT / 'model.json'):
    with open(filename, encoding='utf-8') as stream: return json.load(stream)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    training = sub.add_parser('train', help='Train from labeled synthetic data')
    training.add_argument('--data', type=Path, default=ROOT / 'data' / 'synthetic.csv')
    predict = sub.add_parser('predict', help='Recommend using the saved local model')
    for f in FEATURES: predict.add_argument('--' + f, required=True, choices=VALUES[f])
    predict.add_argument('--unsafe', action='store_true', help='Override AI and stay indoors')
    predict.add_argument('--stationary-only', action='store_true', help='Only sitting/stationary outdoor options')
    args = parser.parse_args()
    if args.command == 'train':
        model = train(read_data(args.data))
        (ROOT / 'model.json').write_text(json.dumps(model, indent=2) + '\n', encoding='utf-8', newline='\n')
        print('Trained local synthetic model on', model['rows'], 'rows; labels:', ', '.join(sorted(model['classes'])))
    else:
        print(json.dumps(recommend(load_model(), {f: getattr(args, f) for f in FEATURES}, args.unsafe, args.stationary_only), indent=2))
if __name__ == '__main__': main()
