import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd
import numpy as np
from src.data import TRANSACTION_COLUMNS, scan_transactions, build_base
from src.common import save_frame, load_frame
from src.features import add_features, model_inputs
from src.strategy import strategy_frame, select_policy

class PipelineTests(unittest.TestCase):
    def fixture(self, root):
        # a latest record duplicated across chunks; b has a distinct same-day tie;
        # c only has a future transaction; d is a known zero-price March plan;
        # e has a post-cutoff registration and a valid pre-cutoff billing record.
        rows = [
            ['a',41,30,149,149,1,20170101,20170201,0],
            ['a',41,30,149,149,1,20170215,20170315,0],
            ['b',36,30,180,180,1,20170215,20170315,0],
            ['a',41,30,149,149,1,20170215,20170315,0],
            ['b',36,30,180,180,1,20170215,20170316,1],
            ['c',41,30,149,149,1,20170301,20170401,0],
            ['a',41,30,149,149,1,20170301,20170401,0],
            ['d',38,30,0,0,0,20170130,20170301,0],
            ['e',38,30,100,90,0,20170228,20170330,0]]
        pd.DataFrame(rows,columns=TRANSACTION_COLUMNS).to_csv(root/'transactions.csv',index=False)
        pd.DataFrame({'msno':list('abcde'),'is_churn':[0,1,1,1,0]}).to_csv(root/'train_v2.csv',index=False)
        pd.DataFrame({'msno':list('abce'),'city':[1,2,1,1], 'bd':[0,25,40,200],
          'gender':[None,'female','male',None],'registered_via':[7,9,7,7],
          'registration_init_time':[20100101,20100101,20100101,20170301]}).to_csv(root/'members_v3.csv',index=False)
        return {'cutoff':'2017-02-28','expiry_start':'2017-03-01','expiry_end':'2017-03-31','chunk_size':2}

    def test_cutoff_ties_duplicates_and_chunk_invariance(self):
        with TemporaryDirectory() as td:
            root=Path(td);config=self.fixture(root)
            a, ties, h, audit=scan_transactions(root/'transactions.csv',set('abcde'),pd.Timestamp(config['cutoff']),2)
            a2, ties2, h2, _=scan_transactions(root/'transactions.csv',set('abcde'),pd.Timestamp(config['cutoff']),100)
            self.assertEqual(set(ties),{'b'})
            self.assertEqual(audit['latest_identical_rows_removed'],1)
            self.assertEqual(h.loc['a','history_transaction_count'],3)
            self.assertEqual(h.loc['a','transaction_count_30d'],2)
            self.assertEqual(h.loc['d','transaction_count_30d'],1)
            self.assertNotIn('c',h.index)
            pd.testing.assert_frame_equal(a.sort_values('msno').reset_index(drop=True),a2.sort_values('msno').reset_index(drop=True))
            pd.testing.assert_frame_equal(h.sort_index(),h2.sort_index())

    def test_cleaning_roundtrip_and_allowlist(self):
        with TemporaryDirectory() as td:
            root=Path(td);config=self.fixture(root)
            base,audit=build_base(root,config)
            self.assertEqual(base.loc[base.campaign_eligible,'msno'].tolist(),['a','d','e'])
            self.assertTrue(base.loc[base.msno.eq('d'),'member_record_missing'].iloc[0])
            self.assertTrue(pd.isna(base.loc[base.msno.eq('e'),'tenure_days'].iloc[0]))
            campaign=add_features(base.loc[base.campaign_eligible],pd.Timestamp(config['cutoff']))
            campaign['churned_revenue_30d_proxy']=123
            X,y=model_inputs(campaign)
            self.assertEqual(X.shape,(3,21))
            self.assertNotIn('is_churn',X)
            self.assertNotIn('churned_revenue_30d_proxy',X)
            save_frame(campaign,root/'checkpoint.csv.gz')
            loaded=load_frame(root/'checkpoint.csv.gz')
            X2,y2=model_inputs(loaded)
            pd.testing.assert_frame_equal(X,X2)
            pd.testing.assert_series_equal(y,y2)

    def test_policy_ignores_outcomes_and_handles_unknown_value(self):
        raw=pd.DataFrame({'msno':list('abcd'),'is_churn':[0,1,0,1],
            'revenue_30d_proxy':[100,100,0,np.nan],
            'predicted_churn_probability':[.8,.5,.9,.9]})
        frame=strategy_frame(raw)
        selected=select_policy(frame,capacity_fraction=1,save_rate=.1,contact_cost=5)
        self.assertEqual(selected.msno.tolist(),['a']) # exactly break-even b excluded
        raw['is_churn']=1-raw.is_churn
        changed=select_policy(strategy_frame(raw),capacity_fraction=1,save_rate=.1,contact_cost=5)
        self.assertEqual(selected.msno.tolist(),changed.msno.tolist())
        self.assertIn('c',frame.msno.values) # known zero retained
        self.assertNotIn('d',frame.msno.values) # unknown excluded

if __name__=='__main__': unittest.main()
