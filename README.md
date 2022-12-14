# FauxPy_Experiments

## Requirements
BugsInPy requires 3 Python Interpreters (3.6, 3.7, 3.8) being installed on the machine since there are different projects in this framework each working with one of these 3 versions. It is better if all these 3 Python interpreters are virtual environments.

BugsInPy does not work with Python commands such as `python3`, `python3.6` or things like that. It only works with the command `python`. The reason is that the shell scripts of the BugsInPy that compiles a project, which means creating a virtual environment for that project and installing all of its dependecies, call the venv creation command using the command `python`.

 So, in order to use BugsInPy correctly, one must either change one's OS's `python` command to point to the correct version for the project being compiled, or install 3 virtual envronments for these 3 python vrsions. We prefer the second solution which is as follows:


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

