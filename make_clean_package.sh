#! /usr/bin/env bash

# Exiting when any command fails
set -e

TEMP_DIRECTORY="/tmp/fauxpy_replication_package"


if [ -d "$TEMP_DIRECTORY" ]; then
  rm -rf "$TEMP_DIRECTORY"
fi

mkdir "$TEMP_DIRECTORY"

cp -r . "$TEMP_DIRECTORY"

cd "$TEMP_DIRECTORY"

# Remove all .gitignore files
ALL_GITIGNORE_FILES=$(find -type f -name '.gitignore')
for item in "${ALL_GITIGNORE_FILES[@]}"; do
    echo "$item"
    rm -rf "$item"
done

# Remove the following files
FILES_TO_REMOVE=(
"bugsinpy_project_types.csv"
"curbatch"
"donezo.sh"
"faux-in-py.sh"
"make_clean_package.sh"
"slurm-runner.cmd"
".git"
)

for item in "${FILES_TO_REMOVE[@]}"; do
    echo "$item"
    rm -rf "$item"
done

