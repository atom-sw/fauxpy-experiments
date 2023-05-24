#! /usr/bin/env bash

# Exiting when any command fails
set -e


# Inputs for the current buggy program
#--------------------------------------------

PYTHON_V="3.8"
BENCHMARK_NAME="fastapi"
BUG_NUMBER="1"
TARGET_DIR="fastapi"
TEST_SUITE=(
"tests/test_additional_properties.py"
"tests/test_additional_response_extra.py"
"tests/test_additional_responses_bad.py"
"tests/test_additional_responses_custom_validationerror.py"
"tests/test_additional_responses_default_validationerror.py"
"tests/test_additional_responses_response_class.py"
"tests/test_additional_responses_router.py"
"tests/test_callable_endpoint.py"
"tests/test_custom_route_class.py"
"tests/test_custom_swagger_ui_redirect.py"
"tests/test_datetime_custom_encoder.py"
"tests/test_default_response_class.py"
"tests/test_default_response_class_router.py"
"tests/test_dependency_cache.py"
"tests/test_dependency_class.py"
"tests/test_dependency_contextmanager.py"
"tests/test_dependency_duplicates.py"
"tests/test_dependency_overrides.py"
"tests/test_duplicate_models_openapi.py"
"tests/test_empty_router.py"
"tests/test_extra_routes.py"
"tests/test_filter_pydantic_sub_model.py"
"tests/test_forms_from_non_typing_sequences.py"
"tests/test_include_route.py"
"tests/test_infer_param_optionality.py"
"tests/test_inherited_custom_class.py"
"tests/test_invalid_path_param.py"
"tests/test_invalid_sequence_param.py"
"tests/test_jsonable_encoder.py"
"tests/test_multi_body_errors.py"
"tests/test_multi_query_errors.py"
"tests/test_no_swagger_ui_redirect.py"
"tests/test_param_class.py"
"tests/test_param_in_path_and_dependency.py"
"tests/test_put_no_body.py"
"tests/test_repeated_dependency_schema.py"
"tests/test_request_body_parameters_media_type.py"
"tests/test_response_change_status_code.py"
"tests/test_response_class_no_mediatype.py"
"tests/test_response_code_no_body.py"
"tests/test_response_model_invalid.py"
"tests/test_response_model_sub_types.py"
"tests/test_router_events.py"
"tests/test_router_prefix_with_template.py"
"tests/test_security_api_key_cookie.py"
"tests/test_security_api_key_cookie_optional.py"
"tests/test_security_api_key_header.py"
"tests/test_security_api_key_header_optional.py"
"tests/test_security_api_key_query.py"
"tests/test_security_api_key_query_optional.py"
"tests/test_security_http_base.py"
"tests/test_security_http_base_optional.py"
"tests/test_security_http_basic_optional.py"
"tests/test_security_http_basic_realm.py"
"tests/test_security_http_bearer.py"
"tests/test_security_http_bearer_optional.py"
"tests/test_security_http_digest.py"
"tests/test_security_http_digest_optional.py"
"tests/test_security_oauth2.py"
"tests/test_security_oauth2_authorization_code_bearer.py"
"tests/test_security_oauth2_optional.py"
"tests/test_security_oauth2_password_bearer_optional.py"
"tests/test_security_openid_connect.py"
"tests/test_security_openid_connect_optional.py"
"tests/test_serialize_response.py"
"tests/test_serialize_response_dataclass.py"
"tests/test_serialize_response_model.py"
"tests/test_skip_defaults.py"
"tests/test_starlette_exception.py"
"tests/test_starlette_urlconvertors.py"
"tests/test_sub_callbacks.py"
"tests/test_swagger_ui_init_oauth.py"
"tests/test_union_body.py"
"tests/test_union_inherited_body.py"
"tests/test_validate_response.py"
"tests/test_validate_response_dataclass.py"
"tests/test_validate_response_recursive.py"
"tests/test_ws_router.py"
)
EXCLUDE=(

)
TARGET_FAILING_TESTS=(
"tests/test_jsonable_encoder.py::test_encode_model_with_default"
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
