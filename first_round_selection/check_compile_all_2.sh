#! /usr/bin/env bash

# Exiting when any command fails
set -e

# Constants
#--------------------------------------------
INFO_DIR="info_2"
OUTPUT_LOG_DIR="compile_log_2"

# Execution commands
#--------------------------------------------

if [ -d "$OUTPUT_LOG_DIR" ]; then
  echo "Removing the previous compile log results..."
  rm -rf "$OUTPUT_LOG_DIR"
fi

mkdir "$OUTPUT_LOG_DIR"

for filename in "$INFO_DIR"/*.json; do
  log_file_name="${filename:7}.log"
  python check_compile.py "$filename" 2>&1 | tee "$OUTPUT_LOG_DIR"/"$log_file_name"
done

