# SFILES 2.0 
This repository is published together with the paper: *SFILES 2.0: An extended text-based flowsheet representation*<br>
The repository contains functionality for the conversion between PFD-graphs/P&ID-graphs and SFILES 2.0 strings. In the paper, we describe the structure of the graphs, notation rules of the SFILES 2.0, and the conversion algorithm.  

## Installation

To install the SFILES 2.0 package via `pip`, simply run:

```sh
pip install SFILES2
```

## Exploring the Repository and Demonstrations

For users who want to explore the functionality with the provided demonstrations and example files:
```sh
git clone https://github.com/process-intelligence-research/SFILES2.git
```

After creating and activating a new virtual environment (python 3.9), you can use the pyproject.toml file to install all required packages:
```sh
pip install .
```
### Demonstration of functionality
You can either have a look at the `demonstration.ipynb` which demonstrates SFILES 2.0 strings for a variety of PFDs and P&IDs or run the python file `run_demonstration.py`.

## Flowsheet Builder

This repository includes a graphical Flowsheet Builder tool that allows you to create and visualize chemical process flowsheets without needing to know the SFILES 2.0 notation directly.

To use the Flowsheet Builder:
```sh
streamlit run flowsheet_builder.py
```

### Key Features
- Add and manage process units with customizable types and names
- Create and visualize streams between units
- Support for branches (multiple outputs from one unit)
- Support for joins (multiple inputs to one unit)
- Create recycle streams
- Import/Export SFILES 2.0 strings
- Real-time visualization of the flowsheet

See [README_FLOWSHEET_BUILDER.md](README_FLOWSHEET_BUILDER.md) for more details on features and usage.

## References

If you use this package or find it helpful in your research, please consider citing:

```text
@article{vogel2023sfiles,
  title={SFILES 2.0: an extended text-based flowsheet representation},
  author={Vogel, Gabriel and Hirtreiter, Edwin and Schulze Balhorn, Lukas and Schweidtmann, Artur M},
  journal={Optimization and Engineering},
  volume={24},
  number={4},
  pages={2911--2933},
  year={2023},
  publisher={Springer}
}
```