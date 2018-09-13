# Spongebob

Installation guide for Windows

## Install Miniconda

To run Spongebob, you need Python 2.7. You can create a conda Python-2.7 environment
from a Python-3 conda installation.

Go to https://conda.io/miniconda.html

and download the installer for Miniconda for Python.

Or follow this link: https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe

Install Miniconda with all the recommended defaults. That is:
- Install for just me (recommended)
- Install in C:/Users/username/Miniconda
- Don´t add Miniconda to your system path (i.e. don´t tick the mark that says to do that).

Now you have an application called anaconda prompt. You can run it from the start menu.

## Download Spongebob

Clone this repository

```posh
git clone https://github.com/manjebrinkhuis/spongebob.git
```

Or download from [here](https://github.com/manjebrinkhuis/spongebob/archive/master.zip).

## Create environment

In the anaconda prompt, type:

```posh
# Create environment
conda create -y -n py27 python=2
# Activate environment
activate py27
```

Then install dependencies into environment. In the prompt, type:

```posh
(py27) C:\> pip install -r /path/to/spongebob/requirements.txt
```

## Run SPM

From anaconda prompt go to the `orig` directory in  the `spongebob` directory. Type:

```posh
(py27) C:\> cd path\to\spongebob\orig
(py27) C:\> python SpongePatternMaker.py
```

## Run motortest

To run motor 6 and 11 in alternation, for a 100 times, from the spongebob directory, run:

```posh
(py27) C:\> cd path\to\spongebob
(py27) C:\> python motortest.py
```

## Run experiments

To run the experiments psychopy is required. See http://www.psychopy.org for more information.
