#! /usr/bin/env bash

# Exiting when any command fails
set -e

# Constants
#--------------------------------------------
INFO_DIR="info"
COMPILE_LOG_DIR="compile_log"

# Execution commands
#--------------------------------------------

if [ -d "$COMPILE_LOG_DIR" ]; then
  echo "Removing the previous compile log results..."
  rm -rf "$COMPILE_LOG_DIR"
fi

mkdir "$COMPILE_LOG_DIR"

for filename in "$INFO_DIR"/*.json; do
  log_file_name="${filename:5}.log"
  python check_compile.py "$filename" 2>&1 | tee "$COMPILE_LOG_DIR"/"$log_file_name"
done

