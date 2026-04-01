# Pebbling Computations

This repository contains Python code for pebbling computations on finite graphs,
together with scripts that generate LaTeX reports used in the paper.

## Main files

- `pebbling.py`: core `Pebbling` class and helper functions
- `test_pebbling.py`: unit tests
- `atlas_ash_report.py`: generates a LaTeX report for almost stacked hypothesis checks on connected graphs in the NetworkX graph atlas
- `atlas_tree_estimation.py`: generates a LaTeX report comparing `stacking_number` and `tree_estimation` on atlas trees
- `special_graph_pebbling_report.py`: generates a LaTeX report for selected graph families

## How to run

Generate the atlas report:

```bash
python atlas_ash_report.py
```

Generate the tree estimation report:

```bash
python atlas_tree_estimation.py
```

Generate the selected-graphs report:

```bash
python special_graph_pebbling_report.py
```

Run the tests:

```bash
pytest
```

## Generated reports

The scripts above write LaTeX files in the current directory:

- `atlas_ash_report.tex`
- `atlas_tree_estimation_report.tex`
- `special_graph_pebbling_report.tex`

These files can be compiled with `pdflatex` if desired.
