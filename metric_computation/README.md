# Metric computation

*The Python scripts in this directory are tested on Python 3.9.
Since we use Python's AST library here, which changes from
one Python version to another one, these scripts might not work
properly on other versions of Python.* 

## 1. Purpose

At this phase, we compute the metrics we picked for 
the paper. The current directory already contains the results of
this phase. But, if you want to replicate it, follow the
instructions in the next section.

This phase uses three inputs:

1. The results produced by running all the scripts we generated at
the [bash_script_generator](/bash_script_generator) phase,

2. the [ground_truth_info.json](/first_round_selection/ground_truth_info.json) and
[predicate_bug_info.json](/first_round_selection/predicate_bug_info.json) files
we generated at the
[first round selection](/first_round_selection) phase, and

3. the [size_counts.json](/first_round_selection/size_counts.json)
file we generated at the [first round selection](/first_round_selection) phase.



## 2. Running the script

To run this phase, first copy file `ground_truth_info.json`, file
`size_counts.json`, and file `predicate_bug_info.json`
from `first_round_selection` directory to this directory, and
then, set the *results path* and *workspace path*
in the [path_item.json](path_item.json) file. The results path should be similar to the one you set 
at the [second_round_selection](/second_round_selection) phase, and
the workspace path should be similar to the one you set at
the [first_round_selection](/first_round_selection). To generate
the results, follow the instructions below in order.

### 2.1 Bug and project types 

Run the following command to generate
[crashing_selected_bug_info.json](crashing_selected_bug_info.json) and
[predicate_selected_bug_info.json](predicate_selected_bug_info.json).
These two files contain information about the type of bugs used in our experiments.

```
python selected_bugs_types.py
```

### 2.2 FauxPy results

Run the following commands to generate the results for
FauxPy techniques at different granularity levels.

- For the statement-level run the following command:
```
python replicate.py 1
```

**Output**: directory [output_fauxpy_statement](output_fauxpy_statement)
contains the metrics, and directory [csv_fauxpy_statement](csv_fauxpy_statement)
contains the output list of different techniques on different bugs.

- For the function-level run the following command:
```
python replicate.py 2
```

**Output**: directory [output_fauxpy_function](output_fauxpy_function)
contains the metrics, and directory [csv_fauxpy_function](csv_fauxpy_function)
contains the output list of different techniques on different bugs.

- For the module-level run the following command:
```
python replicate.py 3
```

**Output**: directory [output_fauxpy_module](output_fauxpy_module)
contains the metrics, and directory [csv_fauxpy_module](csv_fauxpy_module)
contains the output list of different techniques on different bugs.

### 2.3 AvgFL results

Run the following commands to generate the results for
AvgFL techniques at different granularity levels.

- For the statement-level run the following command:
```
python replicate.py 4
```

**Output**: directory [output_avg_statement](output_avg_statement)
contains the metrics.

- For the function-level run the following command:
```
python replicate.py 5
```

**Output**: directory [output_avg_function](output_avg_function)
contains the metrics.

- For the module-level run the following command:
```
python replicate.py 6
```

**Output**: directory [output_avg_module](output_avg_module)
contains the metrics.
