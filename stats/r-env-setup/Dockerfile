FROM continuumio/miniconda3

## configure timezone
ENV TZ="Europe/Zurich"

## project name
ARG CONTENT_DIR="data-analysis"

## to run APT without user input (only when building)
ARG DEBIAN_FRONTEND="noninteractive"

ARG SCRIPTS_DIR="scripts"
ARG BASH_BOOTSTRAP="bash-bootstrap.sh"
ARG R_BOOTSTRAP="r-bootstrap.R"

# Copy bootstrap scripts
RUN mkdir -p "/$SCRIPTS_DIR"
COPY "$SCRIPTS_DIR/$BASH_BOOTSTRAP" "/$SCRIPTS_DIR"
COPY "$SCRIPTS_DIR/$R_BOOTSTRAP" "/$SCRIPTS_DIR"

WORKDIR "/$SCRIPTS_DIR"
# Run Bash bootstrap script, which installs the Conda packages and other system dependencies
RUN chmod +x "$BASH_BOOTSTRAP"
RUN "./$BASH_BOOTSTRAP"
# Run R bootstrap script, which install all other R packages directly in R
RUN chmod +x "$R_BOOTSTRAP"
RUN Rscript "$R_BOOTSTRAP"

# Copy analysis data and scripts
RUN cd "/" && mkdir -p "/$CONTENT_DIR"
COPY "$CONTENT_DIR/" "/$CONTENT_DIR"

WORKDIR "/$CONTENT_DIR"
