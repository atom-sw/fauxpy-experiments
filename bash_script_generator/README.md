# Generating the bash scripts

## Purpose

The purpose of this process is to generate all the scripts required for the experiments. We generated these scripts, which can be found in the [scripts](scripts) directory. So, you do not need to go through this process. But, if you want to replicate it, you can follow the instructions below.

## How to generate the bash scripts

The Python script [subject_script_generator.py](subject_script_generator.py) generates 4 bash scripts for each subject selected for the experiments:

- 1 for SBFL with statement granularity
- 1 for MBFL with statement granularity
- 1 for PS with statement granularity
- 1 for ST with function granularity

The `subject_script_generator.py` script loads two csv files [info/subject_info.csv](info/subject_info.csv) and [info/timeout_info.csv](info/timeout_info.csv) to generate these bash scripts. The file `info/subject_info.csv` is generated during the [first round selection](/first_round_selection) process and copied to the [info](info) directory. The `info/timeout_info.csv` file contains a rough estimate of the time required by each project and fault localization technique. To generate the bash scripts, run the following command:

```
python subject_script_generator
```

When this script finshes, the [scripts](scripts) directory is created, which contains all of the bash scripts required for the experiments.

## Generating subject_info.csv

To know how `info/subject_info.csv` is generated or to produce it yourself, refer to [first_round_selection/README.md](/first_round_selection/README.md).
