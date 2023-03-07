# FauxPy experiments on BugsInPy

This repository contains all the materials needed to experiment FauxPy on BugsInPy.
We may also add the experimental results to this repository later.

## Requirements
BugsInPy requires 3 Python Interpreters (3.6, 3.7, 3.8), since there are different projects in this framework each working with one of these 3 versions. It is better if all these 3 Python interpreters are virtual environments.

The reason is that BugsInPy does not work with Python commands such as `python3`, `python3.6` or things like that. It only works with the command `python` because the shell script of BugsInPy that compiles a project (which means creating a virtual environment for that project and installing all of its dependecies) [call the venv creation command](https://github.com/soarsmu/BugsInPy/blob/master/framework/bin/bugsinpy-compile#L56) using the command `python`.

So, in order to use BugsInPy correctly, one must either change one's OS's `python` command to point to the correct version for the project being compiled, or install 3 virtual envronments for these 3 python vrsions and activate the currect one for the project being compiled. We prefer the second solution which is explained below.

## Running the experiments

1. To replicate the experiments, all you need is the bash scripts we generated that are available in the directory [bash_script_generator/scripts](bash_script_generator/scripts), and the version of [FauxPy](pytest-FauxPy) existing in this repository. So, first clone this repositry, and then copy the `scripts` directory somewhere on your machine (e.g., `~/fauxpy_exp`). Afterwards, copy `FauxPy` to the `~/fauxpy_exp/scripts` directory on your machine.


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

3. Install Python dev package for Python 3.6, 3.7, and 3.8 (I am not sure if it is necessary, but installing them does not hurt):

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
Compileing some of the programs in BugsInPy affect your `.bashrc` file. So, our scripts require a backup version of `.bashrc` to fix these side effects.

```
cp ~/.bashrc ~/_bashrc
```

7. Run all of the scripts one by one to produce the results. For instance, the following command runs SBFL with statement granularity on bug 2 of cookiecutter:

```
./20020_1h_32g_cookiecutter_2_sbfl_statement.sh
```

When a script ends running, a directory by the name of the project for which the script is produced is made in the `~/fauxpy_exp/scripts` directory. This newly made directory contains the results. For instance, for the command above, this directory is `~/fauxpy_exp/scripts/cookiecutter`, which has the result of running SBFL with statement granularity on bug 2 of cookiecutter.

## Generating the bash scripts

We generated the [final bash scripts](bash_script_generator/scripts) in an iterative process that iterates through the following three phases:
1. [first round selection](first_round_selection)
2. [bash script generation](bash_script_generator)
3. [second round selection](second_round_selection)

We have already generated these scripts. So, you do not need to go throw this process. But, if you want to replicate it for any reason, you can follow the instructions below, which is a loop:

- S1. First go to [first round selection](first_round_selection), run all the six steps to generate the `subject_info.csv` file.
Then, pass `subject_info.csv` to the [bash script generation](bash_script_generator) phase.

- S2. Go to [bash script generation](bash_script_generator) and generate the scripts.

- S3. Run all the generated bash scripts and store the results.

- S4. Go to [second round selection](second_round_selection), and perform one iteration of the second round selection.
By doing so, some bugs are removed from the experiments, and thus, some new bugs have to be added to the experiments.
If the `manually_removed_bugs.json` file is not changed, stop this loop right here. Otherwise, go to S5.


- S5. Pass `manually_removed_bugs.json` from `second round selection` to [first round selection](first_round_selection), but, skip the first five steps of `first round selection` and run the rest to generate a new version of `subject_info.csv`.

- S6. Go to S2.


