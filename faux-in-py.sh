#! /usr/bin/env bash

# Exiting when any command fails
set -e


# Inputs for the current buggy program
#--------------------------------------------
BENCHMARK_NAME="cookiecutter"

BUG_NUMBER=1

TARGET_FAILING_TESTS=(
    "tests/test_generate_context.py::test_generate_context_decodes_non_ascii_chars"
    )

TEST_SUITE="tests"

TARGET_DIR="cookiecutter"

EXCLUDE=(
)

PYTHON_V="3.6"


# A function to convert Bash lists to Python lists
#--------------------------------------------
bash2python()
{
    local bashList=("$@")
    local firstElement=$(echo $bashList | cut -d" " -f1)
    local pythonList="$firstElement"

    for i in "${!bashList[@]}"
    do
        if [ $i -ne 0 ]
        then
            pythonList="$pythonList,${bashList[$i]}"
        fi
    done

    pythonList="[$pythonList]"
    echo $pythonList
}

TARGET_FAILING_TESTS_LIST=$(bash2python "${TARGET_FAILING_TESTS[@]}")
EXCLUDE_LIST=$(bash2python "${EXCLUDE[@]}")


# Preparing the buggy program
#--------------------------------------------
SCRIPT_DIR="$(dirname $(readlink -f "${BASH_SOURCE[0]}"))"
HOSTNAME=$(hostname)
if [[ "$HOSTNAME" =~ ics.* ]]; then
	 TEMP_DIR="/scratch/furia/$BENCHMARK_NAME/B$BUG_NUMBER"
else
	 TEMP_DIR="$HOME/temp/fauxpy-temp/$BENCHMARK_NAME/B$BUG_NUMBER"
fi

# Remove a previous run's temp data, if it exists
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

VENV_V="$(echo "$PYTHON_V" | sed 's/[.]//')"
VENV_DIR="$SCRIPT_DIR/../bugsinpyenv$VENV_V"

FAUXPY_PATH="$SCRIPT_DIR/pytest-FauxPy"

echo "------- Cloning BugsInPy"
git clone https://github.com/soarsmu/BugsInPy

echo "------- Checking out the buggy program"
./BugsInPy/framework/bin/bugsinpy-checkout -p "$BENCHMARK_NAME" -i "$BUG_NUMBER" -v 0 -w "$TEMP_DIR"

cd "$BENCHMARK_NAME"

source "$VENV_DIR/bin/activate"
python --version

echo "------- Compiling the buggy program"
../BugsInPy/framework/bin/bugsinpy-compile

if [ -f "$HOME/_bashrc" ]; then
	 echo "------ Restoring clean .bashrc"
	 cp "$HOME/_bashrc" "$HOME/.bashrc"
else
	 echo "------ ERROR: Could not find clean .bashrc to restore"
	 echo "              Copy a clean version of .bashrc to $HOME/_bashrc"
	 exit 1
fi

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

echo "------- Running SBFL with statement granularity"
python -m pytest "$TEST_SUITE"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "statement"\
                 --family "sbfl"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

echo "------- Running MBFL with statement granularity"
python -m pytest "$TEST_SUITE"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "statement"\
                 --family "mbfl"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

echo "------- Running PS with statement granularity"
python -m pytest "${TARGET_FAILING_TESTS[@]}"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "statement"\
                 --family "ps"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

# Function granularity

echo "------- Running SBFL with function granularity"
python -m pytest "$TEST_SUITE"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "function"\
                 --family "sbfl"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

echo "------- Running MBFL with function granularity"
python -m pytest "$TEST_SUITE"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "function"\
                 --family "mbfl"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

echo "------- Running PS with function granularity"
python -m pytest "${TARGET_FAILING_TESTS[@]}"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "function"\
                 --family "ps"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true

echo "------- Running ST with function granularity"
python -m pytest "${TARGET_FAILING_TESTS[@]}"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "function"\
                 --family "st"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true


# Copy FL results to home
mkdir -p "$SCRIPT_DIR/$BENCHMARK_NAME/B$BUG_NUMBER"
find "$TEMP_DIR" -type d -name "FauxPyReport*" -exec cp -Rp {} "$SCRIPT_DIR/$BENCHMARK_NAME/B$BUG_NUMBER/" \;


# Delete scratch data
echo rm -rf "$TEMP_DIR/"
rm -rf "$TEMP_DIR/"
