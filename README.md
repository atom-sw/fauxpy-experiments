# FauxPy experiments on BugsInPy

This repository contains all the materials needed to experiment FauxPy on BugsInPy.
We may also add the experimental results to this repository later.

## Requirements
BugsInPy requires 3 Python Interpreters (3.6, 3.7, 3.8) being installed on the machine since there are different projects in this framework each working with one of these versions.

 All these 3 Python interpreters must be virtual environments since BugsInPy does not work with Python commands such as `Python3`, `Python3.6` or things like that. It only works with the command `Python`.

Thus, to make the machine ready for the experiments, one must follow these instructions:

1. Install Python 3.6, 3.7, and 3.8 on the machine.

```
sudo apt install python3.6
sudo apt install python3.7
sudo apt install python3.8
```

2. Install Python dev package for Python 3.6, 3.7, and 3.8 (I am not sure if it is necessary, but installing them does not hurt):

```
sudo apt-get install python3.6-dev
sudo apt-get install python3.7-dev
sudo apt-get install python3.8-dev
```

3. Create 3 venvs for these 3 Python versions:

```
python3.6 -m venv bugsinpyenv36
python3.7 -m venv bugsinpyenv37
python3.8 -m venv bugsinpyenv38
```

