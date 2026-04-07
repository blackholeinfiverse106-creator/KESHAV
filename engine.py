from collections import deque
from typing import List, Dict, Set, Any

class PropagationEngine:
    def __init__(self, payload: Dict[str, Any]):
        """
        Initializes the PropagationEngine matching the exact input contract.
        """
        self.execution_id = payload.get("execution_id", "default_run")
        self.tasks_data = payload.get("tasks", [])
        constraints_list = payload.get("constraint_results", [])
        
        # O(1) map for constraints
        self.constraints = {c["task_id"]: c for c in constraints_list if "task_id" in c}
        
        # Mappings
        self.reverse_adjacency: Dict[str, Set[str]] = {} # dependent -> dependencies
        self.adjacency: Dict[str, Set[str]] = {} # dependency -> dependent
        
        self.valid_task_ids = set()
        
        self._build_graph()

    def _build_graph(self):
        """
        Phase 1 - Graph Construction
        """
        # Collect valid IDs first
        for task in self.tasks_data:
            task_id = task.get("task_id")
            if task_id is not None:
                self.valid_task_ids.add(task_id)
                self.reverse_adjacency[task_id] = set()
                if task_id not in self.adjacency:
                    self.adjacency[task_id] = set()

        # Build mappings
        for task in self.tasks_data:
            task_id = task.get("task_id")
            if task_id is None:
                continue

            deps = task.get("depends_on", [])
            for dep in deps:
                # ignore invalid references
                if dep not in self.valid_task_ids:
                    continue
                
                self.reverse_adjacency[task_id].add(dep)
                
                if dep not in self.adjacency:
                    self.adjacency[dep] = set()
                self.adjacency[dep].add(task_id)

    def get_downstream_tasks(self, task_id: str) -> Dict[str, Any]:
        """
        Phase 2 & 3 - Deterministic Traversal Engine (Iterative BFS)
        Computes downstream tasks and max propagation_depth.
        """
        if task_id not in self.valid_task_ids:
            return {"affected_tasks": [], "propagation_depth": 0}

        downstream = set()
        queue = deque([(task_id, 0)])
        max_depth = 0
        
        while queue:
            current, depth = queue.popleft()
            max_depth = max(max_depth, depth)
            
            # Deterministic sorting of dependents list
            dependents = sorted(list(self.adjacency.get(current, set())))
            
            for dependent in dependents:
                if dependent not in downstream:
                    downstream.add(dependent)
                    queue.append((dependent, depth + 1))
                    
        return {
            "affected_tasks": sorted(list(downstream)),
            "propagation_depth": max_depth
        }

    def compute_all_propagations(self) -> Dict[str, Any]:
        """
        Phase 3, 4, 5, 6 - Complies to STRICT OUTPUT CONTRACT.
        """
        results_list = []
        max_impact = 0
        max_global_depth = 0
        
        # Phase 5 - Output sorted by task_id
        for task_id in sorted(list(self.valid_task_ids)):
            # Phase 4 - Blockage-Aware Propagation
            # Explicitly check if task is invalid
            constraint = self.constraints.get(task_id)
            is_valid = True
            if constraint is not None:
                is_valid = constraint.get("is_valid", True)
                
            # If a task is invalid -> treat it as a propagation source specially
            if is_valid is False:
                traversal_result = self.get_downstream_tasks(task_id)
                affected = traversal_result["affected_tasks"]
                depth = traversal_result["propagation_depth"]
                
                impact_score = len(affected)
                max_impact = max(max_impact, impact_score)
                max_global_depth = max(max_global_depth, depth)
                
                results_list.append({
                    "task_id": task_id,
                    "affected_tasks": affected,
                    "impact_score": impact_score,
                    "propagation_depth": depth
                })
            
        total_edges = sum(len(deps) for deps in self.adjacency.values())
        
        return {
            "execution_id": self.execution_id,
            "results": results_list,
            "summary": {
                "total_tasks": len(self.valid_task_ids),
                "total_edges": total_edges,
                "max_impact_score": max_impact,
                "max_depth": max_global_depth
            }
        }

def compute_propagation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deliverable 1: Core entry function
    """
    engine = PropagationEngine(payload)
    return engine.compute_all_propagations()
