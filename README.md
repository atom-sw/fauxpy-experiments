# FauxPy experiments on BugsInPy

This repository contains all the materials needed to experiment FauxPy on BugsInPy.
We may also add the experimental results to this repository later.

## Requirements
BugsInPy requires 3 Python Interpreters (3.6, 3.7, 3.8), since there are different projects in this framework each working with one of these 3 versions. It is better if all these 3 Python interpreters are virtual environments.

The reason is that BugsInPy does not work with Python commands such as `python3`, `python3.6` or things like that. It only works with the command `python` because the shell script of BugsInPy that compiles a project (which means creating a virtual environment for that project and installing all of its dependecies) [call the venv creation command](https://github.com/soarsmu/BugsInPy/blob/master/framework/bin/bugsinpy-compile#L56) using the command `python`.

 So, in order to use BugsInPy correctly, one must either change one's OS's `python` command to point to the correct version for the project being compiled, or install 3 virtual envronments for these 3 python vrsions and activate the currect one for the project being compiled. We prefer the second solution which is as follows:


1. Install Python 3.6, 3.7, and 3.8 on the machine.

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

2. Install Python dev package for Python 3.6, 3.7, and 3.8 (I am not sure if it is necessary, but installing them does not hurt):

```
# Using APT
sudo apt-get install python3.6-dev
sudo apt-get install python3.7-dev
sudo apt-get install python3.8-dev

# Nothing needed in Conda
```

3. Create 3 venvs for these 3 Python versions in the directory that contains the parent directory of the scripts (e.g., `cookiecutter_1.sh`). For instance, if the current directory is `scripts` (which contains `cookiecutter_1.sh`), run the following commands:

```
cd ..

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

4. You must also keep a copy of FauxPy in the same directory where the scripts (e.g., `cookiecutter_1.sh`) are located since FauxPy is not publicly available as a pip package at the moment.


## Generating the bash scripts

In order to generate the bash scripts that run FauxPy on each benchmark, one can use the Python script `subject_script_generator.py`. This Python script requires the bash script template `faux-in-py-template.sh` and the csv file `subject_info.csv` to be in the same directory as this Python script. Running `subject_script_generator.py` makes a directory named `scripts` that contains all of the scripts for the experiments.

```
python subject_script_generator.py
```
