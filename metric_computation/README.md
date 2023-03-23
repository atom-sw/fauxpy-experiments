# Metric computation

*The Python scripts in this directory are tested on Python 3.9.
Since we use Python's AST library here, which changes from
one Python version to another one, these scripts might not work
properly on other versions of Python.* 

At this phase, we generate the tabular data 
files that contain the metric results.
We have already done this phase and generated the results.
But, if you want to replicate the process, you can
follow the instructions below.

## Purpose

At this phase, we compute the metrics we picked for 
the paper using three inputs:
1. The results produced by running all the scripts we generated at
the [bash_script_generator](/bash_script_generator) phase,
2. the [ground_truth_info.json](/first_round_selection/ground_truth_info.json) and
[predicate_bug_info.json](/first_round_selection/predicate_bug_info.json) files
we generated at the
[first round selection](/first_round_selection) phase, and 
3. the [size_counts.json](/first_round_selection/size_counts.json)
file we generated at the [first round selection](/first_round_selection) phase.

## Running the script

To run this phase, first copy file `ground_truth_info.json`, file
`size_counts.json`, and file `predicate_bug_info.json`
from `first_round_selection` directory to this directory, and
then, set the *results path* and *workspace path*
in the [path_item.json](path_item.json) file. The results path should be similar to the one you set 
at the [second_round_selection](/second_round_selection) phase, and
the workspace path should be similar to the one you set at
the [first_round_selection](/first_round_selection).

First run the following command to generate [crashing_selected_bug_info.json](crashing_selected_bug_info.json)
and [predicate_selected_bug_info.json](predicate_selected_bug_info.json).
These two files contain information about the type of bugs used in our experiments.

```
python selected_bugs_types.py
```

Then, you can run the following command to compute all the metrics.

```
python compute_all.py
```

