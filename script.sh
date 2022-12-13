#! /usr/bin/bash

# Inputs for the current buggy program
#--------------------------------------------
BENCHMARK_NAME="cookiecutter"

BUG_NUMBER=1

declare -a TARGET_FAILING_TESTS=(
    "tests/test_generate_context.py::test_generate_context_decodes_non_ascii_chars"
    )

TEST_SUITE="tests"

TARGET_DIR="cookiecutter"

VIRTUAL_ENV_PATH="/home/moe/bugsinpyenv36"

FAUXPY_PATH="/home/moe/Desktop/NewStudy/AFL4Python/pytest-FauxPy"
#--------------------------------------------


# Preparing the buggy program
#--------------------------------------------
SCRIPT_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$SCRIPT_DIR"

echo "------- Removing previous results"
find . -type d -name "BugsInPy" | xargs rm -rf
find . -type d -name "$BENCHMARK_NAME" | xargs rm -rf
find . -type d -name "FauxPyReport*" | xargs rm -rf

echo "------- Cloning BugsInPy"
git clone https://github.com/soarsmu/BugsInPy

echo "------- Checking out the buggy program"
BugsInPy/framework/bin/bugsinpy-checkout -p "$BENCHMARK_NAME" -i "$BUG_NUMBER" -v 0 -w "$SCRIPT_DIR"

cd "$BENCHMARK_NAME"

source "$VIRTUAL_ENV_PATH/bin/activate"
python --version

echo "------- Compiling the buggy program"
bugsinpy-compile

source "env/bin/activate"
python --version

pip install --upgrade pip
pip install wheel

#----------- Benchmark specific commands -----------
if [ "$BENCHMARK_NAME" == "cookiecutter" ]
then
    echo "------- Running cookiecutter specific commands"
    pip install -r test_requirements.txt
fi
#------------------------------------------------------------

echo "------- Installing FauxPy"
pip install "$FAUXPY_PATH"
#--------------------------------------------


# Running FauxPy commands
# NOTE: the 7 experiments must not run in parallel
#--------------------------------------------
# Statement granularity
declare -a STATEMENT_FAIMILIES=("sbfl" "mbfl" "ps")

for family in "${STATEMENT_FAIMILIES[@]}"
do
    echo "------- Running $family with statement granularity"
    python -m pytest "$TEST_SUITE" --src "$TARGET_DIR" --granularity statement --family "$family"
done


# Function granularity
declare -a FUNCTION_FAIMILIES=("sbfl" "mbfl" "ps" "st")

for family in "${FUNCTION_FAIMILIES[@]}"
do
    echo "------- Running $family with function granularity"
    python -m pytest "$TEST_SUITE" --src "$TARGET_DIR" --granularity function --family "$family"
done
