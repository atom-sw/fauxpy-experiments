#! /usr/bin/env bash

# Exiting when any command fails
set -e

# Constants
#--------------------------------------------
TEST_OUTPUT_FILE_STDOUT="bugsinpy_test_output_stdout.txt"
TEST_OUTPUT_FILE_STDERR="bugsinpy_test_output_stderr.txt"
REMOTE_URL_FILE_PATH="bugsinpy_remote_url.txt"
WORKSPACE_FILE_NAME="workspace.json"


# Inputs for the current project
#--------------------------------------------

if [ $# -eq 0 ]
then
    echo "Pass the project info file (e.g., keras.json)"
    exit -1
fi

WORKSPACE_PATH=`jq '.WORKSPACE_PATH' $WORKSPACE_FILE_NAME | tr -d '"'`
BENCHMARK_NAME=`jq '.BENCHMARK_NAME' $1 | tr -d '"'`
BUG_NUMBER_START=`jq '.BUG_NUMBER_START' $1`
BUG_NUMBER_END=`jq '.BUG_NUMBER_END' $1`
VIRTUAL_ENV=`jq '.VIRTUAL_ENV' $1 | tr -d '"'`

echo "WORKSPACE_PATH: $WORKSPACE_PATH"
echo "BENCHMARK_NAME: $BENCHMARK_NAME"
echo "BUG_NUMBER_START: $BUG_NUMBER_START"
echo "BUG_NUMBER_END: $BUG_NUMBER_END"
echo "VIRTUAL_ENV: $VIRTUAL_ENV"



# Execution commands
#--------------------------------------------

echo ">>>>>>>activate virtual environment $VIRTUAL_ENV"
source "$VIRTUAL_ENV/bin/activate"
python --version

for (( bug="$BUG_NUMBER_START"; bug<="$BUG_NUMBER_END"; bug++))
do
    echo ">>>>>>>make directories for $BENCHMARK_NAME bug number $bug"
    BUGGY_PATH="$WORKSPACE_PATH/$BENCHMARK_NAME/bug$bug/buggy"
    FIXED_PATH="$WORKSPACE_PATH/$BENCHMARK_NAME/bug$bug/fixed"
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

    echo ">>>>>>>get the remote url for the buggy version of $BENCHMARK_NAME bug number $bug"
    git config --get remote.origin.url | tee "$REMOTE_URL_FILE_PATH"

    echo ">>>>>>>compile the fixed version of $BENCHMARK_NAME bug number $bug"
    cd "$FIXED_PATH/$BENCHMARK_NAME"
    bugsinpy-compile

    echo ">>>>>>>run BugsInPy Test for the fixed version of $BENCHMARK_NAME bug number $bug"
    bugsinpy-test 2> "$TEST_OUTPUT_FILE_STDERR" 1> "$TEST_OUTPUT_FILE_STDOUT"

    echo ">>>>>>>get the remote url for the fixed version of $BENCHMARK_NAME bug number $bug"
    git config --get remote.origin.url | tee "$REMOTE_URL_FILE_PATH"
done

