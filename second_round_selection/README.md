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
3. Due to FauxPy's limitations, FauxPy does not
report any suspicious statements for some buggy versions. For instance,
if some parts of a buggy version that are executed by the selected test suite call
the function `sys.settrace()`, FauxPy may not be able to work properly as
FauxPy uses the `Coverage.py` tool through its APIs, and this tool may not
work properly on source code that calls the function `sys.settrace()`.
4. Due to package conflicts, or for any other reason, FauxPy may not
be able to run on some buggy versions.

After finding those that have problems, we check them manually to see if the 
problems can be fixed. If they cannot be fixed, we go back to 
the first round selection and add that buggy version to the 
manually removed bugs and run the simulation again
to find replacements for the ones that are removed at this phase.
