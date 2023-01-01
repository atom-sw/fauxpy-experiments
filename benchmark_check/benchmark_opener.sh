#! /usr/bin/env bash

# Exiting when any command fails
set -e

# Inputs for the current project
#--------------------------------------------

BENCHMARK_NAME="keras"
BUG_NUMBER_START="1"
BUG_NUMBER_END="10"
WORKSPACE_PATH="/home/moe/BugsInPyExp/7.keras"
VIRTUAL_ENV="/home/moe/bugsinpyenv37"
TEST_OUTPUT_FILE_STDOUT="bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR="bugsinpy_test_output_stderr.txt"


# Execution commands
#--------------------------------------------

echo ">>>>>>>activate virtual environment $VIRTUAL_ENV"
source "$VIRTUAL_ENV/bin/activate"
python --version

for (( bug="$BUG_NUMBER_START"; bug<="$BUG_NUMBER_END"; bug++))
do
    echo ">>>>>>>make directories for $BENCHMARK_NAME bug number $bug"
    BUGGY_PATH="$WORKSPACE_PATH/bug$bug/buggy"
    FIXED_PATH="$WORKSPACE_PATH/bug$bug/fixed"
    mkdir -p "$BUGGY_PATH"
    mkdir -p "$FIXED_PATH"

    echo ">>>>>>>checkout the buggy version of $BENCHMARK_NAME bug number $bug"
    bugsinpy-checkout -p "$BENCHMARK_NAME" -i "$bug" -v 0 -w "$BUGGY_PATH"

    echo ">>>>>>>checkout the fixed version of $BENCHMARK_NAME bug number $bug"
    bugsinpy-checkout -p "$BENCHMARK_NAME" -i "$bug" -v 1 -w "$FIXED_PATH"

    echo ">>>>>>>compile the buggy version of $BENCHMARK_NAME bug number $bug"
    cd "$BUGGY_PATH/$BENCHMARK_NAME"
    bugsinpy-compile
    
    echo ">>>>>>>run BugsInPy Test for the buggy version of $BENCHMARK_NAME bug number $bug"
    bugsinpy-test 2> "$TEST_OUTPUT_FILE_STDERR" 1> "$TEST_OUTPUT_FILE_STDOUT"

    echo ">>>>>>>compile the buggy version of $BENCHMARK_NAME bug number $bug"
    cd "$FIXED_PATH/$BENCHMARK_NAME"
    bugsinpy-compile

    echo ">>>>>>>run BugsInPy Test for the fixed version of $BENCHMARK_NAME bug number $bug"
    bugsinpy-test 2> "$TEST_OUTPUT_FILE_STDERR" 1> "$TEST_OUTPUT_FILE_STDOUT"
done

