import unittest
import copy
from engine import PropagationEngine

class TestPropagationEngine(unittest.TestCase):
    def setUp(self):
        # Build comprehensive Edge Cases Graph payload
        self.payload = {
            "execution_id": "test_exec_001",
            "tasks": [
                # Edge: Deep Chain (5+ levels): C1->C2->C3->C4->C5->C6
                {"task_id": "C1", "depends_on": []},
                {"task_id": "C2", "depends_on": ["C1"]},
                {"task_id": "C3", "depends_on": ["C2"]},
                {"task_id": "C4", "depends_on": ["C3"]},
                {"task_id": "C5", "depends_on": ["C4"]},
                {"task_id": "C6", "depends_on": ["C5"]},
                
                # Edge: Branching (one -> many): B_Root -> B1, B2, B3
                {"task_id": "B_Root", "depends_on": []},
                {"task_id": "B1", "depends_on": ["B_Root"]},
                {"task_id": "B2", "depends_on": ["B_Root"]},
                {"task_id": "B3", "depends_on": ["B_Root"]},
                
                # Edge: Merging (many -> one): M1, M2, M3 -> M_Target
                {"task_id": "M1", "depends_on": []},
                {"task_id": "M2", "depends_on": []},
                {"task_id": "M3", "depends_on": []},
                {"task_id": "M_Target", "depends_on": ["M1", "M2", "M3"]},
                
                # Edge: Disconnected Components
                # Group D: D1->D2
                {"task_id": "D1", "depends_on": []},
                {"task_id": "D2", "depends_on": ["D1"]},
                
                # Edge: Invalid Nodes in chain mapping
                {"task_id": "IV1", "depends_on": ["MISSING_X_1", "MISSING_X_2"]},
                {"task_id": "IV2", "depends_on": ["IV1"]},
                
                # Edge: Isolated nodes
                {"task_id": "ISO_1", "depends_on": []},
                {"task_id": "ISO_2", "depends_on": []}
            ],
            "constraint_results": [
                {"task_id": "C3", "is_valid": False}, # Example of blocked logic lookup
                {"task_id": "IV1", "is_valid": False}
            ]
        }
        
    def test_strict_output_contract(self):
        engine = PropagationEngine(self.payload)
        out = engine.compute_all_propagations()
        
        self.assertEqual(out["execution_id"], "test_exec_001")
        self.assertIn("results", out)
        self.assertIn("summary", out)
        
        # Verify schema
        res_0 = out["results"][0]
        self.assertIn("task_id", res_0)
        self.assertIn("affected_tasks", res_0)
        self.assertIn("impact_score", res_0)
        self.assertIn("propagation_depth", res_0)

    def test_edge_cases(self):
        engine = PropagationEngine(self.payload)
        out = engine.compute_all_propagations()
        
        # Helper to find a specific task result
        def get_res(tid):
            for r in out["results"]:
                if r["task_id"] == tid:
                    return r
            return None
            
        # 1. Deep Chain Validation
        c1 = get_res("C1")
        self.assertEqual(c1["affected_tasks"], ["C2", "C3", "C4", "C5", "C6"])
        self.assertEqual(c1["propagation_depth"], 5)
        self.assertEqual(c1["impact_score"], 5)
        
        # 2. Branching Validation
        b_root = get_res("B_Root")
        self.assertEqual(b_root["affected_tasks"], ["B1", "B2", "B3"])
        self.assertEqual(b_root["propagation_depth"], 1)
        
        # 3. Merging Validation
        m1 = get_res("M1")
        self.assertEqual(m1["affected_tasks"], ["M_Target"])
        m_target = get_res("M_Target")
        self.assertEqual(m_target["affected_tasks"], [])
        
        # 4. Disconnected Component
        d1 = get_res("D1")
        self.assertEqual(d1["affected_tasks"], ["D2"])
        
        # 5. Invalid Nodes in chain
        iv1 = get_res("IV1")
        self.assertEqual(iv1["affected_tasks"], ["IV2"])
        self.assertEqual(iv1["propagation_depth"], 1)
        
        # 6. Isolated Nodes
        iso = get_res("ISO_1")
        self.assertEqual(iso["affected_tasks"], [])
        self.assertEqual(iso["impact_score"], 0)
        
        # Phase 6 Summary Checks
        summary = out["summary"]
        self.assertEqual(summary["total_tasks"], 20)
        # Verify deterministic Edge math
        # C chain = 5 edges
        # B branch = 3 edges
        # M merge = 3 edges
        # D group = 1 edge
        # IV logic = 1 edge
        # Total = 13 edges
        self.assertEqual(summary["total_edges"], 13)
        self.assertEqual(summary["max_depth"], 5)   # C chain depth 5
        self.assertEqual(summary["max_impact_score"], 5) # C1 affects 5

    def test_determinism_proof(self):
        """Phase 8: Same input -> identical output. No traversal or ordering variation."""
        
        payload_1 = copy.deepcopy(self.payload)
        out_1 = PropagationEngine(payload_1).compute_all_propagations()
        
        # Repeat n times and assert absolute memory identity mapping equality
        for _ in range(50):
            payload_copy = copy.deepcopy(self.payload)
            # Shuffle input task array randomly conceptually (by reversing or shifting)
            # ensuring logic is absolutely input-order agnostic
            payload_copy["tasks"].reverse() 
            out_n = PropagationEngine(payload_copy).compute_all_propagations()
            
            # Assert exact dictionary equality natively maps identical json string representations
            self.assertEqual(out_1, out_n)

if __name__ == '__main__':
    unittest.main()
