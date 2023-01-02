This project performs the first round check for the experiments.
In this round we only keep those buggy benchmarks 
that pass the following criteria:
1. The target failing tests fail on the buggy version
2. The target failing tests pass on the fixed version
3. Running the target failing tests do not result in only errors 
in either the buggy or the fixed version.
Having errors in the buggy version while having also failed tests 
is OK. But, running the target failing tests on the fixed version
must not result in any errors.

To perform this check, one must first run the following 
command
```
benchmark_opener.sh [BugsInPyProjectName].json
``` 
where `[BugsInPyProjectName]` can be the name of one of BugsInPy 
projects such as keras. This script checks out all the buggy and 
fixed versions of a given BugsInPy project (e.g., keras), and 
runs the target failing tests on both the buggy and the fixed
version, and saves the results (a time-consuming process). Before
running this command, open the `global_constants.json` file and set the
workspace for the script (set the variable `WORKSPACE_PATH`).
Make sure there is enough space on the path you provide as
the workspace. It can go up to tens of gigabytes.

When the script mentioned above finished working, run the following
command to perform the benchmark selection process.
```
python check.py [BugsInPyProjectName].json
```
Running this must not take so much time. When it is finished, it
generates a csv file for the given BugsInPy project and a file
containing those bug numbers that do not pass the first round
criteria.

The csv file can then be used to generate the experiments bash
scripts. However, the following items must be manually checked
before adding the info in the csv file to the benchmark information
table since in some cases they might not be correct as they are simply
hard coded in the `[BugsInPyProjectName].json` file, which should be
correct in most cases. The items to check manually are:
1. TARGET_DIR
2. TEST_SUITE
3. EXCLUDE

