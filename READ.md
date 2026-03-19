# pebbling

This project studies pebbling configurations on finite graphs.

Let `G` be a graph and let pebbles be distributed on its vertices. For an edge
`uv`, a pebbling step `u -> v` removes two pebbles from `u` and places one
pebble on the adjacent vertex `v`.

A configuration on `G` is a function `c : V(G) -> N`, where `c(v)` is the
number of pebbles on `v`. The size, or weight, of a configuration is

`sum_{v in V(G)} c(v)`.

Two graph invariants are implemented in this repository.

- `stacking_number(G)` is the smallest integer `t` such that every
  configuration of size `t` can be transformed, by pebbling steps, into a
  configuration with all remaining pebbles on a single vertex.
- `clearing_number(G)` is the smallest integer `t` such that every
  configuration of size `t` can be transformed, by pebbling steps, into a
  configuration with exactly one pebble left.

These values are known to behave as follows.

- `stacking_number(G)` is defined for connected graphs.
- `clearing_number(G)` is defined for connected non-bipartite graphs.

`pebbling.py`

The file [pebbling.py](/home/lsoukup/SLmath/Pebbling/pebbling.py) provides the
module-level functions

- `stacking_number(G)`
- `clearing_number(G)`
- `estim(G)`

where `G` is a NetworkX graph.

The module also contains the helper class `Pebbling`, which organizes the
internal search. When a `Pebbling` object is created, the graph is relabeled to
vertices `0, 1, ..., n - 1`. A configuration is then stored as a `bytes`
object with one byte per vertex. This representation makes configurations
hashable, compact, and easy to use in recursive set constructions.

Main responsibilities of `Pebbling`

- convert lists, tuples, or `bytes` into validated configurations
- compute `leaf(r)`, the number of leaves of `G` distinct from `r`
- compute the rooted quantity `sigma(r)` and the estimate `estim(G)`
- enumerate binary configurations of a fixed weight
- enumerate one-supported configurations of a fixed weight
- compute all one-step parents of a configuration
- count all distinct one-step children of a configuration
- build the recursive families used for the clearing and stacking numbers

Rooted estimate

For a vertex `r`, the current implementation defines

`sigma(r) = sum(2^{d(r,v)} deg(v) : v != r, deg(v) > 1) + deg(r) + 1`,

where `d(r,v)` is the usual shortest-path distance from `r` to `v`. It also
defines

`estim(G) = max(sigma(r) + leaf(r) : r in V(G))`.

Recursive families

The algorithms do not test every configuration independently. Instead, they
construct recursive families of configurations that are still "bad" at a given
weight.

For the clearing number, the module builds clearing families `T(i)`.

- `T(1)` is empty.
- To pass from `T(i)` to `T(i+1)`, the algorithm first applies
  `parent_counter(...)`, which collects all configurations that can pebble in
  one step to configurations already in the family.
- While `i <= |V(G)|`, all binary configurations of weight `i + 1` are also
  added.

For the stacking number, the module builds stacking families `U(i)` in a very
similar way, except that before binary configurations are added, all
configurations of weight `i + 1` supported on a single vertex are removed.

The methods

- `sizes_of_clearing_sets(K)`
- `sizes_of_stacking_sets(K)`

return the sizes of these families together with the numbers of configurations
that matched the recursive step. The corresponding invariant is the first
index `i > 1` for which the matched count becomes `0`.

Search bound

Because configurations are stored as bytes, each vertex can carry at most `255`
pebbles in this implementation. For a graph with `n` vertices, the exported
functions search up to weight `255 * n`, and raise `ValueError` if the relevant
number is not found before that bound.

Example

```python
import networkx as nx
from pebbling import clearing_number, estim, stacking_number

G = nx.cycle_graph(5)

print(stacking_number(G))
print(clearing_number(G))
print(estim(G))
```

Error behavior

- `clearing_number(G)` raises `ValueError` when `G` is bipartite, because the
  clearing number is undefined in that case.
- both exported functions raise `ValueError` if the search reaches the
  byte-based bound without finding the required index
- creating `Pebbling(G)` raises `TypeError` if `G` is not a NetworkX graph
- creating `Pebbling(G)` raises `ImportError` if NetworkX is not installed

Atlas tree report

The file
[report_atlas_trees_estim.py](/home/lsoukup/SLmath/Pebbling/report_atlas_trees_estim.py)
scans the NetworkX graph atlas, keeps the connected tree graphs with at least
two vertices, and reports

- `stacking_number(G)`
- `estim(G)`

It prints a text table to the terminal and also writes a LaTeX file with a
TikZ table containing the computed values together with small drawings of the
graphs.

Typical usage

```bash
python report_atlas_trees_estim.py
python report_atlas_trees_estim.py --limit 10
python report_atlas_trees_estim.py -o my_table.tex
```

By default the LaTeX output is written to
[atlas_trees_estim_table.tex](/home/lsoukup/SLmath/Pebbling/atlas_trees_estim_table.tex).

Atlas gallery report

The file
[report_networkx_gallery.py](/home/lsoukup/SLmath/Pebbling/report_networkx_gallery.py)
scans the full NetworkX graph atlas, keeps the connected nonempty graphs, and
generates a LaTeX report containing

- `stacking_number(G)`
- `clearing_number(G)` when defined
- a small TikZ drawing for each graph

Typical usage

```bash
python report_networkx_gallery.py
python report_networkx_gallery.py --jobs 4
python report_networkx_gallery.py --limit 25 -o sample_report.tex
```

By default the LaTeX output is written to
[networkx_gallery_pebbling_table.tex](/home/lsoukup/SLmath/Pebbling/networkx_gallery_pebbling_table.tex).
