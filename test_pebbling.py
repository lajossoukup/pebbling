from collections import Counter

import networkx as nx
import pytest

from pebbling import Pebbling


def test_init_requires_networkx_graph() -> None:
    with pytest.raises(TypeError):
        Pebbling([(0, 1)])


def test_init_rejects_disconnected_graph() -> None:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1])

    with pytest.raises(ValueError):
        Pebbling(graph)


def test_init_rejects_empty_graph() -> None:
    with pytest.raises(ValueError, match="at least 2 vertices"):
        Pebbling(nx.Graph())


def test_init_rejects_single_vertex_graph() -> None:
    with pytest.raises(ValueError, match="at least 2 vertices"):
        Pebbling(nx.Graph([(0, 0)]))


def test_init_relabels_vertices_and_stores_directed_edges() -> None:
    graph = nx.Graph()
    graph.add_edges_from([("u", "v"), ("v", "w")])

    pebbling = Pebbling(graph)

    assert pebbling.vertices == [0, 1, 2]
    assert list(pebbling.G.nodes()) == [0, 1, 2]
    assert list(pebbling.G.edges()) == [(0, 1), (1, 2)]
    assert pebbling.directed_edges == [(0, 1), (1, 2), (1, 0), (2, 1)]


def test_init_copies_graph() -> None:
    graph = nx.path_graph(3)

    pebbling = Pebbling(graph)
    graph.add_edge(0, 3)

    assert list(pebbling.G.nodes()) == [0, 1, 2]
    assert list(pebbling.G.edges()) == [(0, 1), (1, 2)]


def test_norm_counts_total_number_of_pebbles() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.norm((2, 0, 5, 1)) == 8


def test_supp_returns_vertices_with_nonzero_entries() -> None:
    pebbling = Pebbling(nx.path_graph(5))

    assert pebbling.supp((0, 3, 0, 1, 0)) == {1, 3}


def test_suppn_returns_support_size() -> None:
    pebbling = Pebbling(nx.path_graph(5))

    assert pebbling.suppn((0, 3, 0, 1, 0)) == 2


def test_stacked_returns_all_singleton_support_configurations() -> None:
    pebbling = Pebbling(nx.path_graph(3))

    assert pebbling.stacked(4) == {
        (4, 0, 0),
        (0, 4, 0),
        (0, 0, 4),
    }


def test_stacked_is_empty_for_nonpositive_or_too_large_weights() -> None:
    pebbling = Pebbling(nx.path_graph(3))

    assert pebbling.stacked(-1) == set()
    assert pebbling.stacked(0) == set()
    assert pebbling.stacked(256) == set()


def test_minimal_returns_all_binary_configurations_of_weight_i() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.minimal(2) == {
        (1, 1, 0, 0),
        (1, 0, 1, 0),
        (1, 0, 0, 1),
        (0, 1, 1, 0),
        (0, 1, 0, 1),
        (0, 0, 1, 1),
    }


def test_minimal_is_empty_out_of_range() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.minimal(-1) == set()
    assert pebbling.minimal(5) == set()


def test_is_almost_stacked_accepts_stacked_configuration() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.is_almost_stacked((4, 0, 0, 0))


def test_is_almost_stacked_accepts_one_large_entry_with_ones_elsewhere() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.is_almost_stacked((3, 1, 0, 1))


def test_is_almost_stacked_rejects_two_entries_above_one() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert not pebbling.is_almost_stacked((2, 0, 2, 0))


def test_parents_finds_single_parent() -> None:
    pebbling = Pebbling(nx.Graph([(0, 1)]))

    assert pebbling.parents((0, 1)) == {(2, 0)}


def test_parents_finds_multiple_parents() -> None:
    pebbling = Pebbling(nx.path_graph(3))

    assert pebbling.parents((0, 1, 0)) == {
        (2, 0, 0),
        (0, 0, 2),
    }


def test_parents_is_empty_when_no_reverse_move_is_possible() -> None:
    pebbling = Pebbling(nx.Graph([(0, 1)]))

    assert pebbling.parents((0, 0)) == set()


def test_parents_respects_byte_limit() -> None:
    pebbling = Pebbling(nx.Graph([(0, 1)]))

    assert pebbling.parents((1, 254)) == {(3, 253)}


def test_number_of_children_counts_distinct_children() -> None:
    pebbling = Pebbling(nx.Graph([(0, 1)]))

    assert pebbling.number_of_children((2, 0)) == 1
    assert pebbling.number_of_children((2, 2)) == 2
    assert pebbling.number_of_children((1, 1)) == 0


def test_parent_counter_counts_each_parent_once_per_key() -> None:
    pebbling = Pebbling(nx.path_graph(3))
    T = Counter({
        (0, 1, 0): 1,
        (1, 0, 1): 0,
    })

    assert pebbling.parent_counter(T) == Counter({
        (1, 2, 0): 1,
        (0, 2, 1): 1,
    })


def test_parent_counter_accumulates_repeated_parents() -> None:
    pebbling = Pebbling(nx.Graph([(0, 1)]))
    T = Counter({
        (0, 3): 1,
        (3, 0): 1,
    })

    assert pebbling.parent_counter(T) == Counter({
        (2, 2): 2,
    })


