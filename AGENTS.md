# AGENTS.md

## Project Overview

- A library of scripts to support text conversion, editirial productivity, and quality assurance of markdown.

## Tools Used

- [Python3](https://www.python.org/). Scripting language with access to NLP and ML.
- [Visual Studio Code](https://code.visualstudio.com/Download). Primary editing environment.
- [Jupyter Notebook](https://jupyter.org/install). Combining documentation with Python development.
- [Canonical Kubernetes](https://ubuntu.com/kubernetes/). Containerized development environment.
- GNU Make

## Guidelines

- While each script is indepedent in nature, use similar GNU style directory lay outs, naming convensions, and builds. Scripts need to be similarly to maintain.
- Eventually there will be a GUI interface, or CLI to kick off these scripts. When possible have a centralized configuration file.
- Remember, this repo is public. Do not store any keys, passwords, or sensative details. Have those created in the users home directory or secret keys on K8S.
- For details about modules (the sub-directory folders) see [[README]] in the root directory. 
- Try not to duplicate file names across modules. Use human readable naming conventions for tools as the scripts act as functions in the larger toolset.

## Organization


- Maintain platform indepencence for scripts. At a minimum assume a `bash` and `python` environment.

- Under the root directory will be a project folder specific to the tool. 
- Under that folder, each script set will have its own `README.md` for display under GitHub. 
- In the best case, the script itself will include documentation. Be self contained and function without dependencies.

/EOF/