import unittest
from planner import *
class PlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.model = train(read_data())
    def test_dataset_size(self): self.assertEqual(self.model['rows'],81)
    def test_labels(self): self.assertEqual(set(self.model['classes']),set(ACTIVITIES))
    def test_normalization(self): self.assertAlmostEqual(sum(score(self.model,dict(time='15',energy='medium',setting='park')).values()),1)
    def test_deterministic(self): self.assertEqual(train(read_data()),train(read_data()))
    def test_invalid_input(self):
        with self.assertRaises(ValueError): score(self.model,dict(time='100',energy='low',setting='park'))
    def test_unsafe_override(self):
        p=recommend(self.model,dict(time='30',energy='high',setting='park'),unsafe=True)
        self.assertEqual(p['status'],'stay_inside'); self.assertFalse(p['model_used'])
    def test_all_contexts_time_limit(self):
        for t in VALUES['time']:
            for e in VALUES['energy']:
                for s in VALUES['setting']:
                    p=recommend(self.model,dict(time=t,energy=e,setting=s))
                    self.assertLessEqual(p['minutes'],int(t))
    def test_park_filter(self):
        for setting in ('street','doorstep'):
            p=recommend(self.model,dict(time='30',energy='high',setting=setting))
            self.assertNotEqual(p['activity'],'explore')
            self.assertNotIn('explore',[x['activity'] for x in p['alternatives']])
    def test_stationary_only(self):
        p=recommend(self.model,dict(time='30',energy='high',setting='park'),accessible_only=True)
        self.assertIn(p['activity'],('pause','observe'))
    def test_scores_respond_to_energy(self):
        a=score(self.model,dict(time='30',energy='low',setting='park'))
        b=score(self.model,dict(time='30',energy='high',setting='park'))
        self.assertNotEqual(a,b)
        self.assertGreater(b['explore'],a['explore'])
    def test_retraining_changes_actual_recommendation(self):
        f=dict(time='5',energy='low',setting='doorstep')
        a=recommend(train([{**f,'activity':'pause'}]*6 + [{**f,'activity':'observe'}]),f)
        b=recommend(train([{**f,'activity':'observe'}]*6 + [{**f,'activity':'pause'}]),f)
        self.assertEqual(a['activity'],'pause');self.assertEqual(b['activity'],'observe')
    def test_uncertainty_disclosed(self):
        p=recommend(self.model,dict(time='15',energy='medium',setting='street'))
        self.assertIn('not a calibrated',p['uncertainty']);self.assertTrue(p['model_used'])
class ExplanationTests(unittest.TestCase):
    def test_evidence_matches_saved_counts(self):
        m=train(read_data()); f=dict(time='5',energy='low',setting='doorstep'); result=recommend(m,f)
        self.assertEqual(len(result['evidence']),3)
        for row in result['evidence']: self.assertEqual(row['synthetic_matches_for_label'],m['counts'][result['activity']][row['feature']].get(row['value'],0))
        self.assertGreaterEqual(result['eligible_margin'],0)
    def test_close_call_disclosed(self):
        result=recommend(train(read_data()),dict(time='5',energy='low',setting='doorstep'))
        self.assertIn('Close call',result['ranking_note'])
    def test_context_holdout(self):
        from evaluate import evaluate
        report=evaluate()
        self.assertEqual(report['training_rows'],54); self.assertEqual(report['held_out_rows'],27)
        self.assertIn('not real-world',report['scope'])
if __name__=='__main__': unittest.main(verbosity=2)
