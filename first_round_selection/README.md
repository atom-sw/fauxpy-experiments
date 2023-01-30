# First round selection

## Introduction

The purpose of this step is to produce the [subject_info.csv](subject_info.csv) file that
contains all the information about the benchmarks, being used in the experiments. 
The `subject_info.csv` file can then be used to automatically generate the bash scripts in
the [/bash_script_generator/scripts](/bash_script_generator/scripts) directory. To see
how this csv file is used, refer to the [readme](/bash_script_generator/README.md) of the `bash_script_generator` directory.

At the beginning, we tired to do this selection process manually. But, after 
a while, we realized it is so time consuming that doing it manually is 
almost impossible. So, we automated this first round selection 
process, which is explained in this document.

During the manual process, we removed 5 out of the 17 projects since they 
did not pass our criteria for selection. Thus, the process explained below only
performs the first round selection on the 12 remaining projects in BugsInPy.
This whole process have several steps, each of which requires running a specific
Python or Bash script, resulting in the generation of some files that are used
by the next step.

## Step 1: Opening benchmarks

At this step, we clone and compile all the buggy and fixed versions in BugsInPy. 
To do that, we run the following command by passing one of the Json files in
the [info](info) directory. For instance, `[BugsInPyProjectName]` can be
`keras`. This script checks out all the buggy and 
fixed versions of a given BugsInPy project (e.g., keras), and 
runs the target failing tests on both the buggy and the fixed
versions, and saves the results.

This script must be executed for every single one of the 12 Json files
in the `info` directory, which takes around a week to finish, depending on
your machine. Before running this command, open the [workspace.json](workspace.json) file and set
the workspace for the script (set the variable `WORKSPACE_PATH`).
Make sure there is enough space on the path you provide as
the workspace. It requires 542 GB for the 12 selected projects.

```
benchmark_opener.sh info/[BugsInPyProjectName].json
``` 

## Step 2: Checking the compiled versions

At this step, we check if all the buggy and fixed versions are compiled correctly.
If any of them is not compiled, we must repeat the previous step for it, or remove it from
the experiments. To perform this check, we run the following command that takes no
arguments. This script prints on the screen which compilations where not successful, and
it should finish quickly (probably in less than 1 minute).

```
./check_compile_all.sh
```

After running this command, we realized tornado 16 cannot be compiled duo to 
a [bug](https://github.com/soarsmu/BugsInPy/tree/master/projects/tornado/bugs/16) 
in the BugsInPy framework (missing `requirements.txt` file for bug 16). Thus, we
removed tornado 16 from our experiments by setting `BUG_NUMBER_END` in
[info/tornado.json](info/tornado.json) to 15 instead of 16. The standard output of this step
can be found in the [compile_log](compile_log) directory.

## Step 3: Checking target failing tests

The BugsInPy framework contains 17 projects, and the total of 501 bugs. For each bug, it has
a buggy and a fixed version, a test suite, and one or more tests to reveal each bug, we refer to
which as the *target failing tests*. The idea is that the target failing tests of a bug must
fail on the buggy version of that bug while pass on the fixed version of that bug.

However, due to some reasons (such as dependency problems) it does not always hold. For instance, in
some cases, the target failing tests pass or fail on both versions, or produce an error on fixed 
versions. Such bugs must be removed from our experiments, which is done at this step. To perform
this check, run the following command:

```
./check_target_tests_all.sh
```

When this script is finished running, it produces the [selected](selected) directory, containing a Json
file for each project showing which bugs have been removed and kept according to 
the criteria mentioned above.

## Step 4: Time-based selection

Based on some rough estimate of the amount of time each experiment requires and the processing
resources we have (a cluster server with 15 available nodes for two weeks), we randomly
select a subset of the bugs picked at the previous step. To perform this simulation,
run the following command:

```
python estimate_time.py
```

When this script is finished running, it generates 
the [time_selected_bugs.json](time_selected_bugs.json) file that 
contains the randomly selected bugs from each of the 12 projects.

## Step 5: Generating subject_info.csv

This is the final step in which the [subject_info.csv](subject_info.csv) file for the bugs
in `time_selected_bugs.json` is generated. To perform this step, we must run
the following command. However, before running it, add a file named `github_token.txt`
to the current directory and put a GitHub token in it as it needs to fetch data from GitHub.

```
pip install PyGithub
pip install python-scalpel
pip install packaging

generate_subject_info.py
```

This step also performs a call graph based test case selection using
[Scalpel](https://github.com/SMAT-Lab/Scalpel), a python static
analysis framework.
