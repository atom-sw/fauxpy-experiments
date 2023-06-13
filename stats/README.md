# Statistical analysis

This directory contains:

- An RMarkdown script `pyfl.Rmd` that runs a detailed statistical analysis on the Python fault localization data presented in other parts of this repository.

- The corresponding knitted file `pyfl.html`.

If you want to rerun the analysis, you need an R environment configured with all the dependencies. To this end, you can use the content of subdirectory `r-env-setup`:

1. Building the `Dockerfile` creates a Docker image with R and all dependencies installed.

2. Alternatively, you can install the same dependencies on your system following the scripts `bash-bootstrap.sh` followed by `r-bootstrap.R` (which are used by the `Dockerfile`).
