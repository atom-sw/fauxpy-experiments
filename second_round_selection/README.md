# Second round selection

## Purpose

The purpose of this phase is to go through the experimental 
results and find those that did not finish successfully, which
can happen for the following reasons:

1. Due to missing requirements, some buggy versions cannot run all their
test cases, although they have enough of their requirements to run
their target failing tests.
2. Due to timeout, some buggy versions do not finish. The cluster server
we are using for the experiments has a timeout limit of 48 hours, and buggy
version that require more than 48 hours, cannot be used in out experiments.
3. In some cases, running the target failing test does not result in any
execution traces (e.g., fastapi 8).
4. Due to FauxPy's limitations, FauxPy does not
report any suspicious statements for some buggy versions. For instance,
if some parts of a buggy version that are executed by the selected test suite call
the function `sys.settrace()`, FauxPy may not be able to work properly as
FauxPy uses the `Coverage.py` tool through its APIs, and this tool may not
work properly on source code that calls the function `sys.settrace()`.
4. Due to package conflicts, or any other reasons, FauxPy may not
be able to run on some buggy versions.

We also go through the fishy results. A run is fishy if it does not have any
record in its csv files, or all of the records in a csv file are of 
the same score. If a fishy run is correct, we add it 
to the [correct_fishy.csv](correct_fishy.csv) file so that we do not
analyze them in other iterations of the second round selection.

After finding those that have problems, we check them manually to see if the 
problems can be fixed. If they cannot be fixed, we add them
to the [manually_removed_bugs.csv](manually_removed_bugs.csv) file, which
produces the [manually_removed_bugs.json](manually_removed_bugs.json) file.
Then, we copy `manually_removed_bugs.json` to the 
the first round selection directory and run the simulation again
to find replacements for the ones that are removed at this phase.


