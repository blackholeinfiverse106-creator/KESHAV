# KESHAV: Deterministic Task Propagation Engine

A high-performance algorithmic task relationship and propagation engine built in Python. This engine strictly constructs task relationship graphs mapping downstream propagation and scores pure impact topologically without assuming any underlying business logic. 

## Key Features

1. **Deterministic Execution:** No randomization. Uses lexicographical sorting to evaluate dependent sets consistently.
2. **Pure Iterative Traversal:** Computes graph propagation without deep recursion mechanisms (using an explicit Iterative Breadth-First-Search queue array) to prevent maximum recursion depth execution errors on heavy dense graph paths.
3. **Implicit Error Boundary:** Invalid references or missing properties inside inputs log gracefully by simply skipping computation instead of catastrophically dropping context routines or modifying source states.
4. **Zero-Mutation Guarantees:** Assumes inputs as truth boundaries; references are completely detached from mutable variables during adjacency construction and score computing phases.

## Project Structure

* **`engine.py`**: The core propagation loop logic divided into two phases:
  * **Phase 1**: Graph construction. Maps adjacency `dependency → dependent` and inverse `task → dependency`. Filters duplicates out through immutable node sets.
  * **Phase 2**: Iterative Engine evaluation. Retrieves deterministic topological sets representing raw mapping intersections and computes aggregate properties isolated per node. 
* **`test_engine.py`**: A suite of standard regression tests using the `unittest` framework. Contains validations for acyclic paths, dropped properties and phantom references behavior correctness.

## Usage

You can deploy the engine by passing independent `tasks_data` nodes and `constraints` rules representing topological structure maps.

```python
from engine import PropagationEngine

tasks_data = [
    {"id": "A", "dependencies": [], "score": 10},
    {"id": "B", "dependencies": ["A", "MISSING_TASK"], "score": 5},
    {"id": "C", "dependencies": ["B"], "score": 1}
]

constraints = {
    "A": {"impact_multiplier": 1.5}
}

engine = PropagationEngine(tasks_data, constraints)

# Returns a dictionary containing mapped downstream nodes & mathematically locked scale rules
results = engine.compute_all_propagations()

print(results["A"])
# >> {'downstream_tasks': ['B', 'C'], 'topological_impact_size': 2, 'propagation_score': 21.0}
```

## Running Tests

To systematically check logic constraints over execution algorithms:
```bash
python -m unittest test_engine.py
```
