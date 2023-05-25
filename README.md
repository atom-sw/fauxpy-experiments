# FauxPy experiments on BugsInPy

This repository is the first part of the replication package 
for the paper "An Empirical Study of Fault Localization in Python Programs" by Mohammad Rezaalipour and Carlo A. Furia.
This repository contains all the materials needed to replicate all the experiments
and produced all the results provided in the paper.

## 1. Structure

The structure of the repository is as follows.

1. [pytest-FauxPy](/pytest-FauxPy): the snapshot of our tool FauxPy
that we used in our experiments.
2. [first_round_selection](/first_round_selection): the scripts we used to mainly 
select correct subjects from BugsInPy (Section 4.1 in the paper) along with the scripts 
to generate the ground truth information (Section 4.2 in the paper).
3. [bash_script_generator](/bash_script_generator): the scripts to generate the
bash scripts for our experiments along with the bash scripts themselves.
4. [second_round_selection](/second_round_selection): the scripts to automatically
check the experimental results collect by running the bash
scripts generated at `bash_script_generator`.
5. [combinefl](/combinefl): the version of [combinefl](https://combinefl.github.io/)
that we modified and extended to be able to run it on BugsInPy subjects.
6. [metric_computation](/metric_computation): the scripts to generated the metric values
reported in different tables and figures within the paper.
7. [results](results): the scripts and the results of our statistical analyses within the paper.

Every one of the directories mentioned above has its own detailed readme file
or instructions explaining how each process can be replicated.

## 2. Requirements
BugsInPy requires 3 Python Interpreters (3.6, 3.7, 3.8), since there are different projects
in this framework each working with one of these 3 versions.
It is better if all these 3 Python interpreters are virtual environments.

The reason is that BugsInPy does not work with Python commands such as
`python3`, or `python3.6`. It only works with the command `python` because
the shell script of BugsInPy that
compiles a project (which means creating a virtual environment for that
project and installing all of its dependencies)
[calls the venv creation command](https://github.com/soarsmu/BugsInPy/blob/master/framework/bin/bugsinpy-compile#L56) 
using the command `python`.

So, in order to use BugsInPy correctly, one must either change
one's OS's `python` command to point to the correct version for the 
project being compiled, or install 3 virtual environments for these 3 python
versions and activate the current one for the project being compiled.
We prefer the second solution which is explained below.

## 3. Running the experiments

1. To replicate the experiments, all you need is the bash scripts we generated 
that are available in 
the directory [bash_script_generator/scripts](bash_script_generator/scripts), and
the version of [FauxPy](pytest-FauxPy) existing in this repository.
So, first clone this repository, and then copy the `scripts` directory
somewhere on your machine (e.g., `~/fauxpy_exp`). Afterwards, copy `FauxPy` to 
the `~/fauxpy_exp/scripts` directory on your machine.

```
git clone git@github.com:mohrez86/fauxpy_experiments.git
mkdir ~/fauxpy_exp
cp -rf fauxpy_experiments/bash_script_generator/scripts ~/fauxpy_exp
cp -rf fauxpy_experiments/pytest-FauxPy ~/fauxpy_exp/scripts
cd ~/fauxpy_exp
```

2. Install Python 3.6, 3.7, and 3.8 on the machine.

```
# Using APT
sudo apt install python3.6
sudo apt install python3.7
sudo apt install python3.8

# Using Conda
conda create --name fauxpy-3.6 python=3.6
conda create --name fauxpy-3.7 python=3.7
conda create --name fauxpy-3.8 python=3.8
```

3. Install Python dev package for Python 3.6, 3.7, and 3.8:

```
# Using APT
sudo apt-get install python3.6-dev
sudo apt-get install python3.7-dev
sudo apt-get install python3.8-dev

# Nothing needed in Conda
```

4. Create 3 venvs for these 3 Python versions in `~/fauxpy_exp`:

```
# Without Conda
python3.6 -m venv bugsinpyenv36
python3.7 -m venv bugsinpyenv37
python3.8 -m venv bugsinpyenv38

# With Conda
conda activate fauxpy-3.6
python3.6 -m venv bugsinpyenv36
conda deactivate
conda activate fauxpy-3.7
python3.7 -m venv bugsinpyenv37
conda deactivate
conda activate fauxpy-3.8
python3.8 -m venv bugsinpyenv38
conda deactivate
```

5. Go to the `~/fauxpy_exp/scripts` directory and make all the bash scripts executable.

```
cd scripts
chmod +x *.sh
```

6. Make a copy of your `.bashrc` file on your home directory, and name it `_bashrc`.
Compiling some of the programs in BugsInPy affect your `.bashrc` file. So, our scripts
require a backup version of `.bashrc` to fix these side effects.

```
cp ~/.bashrc ~/_bashrc
```

7. Run all of the scripts one by one to produce the data.
For instance, the following
command runs SBFL at the statement-level granularity on
8. cookiecutter bug #2:

```
./20020_1h_32g_cookiecutter_2_sbfl_statement.sh
```

When the script is finished, a directory is made inside 
the `~/fauxpy_exp/scripts` directory, which contains the
data generated by FauxPy.
For instance, for the command above, this directory is
`~/fauxpy_exp/scripts/cookiecutter`, and it contains the data
of running SBFL at 
the statement-level granularity on cookiecutter #2.

## 4. Generating the bash scripts

We generated the [final bash scripts](bash_script_generator/scripts) in
an iterative process, through the following three phases:
1. [first round selection](first_round_selection)
2. [bash script generation](bash_script_generator)
3. [second round selection](second_round_selection)

We have already generated these scripts. So, it is not needed 
to go through this process. But, to replicate the process one 
can follow the instructions below, which is a loop:

- S1. Go to [first round selection](first_round_selection), run
all the seven steps to generate the `subject_info.csv` file.
Then, copy `subject_info.csv` to 
the [bash script generation](bash_script_generator) phase.

- S2. Go to [bash script generation](bash_script_generator) and
generate the scripts.

- S3. Run all the generated bash scripts as 
explained in Section 3 in this file and store the results.

- S4. Go to [second round selection](second_round_selection), and
perform one iteration of the second round selection.
By doing so, some bugs are removed from the experiments, and
thus, some new bugs have to be added to the experiments.
If the `manually_removed_bugs.json` file in the `second round selection` 
is not changed, stop this loop. Otherwise, go to S5.

- S5. Copy `manually_removed_bugs.json` from
`second round selection` to 
[first round selection](first_round_selection). Skip the
first five steps of `first round selection` and run the
rest of the steps to generate a 
new version of `subject_info.csv`.

- S6. Go to S2.

## 5. Metric computation

To generate the results presented in the paper, you 
must first run all of the scripts as explained 
in Section 3 in this file.
Then, you can go through the
[metric_computation](/metric_computation) phase, which
relies on the data generated by running all the scripts.
The second part of our replication package already contains
all the data generated by running the scripts.
However, to use the data you generated yourself according
to Section 3, you must change the structure of the data
in a way `metric_computation` demands.

The `metric_computation` phase expects to get a director named `results`
which contains several directories, each of which is the data collected
by running one of our scripts. The name of each directory must be
the name of the script resulting it followed by an underscore (`_`)
and a random number after it. 
`results` must also contain two other 
directories named `Garbage` and `Timeouts` which can be empty.
For instance, the example mentioned in
Section 3 in this file, runs 
the script names `20020_1h_32g_cookiecutter_2_sbfl_statement.sh`.
Thus, the name of the directory containing the data for this
experiment must be `20020_1h_32g_cookiecutter_2_sbfl_statement_1231242`
(the number 1231242 can be any random 
number and does not have to be unique).
For this specific example, you can run the following commands to
generate the structure.

Run the following commands only once to generate the main structure:
```
cd ~/fauxpy_exp/scripts/
mkdir results
mkdir results/Garbage
mkdir results/Timeouts
```

Run the following script to put the data of the example
mentioned above to the `results` directory in a correct format.
You must do this step for every script you run.
```
cp -r cookiecutter/B2/ results/20020_1h_32g_cookiecutter_2_sbfl_statement_1231242
```



