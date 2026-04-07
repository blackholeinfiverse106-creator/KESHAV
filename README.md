# KESHAV: Deterministic Task Propagation Engine

A high-performance algorithmic Blockage-Aware Propagation Engine. This purely functional python module calculates downstream 'blast-radius' limits predictably without introducing any side-effect variance or randomness.

## Graph Structure Explanation

The engine handles task definitions structurally by parsing acyclic and cyclic task layouts, compiling them safely into twin data maps independently:
* `adjacency`: Tracks exact mapping of dependencies toward dependent objects (`dependency → dependent`).
* `reverse_adjacency`: Re-mapping task paths toward upstream elements (`dependent → dependencies`).

Invalid relations inside configurations (pointers toward tasks omitted from the deployment block) simply evaluate as safe missing states securely rather than halting code. 

## Traversal Explanation

Calculations operate via an **Iterative Breadth-First-Search (BFS)**.
1. The engine checks every execution `payload` task. If an isolated payload sets `"is_valid": False` via the constrained settings block, it initiates traversals.
2. The traversal executes loop mapping dependencies mathematically without resolving any Recursion properties, scaling deeply across large layouts inherently safely.
3. Visited `set()` hashing handles cycles without infinity errors, while sorting lists lexicographically ensures absolute output determinism despite native execution memory differences. 

## Entry Wrapper

```python
from engine import compute_propagation

payload = {
    # payload data schema
}

output_dictionary = compute_propagation(payload)
```
