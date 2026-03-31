"""Generate a LaTeX report of pebbling numbers for selected NetworkX graphs."""

from __future__ import annotations

import argparse
import io
from contextlib import redirect_stdout
from dataclasses import dataclass

import networkx as nx

from pebbling import Pebbling


@dataclass
class GraphResult:
    """Store the computed data for one graph."""

    name: str
    num_vertices: int
    bipartite: bool
    stacking_number: int
    clearing_number: int | None


def latex_graph_name(name: str) -> str:
    """Return a math-mode LaTeX version of a graph name."""
    return f"${name}$"


def selected_graphs() -> list[tuple[str, nx.Graph]]:
    """Return the requested family of graphs."""
    return [
        ("P_2", nx.path_graph(2)),
        ("P_3", nx.path_graph(3)),
        ("P_4", nx.path_graph(4)),
        ("P_5", nx.path_graph(5)),
        ("K_3", nx.complete_graph(3)),
        ("K_4", nx.complete_graph(4)),
        ("K_5", nx.complete_graph(5)),
        ("K_{1,3}", nx.star_graph(3)),
        ("K_{1,4}", nx.star_graph(4)),
        ("K_{2,4}", nx.complete_multipartite_graph(2, 4)),
        ("K_{2,3,4}", nx.complete_multipartite_graph(2, 3, 4)),
        ("C_3", nx.cycle_graph(3)),
        ("C_4", nx.cycle_graph(4)),
        ("C_5", nx.cycle_graph(5)),
        ("C_6", nx.cycle_graph(6)),
        ("C_7", nx.cycle_graph(7)),
        ("C_8", nx.cycle_graph(8)),
    ]


def compute_results() -> list[GraphResult]:
    """Compute stacking and clearing numbers for the selected graphs."""
    results: list[GraphResult] = []

    for name, graph in selected_graphs():
        pebbling = Pebbling(graph)
        bipartite = nx.is_bipartite(graph)

        with redirect_stdout(io.StringIO()):
            stacking_number, _stacking_witness = pebbling.stacking_number()
            clearing_number: int | None = None
            if not bipartite:
                clearing_number, _clearing_witness = pebbling.clearing_number()

        results.append(
            GraphResult(
                name=name,
                num_vertices=graph.number_of_nodes(),
                bipartite=bipartite,
                stacking_number=stacking_number,
                clearing_number=clearing_number,
            )
        )

    return results


def build_report(results: list[GraphResult]) -> str:
    """Build a standalone LaTeX report containing the computed table."""
    rows = []
    for index, result in enumerate(results):
        clearing_value = "--" if result.clearing_number is None else str(result.clearing_number)
        bipartite_value = r"\textsc{Yes}" if result.bipartite else r"\textsc{No}"
        row_prefix = r"\rowcolor{gray!6} " if index % 2 else ""
        rows.append(
            f"{row_prefix}{latex_graph_name(result.name)} & {result.num_vertices} & "
            f"{bipartite_value} & {result.stacking_number} & {clearing_value} \\\\"
        )

    table_rows = "\n".join(rows)

    return rf"""\documentclass{{amsart}}

\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}
\usepackage[table]{{xcolor}}
\usepackage{{array}}
\usepackage{{tikz}}

\title{{Pebbling Report for Selected Graphs}}
\author{{}}
\date{{}}

\begin{{document}}

\maketitle

The table below records the stacking number for each selected graph.
For non-bipartite graphs it also records the clearing number.

\begin{{center}}
\setlength{{\tabcolsep}}{{10pt}}
\renewcommand{{\arraystretch}}{{1.2}}
\begin{{tikzpicture}}
\node[rounded corners=10pt, fill=gray!8, inner sep=10pt] {{
\begin{{tabular}}{{>{{\raggedright\arraybackslash}}p{{2.6cm}}cccc}}
\toprule
\rowcolor{{gray!20}}
\textbf{{Graph}} & \textbf{{$|V(G)|$}} & \textbf{{Bipartite}} & \textbf{{Stacking}} & \textbf{{Clearing}} \\
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
        description="Generate a LaTeX pebbling report for selected graphs."
    )
    parser.add_argument(
        "--output",
        default="special_graph_pebbling_report.tex",
        help="Path of the generated LaTeX report.",
    )
    return parser.parse_args()


def main() -> None:
    """Compute the data and write the LaTeX report."""
    args = parse_args()
    results = compute_results()

    with open(args.output, "w", encoding="utf-8") as report_file:
        report_file.write(build_report(results))


if __name__ == "__main__":
    main()
