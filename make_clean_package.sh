#! /usr/bin/env bash

# Exiting when any command fails
set -e

PACKAGE_NAME="fauxpy_experiments"
TEMP_DIRECTORY="/tmp/$PACKAGE_NAME"

CLEAN_PACKAGE_DIR="clean_package"

FILES_TO_REMOVE=(
"bugsinpy_project_types.csv"
"curbatch"
"donezo.sh"
"faux-in-py.sh"
"make_clean_package.sh"
"slurm-runner.cmd"
".git"
)

SCRIPT_DIR="$(dirname $(readlink -f "${BASH_SOURCE[0]}"))"

if [ -d "$TEMP_DIRECTORY" ]; then
  rm -rf "$TEMP_DIRECTORY"
fi

mkdir "$TEMP_DIRECTORY"

cp -r . "$TEMP_DIRECTORY"

cd "$TEMP_DIRECTORY"

# Remove all .gitignore files in tmp version
ALL_GITIGNORE_FILES=$(find -type f -name '.gitignore')
for item in "${ALL_GITIGNORE_FILES[@]}"; do
    echo "$item"
    rm -rf "$item"
done

# Remove the unwanted files in the tmp version
for item in "${FILES_TO_REMOVE[@]}"; do
    echo "$item"
    rm -rf "$item"
done

# Remove CLEAN_PACKAGE_DIR in the tmp version
if [ -d "$CLEAN_PACKAGE_DIR" ]; then
  "$CLEAN_PACKAGE_DIR"
  rm -rf "$CLEAN_PACKAGE_DIR"
fi

cd "$SCRIPT_DIR"

if [ -d "$CLEAN_PACKAGE_DIR" ]; then
  rm -rf "$CLEAN_PACKAGE_DIR"
fi

mkdir "$CLEAN_PACKAGE_DIR"

cp -r "$TEMP_DIRECTORY" "$CLEAN_PACKAGE_DIR/$PACKAGE_NAME"
