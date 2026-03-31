"""Basic pebbling helpers for connected NetworkX graphs."""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import TypeAlias

import networkx as nx

Configuration: TypeAlias = tuple[int, ...]

# A configuration is a tuple with one entry for each vertex of G; each entry
# stores the number of pebbles at the corresponding vertex.


class Pebbling:
    """Store a relabeled connected graph and its oriented edge pairs."""

    def __init__(self, G: nx.Graph) -> None:
        if not isinstance(G, nx.Graph):
            raise TypeError("G must be a NetworkX graph.")

        if G.number_of_nodes() < 2:
            raise ValueError("G must have at least 2 vertices.")

        if not nx.is_connected(G):
            raise ValueError("G must be connected.")

        # Work with a fixed vertex order so configurations can be stored as tuples.
        relabel_map = {
            vertex: index for index, vertex in enumerate(G.nodes())
        }
        self.G = nx.relabel_nodes(G, relabel_map, copy=True)
        self.vertices = list(self.G.nodes())

        edges = list(self.G.edges())
        # Each undirected pebbling step can be used in either direction.
        self.directed_edges = edges + [(b, a) for a, b in edges]

    def norm(self, c: Configuration) -> int:
        """Return the norm of a configuration."""
        return sum(c)

    def supp(self, c: Configuration) -> set[int]:
        """Return the support of a configuration."""
        return {vertex for vertex, value in enumerate(c) if value != 0}

    def suppn(self, c: Configuration) -> int:
        """Return the size of the support of a configuration."""
        return len(self.supp(c))

    def sigma(self, r: int) -> int:
        """Return sigma(r) = sum(2**d(r, v) * degree(v)) over eligible vertices."""
        if r not in self.G:
            raise ValueError("r must be a vertex of the graph.")

        # Distances are measured from r in the relabeled graph.
        distances = nx.single_source_shortest_path_length(self.G, r)
        total = 0

        for v in self.vertices:
            degree = self.G.degree[v]
            if v != r and degree <= 1:
                continue
            total += (2 ** distances[v]) * degree

        return total

    def leaf(self, r: int) -> int:
        """Return the number of degree-1 vertices different from r."""
        if r not in self.G:
            raise ValueError("r must be a vertex of the graph.")

        return sum(
            1 for v in self.vertices if v != r and self.G.degree[v] == 1
        )

    def tree_estimation(self) -> int:
        """Return max_r (sigma(r) + leaf(r)) + 1 over all vertices r."""
        return max(self.sigma(r) + self.leaf(r) for r in self.vertices) + 1

    def stacked(self, i: int) -> set[Configuration]:
        """Return all stacked configurations of norm i."""
        if i <= 0 or i > 255:
            return set()

        result: set[Configuration] = set()

        for vertex in self.vertices:
            configuration = [0] * len(self.vertices)
            configuration[vertex] = i
            result.add(tuple(configuration))

        return result

    def minimal(self, i: int) -> set[Configuration]:
        """Return all configurations c with suppn(c) = norm(c) = i."""
        if i < 0 or i > len(self.vertices):
            return set()

        result: set[Configuration] = set()

        for support_size_i in combinations(self.vertices, i):
            configuration = [0] * len(self.vertices)
            for vertex in support_size_i:
                configuration[vertex] = 1
            result.add(tuple(configuration))

        return result

    def is_almost_stacked(self, c: Configuration) -> bool:
        """Return whether all but at most one vertex carry at most one pebble."""
        return sum(1 for value in c if value > 1) <= 1

    def parents(self, c: Configuration) -> set[Configuration]:
        """Return the set of configurations d such that c is a child of d."""
        result: set[Configuration] = set()

        for source, target in self.directed_edges:
            # Reversing a pebbling move requires one pebble at the target and
            # enough room to add two pebbles at the source.
            if c[target] == 0 or c[source] > 253:
                continue

            parent = list(c)
            parent[source] += 2
            parent[target] -= 1
            result.add(tuple(parent))

        return result

    def number_of_children(self, c: Configuration) -> int:
        """Return the number of distinct children of c."""
        return sum(1 for source, _target in self.directed_edges if c[source] >= 2)

    def parent_counter(self, T: Counter[Configuration]) -> Counter[Configuration]:
        """Return the counter S built from those c with T[c]=number_of_children(c)."""
        S: Counter[Configuration] = Counter()

        for c in T:
            # Only fully matched configurations contribute to the next level.
            if T[c] != self.number_of_children(c):
                continue
            for d in self.parents(c):
                S[d] += 1

        return S

    def clear_parent_counter(
        self, T: Counter[Configuration], i: int
    ) -> Counter[Configuration]:
        """Return the clearing recursion counter at level i."""
        S = self.parent_counter(T)

        # Minimal binary configurations are the base non-cleared configurations
        # at level i.
        if 1 < i and i <= len(self.vertices):
            for c in self.minimal(i):
                S[c] = 0

        return S

    def stack_parent_counter(
        self, T: Counter[Configuration], i: int
    ) -> Counter[Configuration]:
        """Return the stacking recursion counter at level i."""
        S = self.clear_parent_counter(T, i)

        # Stacked configurations are removed because the stacking recursion
        # keeps only non-stacked witnesses.
        for c in self.stacked(i):
            S.pop(c, None)

        print(f"{T} => {i} => {S}")
        return S

    def clearing_number(self) -> tuple[int, set[Configuration]]:
        """Return the clearing number together with selected keys from T_{i-1}."""
        if nx.is_bipartite(self.G):
            raise ValueError("Clearing number is undefined for bipartite graphs.")

        T_im1: Counter[Configuration] = Counter()
        T_i: Counter[Configuration] = self.clear_parent_counter(T_im1, 1)

        for i in range(1, 255):
            T_ip1 = self.clear_parent_counter(T_i, i + 1)
            # Once the recursion dies out beyond the trivial small levels, the
            # previous fully matched configurations form the witness set.
            if not T_ip1 and i > self.G.number_of_nodes():
                witness_set = {
                    c for c in T_im1 if T_im1[c] == self.number_of_children(c)
                }
                return i, witness_set
            T_im1, T_i = T_i, T_ip1

        raise ValueError("Clearing number was not found before level 255.")

    def stacking_number(self) -> tuple[int, set[Configuration]]:
        """Return the stacking number together with selected keys from T_{i-1}."""
        T_im1: Counter[Configuration] = Counter()
        T_i: Counter[Configuration] = self.stack_parent_counter(T_im1, 1)

        for i in range(1, 255):
            T_ip1 = self.stack_parent_counter(T_i, i + 1)
            # As in the clearing recursion, termination is detected when the
            # next counter becomes empty after the initial small levels.
            if not T_ip1 and i > self.G.number_of_nodes():
                witness_set = {
                    c for c in T_im1 if T_im1[c] == self.number_of_children(c)
                }
                return i, witness_set
            T_im1, T_i = T_i, T_ip1

        raise ValueError("Stacking number was not found before level 255.")

    def is_critical_stacked_almost_stacked(self) -> bool:
        """Return whether the stacking witness set contains an almost stacked configuration."""
        _i, witness_set = self.stacking_number()
        return any(self.is_almost_stacked(c) for c in witness_set)

    def is_critical_clear_almost_stacked(self) -> bool:
        """Return whether the clearing witness set contains an almost stacked configuration."""
        _i, witness_set = self.clearing_number()
        return any(self.is_almost_stacked(c) for c in witness_set)
