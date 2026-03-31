"""Generate a LaTeX summary report for pebbling tests on the graph atlas."""

from __future__ import annotations

import argparse
import io
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass

import networkx as nx

from pebbling import Pebbling


@dataclass
class TestSummary:
    """Store aggregate test results for the graph atlas."""

    total_graphs: int = 0
    connected_graphs: int = 0
    non_bipartite_graphs: int = 0
    stacked_successes: int = 0
    stacked_failures: int = 0
    clear_successes: int = 0
    clear_failures: int = 0
    stacked_failure_ids: list[int] | None = None
    clear_failure_ids: list[int] | None = None

    def __post_init__(self) -> None:
        if self.stacked_failure_ids is None:
            self.stacked_failure_ids = []
        if self.clear_failure_ids is None:
            self.clear_failure_ids = []


def evaluate_connected_atlas_graphs(
    limit: int | None = None,
    progress_every: int = 0,
) -> TestSummary:
    """Run the pebbling checks on every connected graph in the NetworkX atlas."""
    summary = TestSummary()

    for atlas_index, graph in enumerate(nx.graph_atlas_g()):
        if limit is not None and summary.total_graphs >= limit:
            break

        summary.total_graphs += 1

        if progress_every and summary.total_graphs % progress_every == 0:
            print(
                f"Processed {summary.total_graphs} atlas graphs...",
                file=sys.stderr,
                flush=True,
            )

        if graph.number_of_nodes() < 2 or not nx.is_connected(graph):
            continue

        summary.connected_graphs += 1
        pebbling = Pebbling(graph)

        with redirect_stdout(io.StringIO()):
            if pebbling.is_critical_stacked_almost_stacked():
                summary.stacked_successes += 1
            else:
                summary.stacked_failures += 1
                summary.stacked_failure_ids.append(atlas_index)

            if not nx.is_bipartite(graph):
                summary.non_bipartite_graphs += 1
                if pebbling.is_critical_clear_almost_stacked():
                    summary.clear_successes += 1
                else:
                    summary.clear_failures += 1
                    summary.clear_failure_ids.append(atlas_index)

    return summary


def format_id_list(values: list[int]) -> str:
    """Format atlas indices for LaTeX output."""
    if not values:
        return "none"
    return ", ".join(str(value) for value in values)


def build_report(summary: TestSummary) -> str:
    """Return a standalone LaTeX report for the computed summary."""
    return rf"""\documentclass{{amsart}}

\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}

\title{{Pebbling Atlas Report}}
\author{{}}
\date{{}}

\begin{{document}}

\maketitle

This report summarizes the pebbling tests over the NetworkX graph atlas.
Only connected graphs with at least two vertices are processed by the program.

\section*{{Counts}}

\begin{{center}}
\begin{{tabular}}{{lr}}
\toprule
Quantity & Count \\
\midrule
Graphs in the NetworkX atlas & {summary.total_graphs} \\
Connected graphs tested & {summary.connected_graphs} \\
Connected non-bipartite graphs tested & {summary.non_bipartite_graphs} \\
Successful stacked-almost-stacked tests & {summary.stacked_successes} \\
Unsuccessful stacked-almost-stacked tests & {summary.stacked_failures} \\
Successful clear-almost-stacked tests & {summary.clear_successes} \\
Unsuccessful clear-almost-stacked tests & {summary.clear_failures} \\
\bottomrule
\end{{tabular}}
\end{{center}}

\section*{{Failures}}

Atlas indices failing \texttt{{is\_critical\_stacked\_almost\_stacked}}:
\[
\text{{{format_id_list(summary.stacked_failure_ids)}}}
\]

Atlas indices failing \texttt{{is\_critical\_clear\_almost\_stacked}}:
\[
\text{{{format_id_list(summary.clear_failure_ids)}}}
\]

\end{{document}}
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a LaTeX pebbling report for graph atlas graphs."
    )
    parser.add_argument(
        "--output",
        default="atlas_pebbling_report.tex",
        help="Path of the generated LaTeX report.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap on the number of atlas graphs examined.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=25,
        help="Print a progress message after this many atlas graphs.",
    )
    return parser.parse_args()


def main() -> None:
    """Compute the atlas summary and write the LaTeX report."""
    args = parse_args()
    summary = evaluate_connected_atlas_graphs(
        limit=args.limit,
        progress_every=args.progress_every,
    )

    with open(args.output, "w", encoding="utf-8") as report_file:
        report_file.write(build_report(summary))


if __name__ == "__main__":
    main()
