# CombineFL on BugsInPy

## Requirements

We built our package in this directory 
on top of the replication package of
[CombineFL](https://damingz.github.io/combinefl/index.html).
Since `CombineFL` is written in Python 2.7, we also
used Python 2.7 for the package in this directory
to be able to adopt it to our experiments with only a few changes.
Thus, this package is only tested on Python 2.7 and may not work
on Python 3.

The package `CombineFL` uses
[Support Vector Machine for Ranking](https://www.cs.cornell.edu/people/tj/svm_light/svm_rank.html),
which is already included in the current package in [SVMRank](SVMRank) directory.
So, there is no need to download it or install it.

## Supporting BugsInPy

The `CombineFL` replication packages contains a file
`release.json` that has information about the different techniques' scores
on different statements in Defects4J bugs. The size of this file
is around 270 MB. So, we split it into 10 files starting 
with [java_release_0.json](data/java_release_0.json) to be able
to add them to this GitHub repository. In order to run `CombineFL` on BugsInPy,
we added 3 * 10 files named `python_x_release_y.json` similar to those of Defects4j,
but for BugsInPy bugs and for different granularity levels.

We also renamed the file `qid-lines.csv` (line numbers in Defects4j bugs)
in CombineFL's replication package to
[java_qid-lines.csv](data/java_qid-lines.csv) 
(where `x` is the granularity level and `y` 
is a number between 0 and 9) and added three files
`python_x_qid-lines.csv` (where `x` is the granularity level), 
for BugsInPy bugs for three different granularity levels.

All of the files we added 
are generated at the [metric_computation](/metric_computation)
phase, and were copied to directory [data](data).

Then, we extended CombineFL's replication package to support eight different
experiments:
1. py_alfa_stmt
2. py_alfa_func
3. py_alfa_mod
4. py_sbst_stmt
5. py_sbst_func
6. py_sbst_mod
7. j_alfa_stmt
8. j_sbst_stmt


## Running CombineFL on BugsInPy

To run `CombineFL` on BugsInPy or Defects4j, run the following commands in order.
The `<experiment type>` parameter can be one of the eight
experiments mentioned above.

```
python 1-combine.py -e <experiment type>

./2-split.sh

./3-crossvalidation.sh

python 4-calc-metric.py
```

## Results

The results of running the eight experiments mentioned above are as follows.
Copy these eight files 
to directory `inputs_from_combine_fl`
in [metric_computation](/metric_computation).

1.File [results_python_statement_alfa.json](results_python_statement_alfa.json)
contains the results of running CombineFL on Python, at the statement
level granularity, while combining all families.

2.File [results_python_function_alfa.json](results_python_function_alfa.json)
contains the results of running CombineFL on Python, at the function
level granularity, while combining all families.

3.File [results_python_module_alfa.json](results_python_module_alfa.json)
contains the results of running CombineFL on Python, at the module
level granularity, while combining all families.

4.File [results_python_statement_sbst.json](results_python_statement_sbst.json)
contains the results of running CombineFL on Python, at the statement
level granularity, while combining SBFL and ST.

5.File [results_python_function_sbst.json](results_python_function_sbst.json)
contains the results of running CombineFL on Python, at the function
level granularity, while combining SBFL and ST.

6.File [results_python_module_sbst.json](results_python_module_sbst.json)
contains the results of running CombineFL on Python, at the module
level granularity, while combining SBFL and ST.

7.File [results_java_statement_alfa.json](results_java_statement_alfa.json)
contains the results of running CombineFL on Java, at the statement
level granularity, while combining all families.

8.File [results_java_statement_sbst.json](results_java_statement_sbst.json)
contains the results of running CombineFL on Java, at the statement
level granularity, while combining SBFL and ST.
