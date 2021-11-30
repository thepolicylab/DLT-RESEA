# DLT-RESEA

This repository contains code that was used to analyze the impact of Rhode Island’s Reemployment Services and Eligibility Assessments (RESEA) on career outcomes for participants. This README provides instructions on replicating the analysis.

## Context

Reemployment Services and Eligibility Assessment (RESEA) programs, supported by federal funding, support individuals who are out of work and most likely to exhaust Unemployment Insurance (UI) benefits by helping them get back into meaningful employment faster. In 2018, the U.S. Department of Labor (DOL) began requiring states to implement RESEA programming shown to be effective with strong causal evidence, or to prove through evaluation that their program is causally associated with positive outcomes. The Rhode Island Depart of Labor and Training’s (DLT) RESEA program places selected UI recipients in a required meeting with a career counselor who will support them developing their resume, walk them through potential job opportunities, introduce them to State assistance they may be eligible for (e.g., childcare and transportation), and teach them to locate a new job in an increasingly virtual environment. For further information regarding the project's scope and methodology, please refer to the pre-analysis plan posted on [OSF](https://osf.io/c9xe8/).


## Requirements

### Software

The code in this repository comes in several languages. In particular, you will need:
  * Python 3.8+
  * Rust 1.56+

For instructions on installing Rust, see [their installation page](https://www.rust-lang.org/tools/install). For instructions on installing Python, we highly recommend [pyenv](https://github.com/pyenv/pyenv-installer).

Once Python is installed, our dependencies are managed with [poetry](https://python-poetry.org/). Installation instructions are available [here](https://python-poetry.org/docs/).

Once poetry is installed, to install all dependencies, run:

```bash
poetry install
cargo build --release
```

## Repository layout

### `/PreAnalysis`

This folder contains the code for replicating Appendix 2 (the power analysis) and Appendix 3 (the randomizer analysis) of our pre-analysis plan. These are simple jupyter notebooks and so can be run by opening a jupyter kernel:

```bash
poetry run jupyter notebook
```

opening the notebooks and choosing "Restart and Run All".

### `/src`

This folder contains source code associated with the analysis.

The `dlt` folder contains the source of a Python package (installed locally by poetry and importable as `dlt`) that has many helper functions utilized in the analysis.

The `notebooks` folder contains a jupyter notebook that is currently a placeholder for reading data from DLT in the final analysis.

The `rust` folder contains our rust code, which simply checks the injectivity of DLT's hash function. See the Appendix 3 notebook in the `/PreAnalysis` folder for more details.

### `/tests`

This folder contains various tests that we have written to test our code. They may be run using:

```bash
poetry run py.test
```

## License

MIT License. For more info, see the LICENSE file.