def test_parent_counter_skips_mismatched_entries() -> None:
    pebbling = Pebbling(nx.Graph([(0, 1)]))

    assert pebbling.parent_counter(Counter({(0, 3): 2})) == Counter()


def test_clear_parent_counter_adds_minimal_i_with_zero_values_when_i_is_small() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.clear_parent_counter(Counter(), 2) == Counter({
        (1, 1, 0, 0): 0,
        (1, 0, 1, 0): 0,
        (1, 0, 0, 1): 0,
        (0, 1, 1, 0): 0,
        (0, 1, 0, 1): 0,
        (0, 0, 1, 1): 0,
    })


def test_clear_parent_counter_does_not_add_minimal_when_i_is_one() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.clear_parent_counter(Counter(), 1) == Counter()


def test_clear_parent_counter_does_not_add_minimal_when_i_is_too_large() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.clear_parent_counter(Counter(), 5) == Counter()


def test_clear_parent_counter_adds_minimal_when_i_equals_vertex_count() -> None:
    pebbling = Pebbling(nx.path_graph(4))

    assert pebbling.clear_parent_counter(Counter(), 4) == Counter({
        (1, 1, 1, 1): 0,
    })


def test_clear_parent_counter_keeps_parent_counter_contributions() -> None:
    pebbling = Pebbling(nx.path_graph(3))
    T = Counter({
        (0, 1, 0): 0,
    })

    assert pebbling.clear_parent_counter(T, 2) == Counter({
        (2, 0, 0): 1,
        (0, 0, 2): 1,
        (1, 1, 0): 0,
        (1, 0, 1): 0,
        (0, 1, 1): 0,
    })


def test_stack_parent_counter_removes_stacked_configurations() -> None:
    pebbling = Pebbling(nx.path_graph(3))

    assert pebbling.stack_parent_counter(Counter(), 3) == {
        (1, 1, 1): 0,
    }


def test_stack_parent_counter_keeps_nonstacked_contributions() -> None:
    pebbling = Pebbling(nx.complete_graph(3))
    T = Counter({
        (0, 1, 0): 0,
    })

    assert pebbling.stack_parent_counter(T, 2) == Counter({
        (1, 1, 0): 0,
        (1, 0, 1): 0,
        (0, 1, 1): 0,
    })


def test_clearing_number_uses_the_recursive_counters() -> None:
    pebbling = Pebbling(nx.cycle_graph(5))

    i, W = pebbling.clearing_number()

    assert i == 10
    assert W == {
        (9, 0, 0, 0, 0),
        (0, 9, 0, 0, 0),
        (0, 0, 9, 0, 0),
        (0, 0, 0, 9, 0),
        (0, 0, 0, 0, 9),
    }


def test_clearing_number_on_c7() -> None:
    pebbling = Pebbling(nx.cycle_graph(7))

    i, W = pebbling.clearing_number()

    assert i == 22
    assert W == {
        (21, 0, 0, 0, 0, 0, 0),
        (0, 21, 0, 0, 0, 0, 0),
        (0, 0, 21, 0, 0, 0, 0),
        (0, 0, 0, 21, 0, 0, 0),
        (0, 0, 0, 0, 21, 0, 0),
        (0, 0, 0, 0, 0, 21, 0),
        (0, 0, 0, 0, 0, 0, 21),
    }


def test_clearing_number_on_k3_returns_matching_keys_from_t_i_minus_1() -> None:
    pebbling = Pebbling(nx.complete_graph(3))

    assert pebbling.clearing_number() == (
        4,
        {
            (3, 0, 0),
            (0, 3, 0),
            (0, 0, 3),
            (1, 1, 1),
        },
    )


def test_clearing_number_is_undefined_for_bipartite_graphs() -> None:
    pebbling = Pebbling(nx.path_graph(3))

    with pytest.raises(ValueError, match="undefined for bipartite graphs"):
        pebbling.clearing_number()


def test_stacking_number_on_k2() -> None:
    pebbling = Pebbling(nx.complete_graph(2))

    assert pebbling.stacking_number() == (3, {(1, 1)})


def test_stacking_number_on_k3() -> None:
    pebbling = Pebbling(nx.complete_graph(3))

    assert pebbling.stacking_number() == (
        4,
        {
            (1, 1, 1),
        },
    )


def test_stacking_number_on_path_graph() -> None:
    pebbling = Pebbling(nx.path_graph(3))

    assert pebbling.stacking_number() == (
        7,
        {
            (5, 0, 1),
            (3, 0, 3),
            (1, 0, 5),
        },
    )


def test_is_critical_stacked_almost_stacked_is_true_for_k2() -> None:
    pebbling = Pebbling(nx.complete_graph(2))

    assert pebbling.is_critical_stacked_almost_stacked()


def test_is_critical_stacked_almost_stacked_is_true_for_k3() -> None:
    pebbling = Pebbling(nx.complete_graph(3))

    assert pebbling.is_critical_stacked_almost_stacked()
