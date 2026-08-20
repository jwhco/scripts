# AGENTS.md

## Project Overview

- A library of scripts to support text conversion, editorial productivity, and quality assurance of Markdown.

## Conciseness

- You are an experienced software developer with expertise in python, text analytics, data mining, and tool development.

## Tools Used

- [Python3](https://www.python.org/). Scripting language with access to NLP and ML.
- [Visual Studio Code](https://code.visualstudio.com/Download). Primary editing environment.
- [Jupyter Notebook](https://jupyter.org/install). Combining documentation with Python development.
- [Canonical Kubernetes](https://ubuntu.com/kubernetes/). Containerized development environment.
- GNU Make

## Guidelines

- Don't store personally identifiable information or limited audience details in scripts. When working with people, places, and things, avoid adding these details to documentations.
- While each script is independent in nature, use similar GNU-style directory layouts, naming conventions, and build processes. Scripts should be similarly structured for maintainability.
- Eventually there will be a GUI interface, or CLI to kick off these scripts. When possible have a centralized configuration file.
- Remember, this repo is public. Do not store any keys, passwords, or sensitive details. Have those created in the users home directory or secret keys on K8S.
- For details about modules (the subdirectory folders) see [[README]] in the root directory.
- Try not to duplicate file names across modules. Use human-readable naming conventions for tools as the scripts act as functions in the larger tool set.
- Write clear well documented code that runs in distributed environments with minimal easy to follow user interfaces. Keep it simple.
- Use Unix style commands, meaning they can accept standard input, a specific file name, or a directory name. Otherwise, the command runs down a directory tree.
- For all scripts and documents use kebab-case for OS compatibility.

## Organization

- Maintain platform independence for scripts. At a minimum assume a `bash` and `python` environment.

- Under the root directory will be a project folder specific to the tool.
- Under that folder, each script set will have its own `README.md` for display under GitHub.
- In the best case, the script itself will include documentation. Be self-contained and function without dependencies.

/EOF/
