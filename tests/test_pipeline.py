"""
Automated Unit and Integration Tests for Zamp AP Flow.
Verifies all 5 scenarios, policy thresholds, duplicate prevention, and human overrides.
"""
import unittest
from starlette.testclient import TestClient
from server import app
from erp_database import db

class TestZampAPFlow(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        db.reset()

    def test_scenarios_available(self):
        res = self.client.get('/api/scenarios')
        self.assertEqual(res.status_code, 200)
        scenarios = res.json()
        self.assertEqual(len(scenarios), 5)
        ids = [s['id'] for s in scenarios]
        self.assertIn('happy_path', ids)
        self.assertIn('edge_price_variance', ids)
        self.assertIn('edge_split_billing', ids)
        self.assertIn('edge_duplicate_fraud', ids)
        self.assertIn('edge_unapproved_vendor', ids)

    def test_happy_path_auto_approved(self):
        res = self.client.post('/api/process', data={'scenario_id': 'happy_path'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['decision'], 'APPROVED')
        self.assertEqual(data['risk_level'], 'LOW')
        self.assertGreaterEqual(data['confidence_score'], 0.95)
        self.assertEqual(data['vendor_name'], 'Apex Data Systems')
        self.assertEqual(data['total_amount'], 7500.0)

    def test_edge_price_variance_flagged(self):
        res = self.client.post('/api/process', data={'scenario_id': 'edge_price_variance'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['decision'], 'FLAGGED_EXCEPTION')
        # Line item variance check
        reconciled = data['stages'][3]['details']['reconciled_lines']
        var_line = next(item for item in reconciled if item['sku'] == 'FREIGHT-EXP-01')
        self.assertGreater(var_line['variance_pct'], 3.0)

    def test_edge_split_billing_approved_and_decrements_po(self):
        initial_po = db.get_po('PO-7020')
        initial_bal = initial_po['remaining_balance']
        self.assertEqual(initial_bal, 10000.0)

        res = self.client.post('/api/process', data={'scenario_id': 'edge_split_billing'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['decision'], 'APPROVED')
        self.assertEqual(data['total_amount'], 6000.0)

        updated_po = db.get_po('PO-7020')
        self.assertEqual(updated_po['remaining_balance'], 4000.0)

    def test_edge_duplicate_fraud_rejected(self):
        res = self.client.post('/api/process', data={'scenario_id': 'edge_duplicate_fraud'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['decision'], 'REJECTED')
        self.assertEqual(data['risk_level'], 'HIGH')
        self.assertTrue(any('duplicate' in r.lower() for r in data['reasoning_points']))

    def test_edge_unapproved_vendor_rejected(self):
        res = self.client.post('/api/process', data={'scenario_id': 'edge_unapproved_vendor'})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['decision'], 'REJECTED')
        self.assertEqual(data['risk_level'], 'HIGH')
        self.assertTrue(any('not found' in r.lower() or 'compliance' in r.lower() for r in data['reasoning_points']))

    def test_missing_metadata_rejected(self):
        # Empty text / blank file
        blank_pdf = b"%PDF-1.4 empty stream"
        files = {'file': ('blank.pdf', blank_pdf, 'application/pdf')}
        res = self.client.post('/api/process', files=files)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['decision'], 'REJECTED')
        self.assertTrue(any('missing' in r.lower() for r in data['reasoning_points']))

    def test_human_override_workflow(self):
        res = self.client.post('/api/process', data={'scenario_id': 'edge_price_variance'})
        run_id = res.json()['run_id']
        
        override_res = self.client.post(f'/api/runs/{run_id}/override', json={
            'action': 'OVERRIDE_APPROVE',
            'notes': 'Approved emergency shipping variance.',
            'reviewer': 'Finance Director'
        })
        self.assertEqual(override_res.status_code, 200)
        self.assertEqual(override_res.json()['decision'], 'APPROVED_WITH_OVERRIDE')

if __name__ == '__main__':
    unittest.main()
