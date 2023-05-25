#! /usr/bin/env bash

R_V="4.2.3"

apt update
apt -y upgrade

# Dependencies for Stan
apt -y --no-install-recommends install gcc g++ gcc-10 g++-10 cmake

conda config --add channels conda-forge
conda config --set channel_priority strict
conda install r-base="$R_V" r-devtools r-codetools r-v8 emacs pandoc
