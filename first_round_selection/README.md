# First round selection

*The Python scripts in this directory are tested on Python 3.9.
Due to extensive usage of Python's AST library, which changes from
one Python version to another one, these scripts might not work
properly on other versions of Python.* 

## Purpose

The purpose of this phase is to produce three files. The first file is 
the [subject_info.csv](subject_info.csv) file that
contains all the information about the benchmarks that are used in the experiments. 
The `subject_info.csv` file can then be used to automatically generate the 
bash scripts in
the [bash_script_generator/scripts](/bash_script_generator/scripts) directory.
The second file is the [ground_truth_info.json](ground_truth_info.json) file
that contains information
about the changes in the commits representing the bugs in BugsInPy.
The third file is the [size_counts.json](size_counts.json) file,
which contains the number of lines, functions, and modules in each
buggy version.
The files `ground_truth_info.json` and `size_counts.json` are used 
in the [metric_computation](/metric_computation) phase.
We have already generated these three files, and they exist in this directory.
So, you do not need to go through this process. 
But, if you want to replicate the process, you can follow the
instructions below.
Keep in mind that going through the whole process can take up to
seven 10 days and nights.

## Introduction

At the beginning, we tired to do this selection process manually.
But, after a while, we realized it is so time-consuming that doing it manually is 
almost impossible. So, we automated this first round selection 
process, which is explained in this document.
This whole process have several steps, each of which requires running a specific
Python or Bash script, resulting in the generation of some files that are used
by the next step.

## Step 1: Opening benchmarks

At this step, we clone and compile all the buggy and fixed versions in BugsInPy. 
To do that, we run the following command by passing one of the Json files in
the [info](info) and [info_2](info_2) directories.
For instance, `[BugsInPyProjectName]` can be
`keras`. This script checks out all the buggy and 
fixed versions of a given BugsInPy project (e.g., keras), and 
runs the target failing tests on both the buggy and the fixed
versions, and saves the results.

This script must be executed for every single one of the Json files
in the `info` and `info_2` directories, which takes around a 
week (7 * 24 hours) to finish, depending on
your machine.

Before running any of the following steps, open 
the [workspace.json](workspace.json) file and set
the workspace for the script (set the variable `WORKSPACE_PATH`).
Make sure there is enough space on the path you provide as
the workspace. It requires ~500 GB for all the projects.
Also, add a file named `github_token.txt` to the current directory and 
put a GitHub token in it as it is needed to fetch data from GitHub.

```
./benchmark_opener.sh [info|info_2]/[BugsInPyProjectName].json
``` 

## Step 2: Checking the compiled versions

At this step, we check if all the buggy and fixed versions are compiled correctly.
If any of them is not compiled, we must repeat the previous step for it, or remove it
from the experiments. To perform this check, we run the following commands
that take no
arguments. These scripts print on the screen which compilations where not 
successful, and
it should finish quickly (probably in less than 1 minute).

```
pip install PyGithub

./check_compile_all.sh
./check_compile_all_2.sh
```

After running these commands, we realized tornado 16 cannot be compiled duo to 
a [bug](https://github.com/soarsmu/BugsInPy/tree/master/projects/tornado/bugs/16) 
in the BugsInPy framework (missing `requirements.txt` file for bug 16). Thus, we
removed tornado 16 from our experiments by setting `BUG_NUMBER_END` in
[info/tornado.json](info/tornado.json) to 15 instead of 16. The standard output
of this step
can be found in the [compile_log](compile_log) and [compile_log_2](compile_log_2)
directory.

## Step 3: Checking target failing tests

The BugsInPy framework contains 17 projects, and the total of 501 bugs.
For each bug, it has
a buggy and a fixed version, a test suite, and one or more tests to
reveal each bug, we refer to
which as the *target failing tests*.
The idea is that the target failing tests of a bug must
fail on the buggy version of that bug while pass on the
fixed version of that bug.

However, due to some reasons (such as dependency problems) it does
not always hold. For instance, in
some cases, the target failing tests pass or fail on both versions, or 
produce an error on fixed 
versions. Such bugs must be removed from our experiments, which is
done at this step. To perform
this check, run the following commands:


```
./check_target_tests_all.sh
./check_target_tests_all_2.sh
```

When these scripts are finished running, they produce
the [correct](correct) and [correct_2](correct_2) directories,
containing a Json
file for each project showing which bugs have been removed and
kept according to 
the criteria mentioned above. The standard output of this step
can be found in 
the [target_tests_log](target_tests_log) 
and [target_tests_log_2](target_tests_log_2) directories.

Before running `./check_target_tests_all_2.sh`, 
fix the `bugsinpy_run_test.sh` file in buggy and fixed versions
of matplotlib 8
by putting the two tests in two different lines and removing
the semicolon between them or `./check_target_tests_all_2.sh` crashes
for matplotlib due to an assertion failure.


## Step 4: Ground truth generation

At this step, we generate 
the file [ground_truth_info.json](ground_truth_info.json) that contains
information about changes made to fix each bug in BugsInPy.
This file is then used 
at the [metric_computation](/metric_computation) phase to calculate
the metrics we use in the paper.
To generate `ground_truth_info.json`, run the following command:

```
python generate_ground_truth_info.py
```

This script also generates 
two files [empty_ground_truth_info.json](empty_ground_truth_info.json) 
and [empty_ground_truth_info_2.json](empty_ground_truth_info_2.json) that
contains those bugs in BugsInPy for which the computed ground
truth is empty. These files are used at 
step 6 to exclude such cases 
from the experiments (we
ignore `empty_ground_truth_info_2.json` because it is empty).

Another file generated at this phase
is [predicate_bug_info.json](predicate_bug_info.json)
that show which bugs are predicate bugs.
We use this file also at the metric computation phase.


## Step 5: Counting loc, number of functions, and number of modules

At this step, we count the number of lines in every buggy version,
excluding empty lines
and comment lines. We only consider lines from modules that
are used in
fault localization, which are those in target directories
(not in test modules or Python virtual environments).
We also count the number of functions, and
the number of modules in each buggy version.

We need this information to compute the *Exam Score* at 
the [metric_computation](/metric_computation) phase.
Run the following command (which is slow) to generate 
the [size_counts.json](size_counts.json) file:

```
python size_counter.py
```


## Step 6: Time-based selection

Based on some rough estimate of the amount of time each experiment
requires and the processing
resources we have (a cluster server with 15 available nodes for
two weeks), we randomly
select a subset of the bugs picked at the previous step. To perform this
simulation, run the following command:

```
python estimate_time.py
```

When this script is finished running, it generates 
the [time_selected_bugs.json](time_selected_bugs.json) file that 
contains the randomly selected bugs from each of the BugsInPy projects.

## Step 7: Generating subject_info.csv

This is the final step in which the [subject_info.csv](subject_info.csv) file
for the bugs
in `time_selected_bugs.json` is generated. To perform this step, we must run
the following command.

```
pip install python-scalpel
pip install packaging

python generate_subject_info.py
```

This step also performs a call graph based test case selection using
[Scalpel](https://github.com/SMAT-Lab/Scalpel), a python static
analysis framework. So, it is very slow.
