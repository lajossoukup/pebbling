"""Generate a LaTeX report for stacking numbers and tree estimations on atlas trees."""

from __future__ import annotations

import argparse
import io
from contextlib import redirect_stdout
from dataclasses import dataclass

import networkx as nx

from pebbling import Pebbling


@dataclass
class TreeResult:
    """Store the computed invariants for one atlas tree."""

    atlas_index: int
    num_vertices: int
    stacking_number: int
    tree_estimation: int

    @property
    def values_match(self) -> bool:
        """Return whether the two computed values agree."""
        return self.stacking_number == self.tree_estimation


def is_tree_with_at_least_two_vertices(graph: nx.Graph) -> bool:
    """Return whether the graph is a tree with at least two vertices."""
    return graph.number_of_nodes() >= 2 and nx.is_tree(graph)


def compute_results() -> list[TreeResult]:
    """Compute stacking numbers and tree estimations for all atlas trees."""
    results: list[TreeResult] = []

    for atlas_index, graph in enumerate(nx.graph_atlas_g()):
        if not is_tree_with_at_least_two_vertices(graph):
            continue

        pebbling = Pebbling(graph)
        with redirect_stdout(io.StringIO()):
            stacking_number, _ = pebbling.stacking_number()
        tree_estimation = pebbling.tree_estimation()

        results.append(
            TreeResult(
                atlas_index=atlas_index,
                num_vertices=graph.number_of_nodes(),
                stacking_number=stacking_number,
                tree_estimation=tree_estimation,
            )
        )

    return results


def build_report(results: list[TreeResult]) -> str:
    """Build a standalone LaTeX report from the computed tree data."""
    all_equal = all(result.values_match for result in results)
    failures = [str(result.atlas_index) for result in results if not result.values_match]
    checked_count = len(results)

    rows = []
    for index, result in enumerate(results):
        row_prefix = r"\rowcolor{gray!6} " if index % 2 else ""
        match_text = r"\textsc{Yes}" if result.values_match else r"\textsc{No}"
        rows.append(
            f"{row_prefix}{result.atlas_index} & "
            f"{result.num_vertices} & "
            f"{result.stacking_number} & "
            f"{result.tree_estimation} & "
            f"{match_text} \\\\"
        )

    table_rows = "\n".join(rows)
    equality_sentence = (
        "During the generation of this report, the program checked for each atlas "
        "tree whether the stacking number is equal to the tree estimation. "
        f"For all {checked_count} trees considered here, the two values are equal."
        if all_equal
        else (
            "During the generation of this report, the program checked for each atlas "
            "tree whether the stacking number is equal to the tree estimation. "
            "These two values are not always equal. "
            f"The failing atlas indices are: {', '.join(failures)}."
        )
    )

    return rf"""\documentclass{{amsart}}

\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}
\usepackage[table]{{xcolor}}
\usepackage{{array}}
\usepackage{{tikz}}

\title{{Atlas Tree Estimation Report}}
\author{{}}
\date{{}}

\begin{{document}}

\maketitle

This report compares the stacking number and the tree estimation for every tree
in the NetworkX graph atlas with at least two vertices.

\medskip

{equality_sentence}

\begin{{center}}
\setlength{{\tabcolsep}}{{10pt}}
\renewcommand{{\arraystretch}}{{1.15}}
\begin{{tikzpicture}}
\node[rounded corners=10pt, fill=gray!8, inner sep=10pt] {{
\begin{{tabular}}{{ccccc}}
\toprule
\rowcolor{{gray!20}}
\textbf{{Atlas index}} & \textbf{{$|V(G)|$}} & \textbf{{Stacking}} & \textbf{{Tree estimation}} & \textbf{{Equal?}} \\
\midrule
{table_rows}
\bottomrule
\end{{tabular}}
}};
\end{{tikzpicture}}
\end{{center}}

\end{{document}}
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a LaTeX report for atlas tree estimations."
    )
    parser.add_argument(
        "--output",
        default="atlas_tree_estimation_report.tex",
        help="Path of the generated LaTeX report.",
    )
    return parser.parse_args()


def main() -> None:
    """Compute the data and write the report."""
    args = parse_args()
    results = compute_results()

    with open(args.output, "w", encoding="utf-8") as report_file:
        report_file.write(build_report(results))


if __name__ == "__main__":
    main()
