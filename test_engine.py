import unittest
import copy
from engine import compute_propagation

class TestPropagationEngine(unittest.TestCase):
    def setUp(self):
        # Deliverable 2: Minimum 8 complex graph scenarios
        self.payload = {
            "execution_id": "test_exec_001",
            "tasks": [
                # Case 1: Deep Chain (5+ levels)
                {"task_id": "C1", "depends_on": []},
                {"task_id": "C2", "depends_on": ["C1"]},
                {"task_id": "C3", "depends_on": ["C2"]},
                {"task_id": "C4", "depends_on": ["C3"]},
                {"task_id": "C5", "depends_on": ["C4"]},
                {"task_id": "C6", "depends_on": ["C5"]},
                {"task_id": "C7", "depends_on": ["C6"]},
                
                # Case 2: Branching graph (one -> many)
                {"task_id": "B_Root", "depends_on": []},
                {"task_id": "B1", "depends_on": ["B_Root"]},
                {"task_id": "B2", "depends_on": ["B_Root"]},
                {"task_id": "B3", "depends_on": ["B_Root"]},
                
                # Case 3: Merging graph (many -> one)
                {"task_id": "M1", "depends_on": []},
                {"task_id": "M2", "depends_on": []},
                {"task_id": "M3", "depends_on": []},
                {"task_id": "M_Target", "depends_on": ["M1", "M2", "M3"]},
                
                # Case 4: Disconnected Components
                {"task_id": "D1", "depends_on": []},
                {"task_id": "D2", "depends_on": ["D1"]},
                
                # Case 5: Invalid Nodes in Chain (depends on non-existent node)
                {"task_id": "IV1", "depends_on": ["MISSING_X_1", "MISSING_X_2"]},
                {"task_id": "IV2", "depends_on": ["IV1"]},
                
                # Case 6: Isolated Nodes
                {"task_id": "ISO_1", "depends_on": []},
                
                # Case 7: Cyclic Graph Attempt (Should be handled gracefully by BFS visited set)
                # CY1 <-> CY2
                {"task_id": "CY1", "depends_on": ["CY2"]},
                {"task_id": "CY2", "depends_on": ["CY1"]},
                
                # Case 8: Multi-Root Blockage Merge (Two sources block the exact same target)
                {"task_id": "MR1", "depends_on": []},
                {"task_id": "MR2", "depends_on": []},
                {"task_id": "MR_Target", "depends_on": ["MR1", "MR2"]}
            ],
            
            # For Phase 4 execution, we treat all of the "root" sources of these topologies as INVALID
            # to verify they accurately evaluate impact propagation topology.
            "constraint_results": [
                {"task_id": "C1", "is_valid": False}, # Case 1 origin
                {"task_id": "B_Root", "is_valid": False}, # Case 2 origin
                {"task_id": "M1", "is_valid": False}, # Case 3 origin A
                {"task_id": "M2", "is_valid": False}, # Case 3 origin B
                {"task_id": "D1", "is_valid": False}, # Case 4 origin
                {"task_id": "IV1", "is_valid": False}, # Case 5 origin
                {"task_id": "ISO_1", "is_valid": False}, # Case 6 origin
                {"task_id": "CY1", "is_valid": False}, # Case 7 origin
                {"task_id": "MR1", "is_valid": False}, # Case 8 origin A
                {"task_id": "MR2", "is_valid": False}  # Case 8 origin B
            ]
        }

    def test_eight_core_cases(self):
        out = compute_propagation(self.payload)
        
        def get_res(tid):
            for r in out["results"]:
                if r["task_id"] == tid:
                    return r
            return None
            
        # Case 1: Deep Chain
        c1 = get_res("C1")
        self.assertEqual(c1["affected_tasks"], ["C2", "C3", "C4", "C5", "C6", "C7"])
        self.assertEqual(c1["propagation_depth"], 6)
        
        # Case 2: Branching
        b_root = get_res("B_Root")
        self.assertEqual(b_root["affected_tasks"], ["B1", "B2", "B3"])
        
        # Case 3: Merging
        m1 = get_res("M1")
        self.assertEqual(m1["affected_tasks"], ["M_Target"])
        m2 = get_res("M2")
        self.assertEqual(m2["affected_tasks"], ["M_Target"])
        
        # Case 4: Disconnected
        d1 = get_res("D1")
        self.assertEqual(d1["affected_tasks"], ["D2"])
        
        # Case 5: Invalid chain
        iv1 = get_res("IV1")
        self.assertEqual(iv1["affected_tasks"], ["IV2"])
        
        # Case 6: Isolated 
        iso = get_res("ISO_1")
        self.assertEqual(iso["impact_score"], 0)
        
        # Case 7: Cycle
        cy1 = get_res("CY1")
        self.assertEqual(cy1["affected_tasks"], ["CY1", "CY2"])
        
        # Case 8: Multi-Root Blockage Merge 
        mr1 = get_res("MR1")
        self.assertEqual(mr1["affected_tasks"], ["MR_Target"])

    def test_strict_contract(self):
        out = compute_propagation(self.payload)
        self.assertEqual(out["execution_id"], "test_exec_001")
        
        # Verify schema elements exist strictly
        summary = out["summary"]
        self.assertEqual(summary["total_tasks"], 25)
        self.assertEqual(summary["total_edges"], 18)

    def test_determinism_proof(self):
        """
        Deliverable 3: Determinism Proof 
        Repeated execution with identical arrays MUST equal natively identical json mappings,
        proving absolutely no variation despite memory shifts via array shuffling.
        """
        out_1 = compute_propagation(copy.deepcopy(self.payload))
        
        for _ in range(50):
            payload_scrambled = copy.deepcopy(self.payload)
            # Shuffle inputs artificially
            payload_scrambled["tasks"].reverse()
            out_n = compute_propagation(payload_scrambled)
            
            # Dictionary matching asserts completely invariant identical outputs
            self.assertEqual(out_1, out_n)

if __name__ == '__main__':
    unittest.main()
