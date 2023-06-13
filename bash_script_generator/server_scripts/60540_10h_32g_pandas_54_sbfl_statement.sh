#! /usr/bin/env bash

# Exiting when any command fails
set -e


# Inputs for the current buggy program
#--------------------------------------------

PYTHON_V="3.8"
BENCHMARK_NAME="pandas"
BUG_NUMBER="54"
TARGET_DIR="pandas"
TEST_SUITE=(
"pandas/tests/arrays/categorical/test_constructors.py"
"pandas/tests/arrays/categorical/test_dtypes.py"
"pandas/tests/arrays/categorical/test_missing.py"
"pandas/tests/arrays/test_array.py"
"pandas/tests/arrays/test_datetimes.py"
"pandas/tests/arrays/test_period.py"
"pandas/tests/dtypes/cast/test_construct_from_scalar.py"
"pandas/tests/dtypes/cast/test_find_common_type.py"
"pandas/tests/dtypes/cast/test_promote.py"
"pandas/tests/dtypes/test_common.py"
"pandas/tests/dtypes/test_dtypes.py"
"pandas/tests/dtypes/test_missing.py"
"pandas/tests/extension/test_common.py"
"pandas/tests/extension/test_datetime.py"
"pandas/tests/extension/test_interval.py"
"pandas/tests/extension/test_period.py"
"pandas/tests/frame/indexing/test_categorical.py"
"pandas/tests/frame/test_dtypes.py"
"pandas/tests/frame/test_timezones.py"
"pandas/tests/indexes/categorical/test_category.py"
"pandas/tests/indexes/interval/test_astype.py"
"pandas/tests/indexes/interval/test_constructors.py"
"pandas/tests/indexes/multi/test_astype.py"
"pandas/tests/indexes/period/test_constructors.py"
"pandas/tests/indexing/test_categorical.py"
"pandas/tests/io/json/test_json_table_schema.py"
"pandas/tests/io/parser/test_dtypes.py"
"pandas/tests/reshape/merge/test_merge.py"
"pandas/tests/reshape/test_concat.py"
"pandas/tests/series/test_constructors.py"
"pandas/tests/series/test_dtypes.py"
"pandas/tests/test_algos.py"
)
EXCLUDE=(
"pandas/tests"
)
TARGET_FAILING_TESTS=(
"pandas/tests/dtypes/test_dtypes.py::TestCategoricalDtype::test_from_values_or_dtype_invalid_dtype"
)
FAMILY="sbfl"
GRANULARITY="statement"


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
   TEMP_DIR="/scratch/furia/$BENCHMARK_NAME/B${BUG_NUMBER}_F${FAMILY}_G${GRANULARITY}"
else
	 TEMP_DIR="$HOME/temp/fauxpy-temp/$BENCHMARK_NAME/B${BUG_NUMBER}_F${FAMILY}_G${GRANULARITY}"
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

echo "------- Removing the .git directory of the benchmark"
rm -rf .git

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

commentPatternInpytestIni() 
{
    local pytest_ini="pytest.ini"

    if [ -f "$pytest_ini" ]
    then
        cp "$pytest_ini" "$pytest_ini.bak"

        # To handle the final missing new line problem
        echo >> "$pytest_ini"

        local new_lines_list=()
        while IFS= read -r line; do
            local trimed_line=`echo "$line" | xargs`
            # If contains the passed argument and does not start with #
            if [[ "$line" == *"$1"* ]] && [[ "$trimed_line" != "#"* ]]
            then
                new_lines_list+=("# $line")
            else
                new_lines_list+=("$line")
            fi
        done < "$pytest_ini"

        > "$pytest_ini"

        for new_line in "${new_lines_list[@]}"
        do
            echo "$new_line" >> "$pytest_ini"
        done
    fi
}

if [ "$BENCHMARK_NAME" == "cookiecutter" ]
then
    echo "------- Running cookiecutter specific commands"
    # This is a requirement for running tests.

    if [ "$BUG_NUMBER" == "4" ]
    then
        # For bug number 4, I had to make this file from tox.ini.
        wget "https://raw.githubusercontent.com/mohrez86/faux_in_py_subject_fixes/main/fixes/subjects/cookiecutter/B4/test_requirements.txt"
    fi

    pip install -r test_requirements.txt
fi

if [ "$BENCHMARK_NAME" == "sanic" ]
then
    echo "------- Running sanic specific commands"
    # FauxPy is not compatible with pytest-sugar.
    pip uninstall -y pytest-sugar
fi

if [ "$BENCHMARK_NAME" == "httpie" ]
then
    echo "------- Running httpie specific commands"
    # Comment out --tb=native in pytest.ini file.
    # The current version of FauxPy is not compatible with
    # this option.
    $(commentPatternInpytestIni "--tb=native")
fi

if [ "$BENCHMARK_NAME" == "keras" ]
then
    echo "------- Running keras specific commands"
    # Comment out -n 2 option within the pytest.ini file.
    # The corrent version of FauxPy is not compatible with
    # this option.
    $(commentPatternInpytestIni "-n 2")    
fi

if [ "$BENCHMARK_NAME" == "thefuck" ]
then
    echo "------- Running thefuck specific commands"
    # Replace conftest.py with the fixed one.
    # The version of Pytest that FauxPy uses is higher than the one used
    # by these subject. Read the following post for more information.
    # https://stackoverflow.com/questions/54254337/pytest-attributeerror-function-object-has-no-attribute-get-marker
    if [ "$BUG_NUMBER" == "3" ] || 
    [ "$BUG_NUMBER" == "4" ] || 
    [ "$BUG_NUMBER" == "6" ] || 
    [ "$BUG_NUMBER" == "7" ] || 
    [ "$BUG_NUMBER" == "8" ] || 
    [ "$BUG_NUMBER" == "13" ] || 
    [ "$BUG_NUMBER" == "14" ] || 
    [ "$BUG_NUMBER" == "15" ] || 
    [ "$BUG_NUMBER" == "17" ] ||
    [ "$BUG_NUMBER" == "19" ] ||
    [ "$BUG_NUMBER" == "20" ]
    then
        rm -f "tests/conftest.py"
        wget "https://raw.githubusercontent.com/mohrez86/faux_in_py_subject_fixes/main/fixes/subjects/thefuck/B$BUG_NUMBER/conftest.py"
    fi
fi

if [ "$BENCHMARK_NAME" == "luigi" ]
then
    echo "------- Running luigi specific commands"
    # FauxPy is not compatible with pytest-sugar.
    pip uninstall -y pytest-sugar
fi
#------------------------------------------------------------

echo "------- Installing FauxPy"
pip install "$FAUXPY_PATH"
#--------------------------------------------


# Running FauxPy commands
#--------------------------------------------

# statement granularity

echo "------- Running SBFL with statement granularity"
python -m pytest "${TEST_SUITE[@]}"\
                 --src "$TARGET_DIR"\
                 --exclude "$EXCLUDE_LIST"\
                 --granularity "statement"\
                 --family "sbfl"\
                 --failing-list "$TARGET_FAILING_TESTS_LIST" || true



# Copy FL results to home
mkdir -p "$SCRIPT_DIR/$BENCHMARK_NAME/B$BUG_NUMBER"
find "$TEMP_DIR" -type d -name "FauxPyReport*" -exec cp -Rp {} "$SCRIPT_DIR/$BENCHMARK_NAME/B$BUG_NUMBER/" \;


# Delete scratch data
echo rm -rf "$TEMP_DIR/"
rm -rf "$TEMP_DIR/"
