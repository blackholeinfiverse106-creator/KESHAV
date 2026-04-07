from collections import deque
from typing import List, Dict, Set, Any

class PropagationEngine:
    def __init__(self, tasks_data: List[Dict[str, Any]], constraints: Dict[str, Any] = None):
        """
        Initializes the PropagationEngine.
        restrictions:
        - No modification of input
        - No introduction of new rules
        - No randomness
        - No business logic assumptions
        """
        # Store input as immutable reference source. We do not modify these dictionaries.
        self.tasks_data = tasks_data
        self.constraints = constraints if constraints is not None else {}
        
        # Mappings
        # Reverse adjacency: task -> its dependencies
        self.reverse_adjacency: Dict[str, Set[str]] = {}
        # Adjacency list: dependency -> dependent
        self.adjacency: Dict[str, Set[str]] = {}
        
        self.valid_task_ids = set()
        
        self._build_graph()

    def _build_graph(self):
        """
        Phase 1 - Graph Construction
        """
        # Step 1: Collect all valid task IDs
        for task in self.tasks_data:
            task_id = task.get("id")
            if task_id is not None:
                self.valid_task_ids.add(task_id)
                self.reverse_adjacency[task_id] = set()
                if task_id not in self.adjacency:
                    self.adjacency[task_id] = set()

        # Step 2: Build adjacency mappings
        for task in self.tasks_data:
            task_id = task.get("id")
            if task_id is None:
                continue

            deps = task.get("dependencies", [])
            for dep in deps:
                # ignore invalid references without fixing or erroring out
                if dep not in self.valid_task_ids:
                    continue
                
                # Sets handle duplicate edges naturally
                self.reverse_adjacency[task_id].add(dep)
                
                if dep not in self.adjacency:
                    self.adjacency[dep] = set()
                self.adjacency[dep].add(task_id)

    def get_downstream_tasks(self, task_id: str) -> List[str]:
        """
        Phase 2 - Deterministic Traversal Engine (Iterative BFS)
        Computes all downstream affected tasks deterministically without recursion.
        """
        if task_id not in self.valid_task_ids:
            return []

        downstream = set()
        queue = deque([task_id])
        
        while queue:
            current = queue.popleft()
            
            # Sort dependents to ensure strictly deterministic traversal order
            dependents = sorted(list(self.adjacency.get(current, set())))
            
            for dependent in dependents:
                if dependent not in downstream:
                    downstream.add(dependent)
                    queue.append(dependent)
                    
        # Return sorted list for consistent deterministic output structure
        return sorted(list(downstream))

    def compute_all_propagations(self) -> Dict[str, Dict[str, Any]]:
        """
        Computes downstream propagation and structure scoring outputs for all tasks.
        Uses graph topology and provided constraint properties.
        """
        results = {}
        
        for task_id in sorted(list(self.valid_task_ids)):
            affected_downstream = self.get_downstream_tasks(task_id)
            
            # Create a task mapping to extract properties cleanly without mutation
            task_node = next((t for t in self.tasks_data if t.get("id") == task_id), {})
            base_score = task_node.get("score", 0)
            
            # Extract basic topological scoring outputs
            results[task_id] = {
                "downstream_tasks": affected_downstream,
                "topological_impact_size": len(affected_downstream),
                "propagation_score": self._aggregate_score(task_id, affected_downstream, base_score)
            }
            
        return results

    def _aggregate_score(self, source_task_id: str, downstream: List[str], base_score: float) -> float:
        """
        Deterministically aggregates structural scores with structural predictability.
        Incorporates pre-evaluated constraints purely as input constants if present.
        """
        total = float(base_score)
        
        source_constraint = self.constraints.get(source_task_id, {})
        # If there are constraint scores, use them
        if "impact_multiplier" in source_constraint:
            total *= source_constraint["impact_multiplier"]
            
        for ds in downstream:
            ds_node = next((t for t in self.tasks_data if t.get("id") == ds), {})
            total += float(ds_node.get("score", 1.0)) # assume a baseline unit weight if no score is specified
            
        return float(round(total, 4))
