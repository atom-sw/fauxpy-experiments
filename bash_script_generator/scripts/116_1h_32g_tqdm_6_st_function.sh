#! /usr/bin/env bash

# Exiting when any command fails
set -e


# Inputs for the current buggy program
#--------------------------------------------

PYTHON_V="3.6"
BENCHMARK_NAME="tqdm"
BUG_NUMBER="6"
TARGET_DIR="tqdm"
TEST_SUITE=(
"tqdm/tests"
)
EXCLUDE=(
"tqdm/tests"
)
TARGET_FAILING_TESTS=(
"tqdm/tests/test_synchronisation.py::test_imap"
)
FAMILY="st"
GRANULARITY="function"


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

    if [ "$BUG_NUMBER" == "5" ]
    then
        # Bug number 5 is very old.
        # Current versions of Pytest do not collect
        # test modlues which have names starting with tests or their
        # names are only test.py
        cp tests/tests.py tests/test_all.py
    fi

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
    # Remove three test files that have errors.
    rm -f "tests/rules/test_git_checkout.py"
    rm -f "tests/rules/test_git_two_dashes.py"
    rm -f "tests/rules/test_touch.py"

    # Replace conftest.py with the fixed one.
    # The version of Pytest that FauxPy uses is higher than the one used
    # by this subject. Read the following post for more information.
    # https://stackoverflow.com/questions/54254337/pytest-attributeerror-function-object-has-no-attribute-get-marker
    rm -f "tests/conftest.py"
    wget "https://raw.githubusercontent.com/mohrez86/faux_in_py_subject_fixes/main/fixes/subjects/thefuck/B$BUG_NUMBER/conftest.py"
fi

if [ "$BENCHMARK_NAME" == "fastapi" ]
then
    echo "------- Running fastapi specific commands"
    # Update pip (which is done before this command).
    # Remove the test package tests/test_tutorial.
    # These tests have bugs and stops Pytest.
    rm -rf "tests/test_tutorial"
fi

if [ "$BENCHMARK_NAME" == "tqdm" ]
then
    echo "------- Running tqdm specific commands"
    # Make a copy of every test module and change the names from tests* to test*.
    # The reason to make this change is that Pytest cannot collect 
    # test modules starting with "tests_".
    for TEST_FILE_NAME in tqdm/tests/test*
    do
        NEW_FILE_NAME="${TEST_FILE_NAME/tests_/test_}"
        cp "$TEST_FILE_NAME" "$NEW_FILE_NAME"
    done
fi

if [ "$BENCHMARK_NAME" == "youtube-dl" ]
then
    echo "------- Running youtube-dl specific commands"
    # Remove test/test_download.py because it is too slow.
    # It is not necessary thought.
    rm -rf "test/test_download.py"
fi
#------------------------------------------------------------

echo "------- Installing FauxPy"
pip install "$FAUXPY_PATH"
#--------------------------------------------


# Running FauxPy commands
#--------------------------------------------

# function granularity

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
