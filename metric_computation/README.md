# Metric computation

## Purpose

At this phase, we compute the metrics we picked for 
the paper using three inputs:
1. The results produced by running all the scripts we generated at
the [bash_script_generator](/bash_script_generator) phase, and
2. the [ground_truth_info.json](/first_round_selection/ground_truth_info.json)
file we generated at the [first round selection](/first_round_selection) phase.
3. the [line_counts.json](/first_round_selection/line_counts.json)
file we generated at the [first round selection](/first_round_selection) phase.

To run this phase, first copy `ground_truth_info.json` and `line_counts.json` from `first_round_selection` directory to this directory, and
then, set the results path in the [workspace.json](workspace.json) file. The
results path should be similar to the one you set at the [second_round_selection](/second_round_selection) phase.
Then, you can run the following command to compute all the metrics.

```
python compute_all.py
```

