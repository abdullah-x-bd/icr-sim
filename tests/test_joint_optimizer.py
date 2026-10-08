"""Tests for joint traffic, agreement selection and coalition settlements."""
import unittest
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research.joint_optimizer import (
    instance,optimize,coalition_values,payoffs,bilateral_payments,
    core_violation,unconstrained_core,implementable_settlement,run_game
)

class JointICRTests(unittest.TestCase):
    def test_flow_capacity_and_costs(self):
        data=instance(20003)
        r=optimize(data)
        self.assertGreater(r['welfare'],0)
        self.assertAlmostEqual(r['welfare'],r['base_gains'].sum(),places=6)
        for i in range(4):
            self.assertAlmostEqual(r['volumes'][i,i,:].sum(),0)
        for i,j in r['active']:
            self.assertGreater(r['volumes'][i,j,:].sum(),0)
            self.assertGreater(r['fixed'][i,j],0)
        for host in range(4):
            for t in range(2):
                self.assertLessEqual(r['volumes'][:,host,t].sum(),
                                     data['capacity'][:,host,t].sum()+1e-6)

    def test_coalition_and_tariff_feasibility(self):
        for seed in [20000,20001,20002,20003,20031,20110]:
            g=run_game(seed)
            self.assertEqual(len(g['coalition_values']),16)
            self.assertAlmostEqual(g['grand_value'],g['coalition_values'][15],places=6)
            for name in ['directional','signed_credit','capped_bilateral']:
                settlement=g[name]
                self.assertTrue(settlement['core_stable'],(seed,name,settlement['violating_coalitions']))
                self.assertAlmostEqual(sum(settlement['gains']),g['grand_value'],places=5)
                self.assertTrue(all(x>=-1e-6 for x in settlement['gains']))
            self.assertTrue(g['ideal_core']['feasible'])

    def test_empty_core_is_not_silently_approved(self):
        # Three-player simple majority, with T4 a dummy. Any two of
        # T1/T2/T3 can earn one unit but the grand coalition earns one.
        value={0:0.}
        for mask in range(1,16):
            value[mask]=float((mask & 7).bit_count()>=2)
        result=unconstrained_core(value)
        self.assertFalse(result['feasible'])
        self.assertGreater(result['least_core_epsilon'],.3)
        self.assertTrue(core_violation(np.ones(4)/4,value))

    def test_no_trade(self):
        data=instance(20000)
        data['coverage'][:]=True
        coal=coalition_values(data)
        self.assertTrue(all(abs(x)<1e-8 for x in coal.values()))
        r=optimize(data)
        settle=implementable_settlement(r,coal,pairwise_bounds=True)
        self.assertTrue(settle['core_stable'])
        self.assertEqual(settle['payments'],{})
        self.assertAlmostEqual(settle['gains'].sum(),0)

if __name__=='__main__':
    unittest.main()
