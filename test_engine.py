import unittest
from engine import PropagationEngine

class TestPropagationEngine(unittest.TestCase):
    def setUp(self):
        self.tasks_data = [
            {"id": "task_A", "dependencies": [], "score": 5},
            # task_B depends on task_A and an invalid reference 'task_MISSING'
            {"id": "task_B", "dependencies": ["task_A", "task_MISSING"], "score": 2},
            {"id": "task_C", "dependencies": ["task_A"], "score": 3},
            # task_D depends on task_B
            {"id": "task_D", "dependencies": ["task_B"], "score": 10},
            # task_E depends on task_C, task_B, and has duplicate task_B reference
            {"id": "task_E", "dependencies": ["task_C", "task_B", "task_B"], "score": 8},
        ]
        
        self.constraints = {
            "task_A": {"impact_multiplier": 1.5}
        }
        
    def test_graph_construction(self):
        engine = PropagationEngine(self.tasks_data, self.constraints)
        
        # Verify valid IDs
        self.assertEqual(engine.valid_task_ids, {"task_A", "task_B", "task_C", "task_D", "task_E"})
        
        # Verify adjacency (dependency -> dependent)
        # task_A -> task_B, task_C
        self.assertEqual(engine.adjacency["task_A"], {"task_B", "task_C"})
        
        # Verify reverse adjacency (dependent -> dependency)
        # task_B has valid task_A, missing is ignored
        self.assertEqual(engine.reverse_adjacency["task_B"], {"task_A"})
        
        # Verify duplicates are dropped
        self.assertEqual(engine.reverse_adjacency["task_E"], {"task_B", "task_C"})
        
        # Verify invalid references DO NOT exist in graph
        self.assertNotIn("task_MISSING", engine.adjacency)
        self.assertNotIn("task_MISSING", engine.reverse_adjacency)

    def test_deterministic_traversal(self):
        engine = PropagationEngine(self.tasks_data, self.constraints)
        
        # task_A downstream: B, C, D, E
        downstream_A = engine.get_downstream_tasks("task_A")
        self.assertEqual(downstream_A, ["task_B", "task_C", "task_D", "task_E"])
        
        # task_B downstream: D, E
        downstream_B = engine.get_downstream_tasks("task_B")
        self.assertEqual(downstream_B, ["task_D", "task_E"])
        
        # task_E downstream: None
        downstream_E = engine.get_downstream_tasks("task_E")
        self.assertEqual(downstream_E, [])

    def test_propagation_outputs(self):
        engine = PropagationEngine(self.tasks_data, self.constraints)
        results = engine.compute_all_propagations()
        
        # Test basic outputs exist and are structured correctly
        self.assertIn("task_A", results)
        self.assertIn("task_E", results)
        
        # Check topological sizes
        self.assertEqual(results["task_A"]["topological_impact_size"], 4)
        self.assertEqual(results["task_B"]["topological_impact_size"], 2)
        
        # Check deterministic evaluation (no randomness)
        results_again = engine.compute_all_propagations()
        self.assertEqual(results, results_again)

if __name__ == '__main__':
    unittest.main()
