#! /usr/bin/env bash

# Exiting when any command fails
set -e

# Constants
#--------------------------------------------
INFO_DIR="info"

# Execution commands
#--------------------------------------------

for filename in "$INFO_DIR"/*.json; do
  python check_target_tests.py "$filename"
done

