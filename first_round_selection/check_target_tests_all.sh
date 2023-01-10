#! /usr/bin/env bash

# Exiting when any command fails
set -e

# Constants
#--------------------------------------------
INFO_DIR="info"
OUTPUT_LOG_DIR="target_tests_log"

# Execution commands
#--------------------------------------------

if [ -d "$OUTPUT_LOG_DIR" ]; then
  echo "Removing the previous target tests log results..."
  rm -rf "$OUTPUT_LOG_DIR"
fi

mkdir "$OUTPUT_LOG_DIR"

for filename in "$INFO_DIR"/*.json; do
  log_file_name="${filename:5}.log"
  python check_target_tests.py "$filename" 2>&1 | tee "$OUTPUT_LOG_DIR"/"$log_file_name"
done

