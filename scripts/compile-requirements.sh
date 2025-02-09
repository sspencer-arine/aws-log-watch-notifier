#!/usr/bin/env bash

set -ex

# Change the current working directory to the directory of the script.
cd "$(dirname "$0")"

# Ensure we are operating in our virtual environment.
source ../.venv/bin/activate

# Ensure that the bootstrap requirements are up-to-date within our python environment.
# This should just include pip, pip-sync, setuptools, wheel initially if it doesn't already exist.
pip install \
    -c ../requirements/constraints.in \
    -r ../requirements/bootstrap.in

# Define the base options for pip-compile.
declare -a pip_compile_options

pip_compile_options+=("--verbose")
pip_compile_options+=("--allow-unsafe")
pip_compile_options+=("--generate-hashes")
pip_compile_options+=("--no-emit-index-url")
pip_compile_options+=("--no-emit-options")
pip_compile_options+=("--no-emit-trusted-host")
pip_compile_options+=("--no-reuse-hashes")
pip_compile_options+=("--resolver=backtracking")
pip_compile_options+=("--strip-extras")

# Clean this out so that we are always drawing from `constraints.txt`.
rm -f ../requirements/bootstrap.txt
rm -f ../requirements/development.txt
rm -f ../requirements/production.txt
rm -f ../requirements/deployment.txt

# Compile the constraints from all of the input files and leverage --upgrade during this run.
pip-compile \
    ${pip_compile_options[*]} \
    --output-file=../requirements/constraints.txt \
    --upgrade \
    ../requirements/*.in \
    ;

# Recompile to regenerate all the hashes.
pip-compile \
    ${pip_compile_options[*]} \
    --output-file=../requirements/constraints.txt \
    ../requirements/*.in \
    ;

# Compile the bootstrap requirements.
pip-compile \
    ${pip_compile_options[*]} \
    --output-file=../requirements/bootstrap.txt \
    ../requirements/constraints.in.inc \
    ../requirements/bootstrap.in \
    ;

# Reinstall the newly formed bootstrap.txt
pip install -r ../requirements/bootstrap.txt

# Compile the deployment requirements.
pip-compile \
    ${pip_compile_options[*]} \
    --output-file=../requirements/deployment.txt \
    ../requirements/constraints.in.inc \
    ../requirements/deployment.in \
    ;

# Compile the development requirements.
pip-compile \
    ${pip_compile_options[*]} \
    --output-file=../requirements/development.txt \
    ../requirements/constraints.in.inc \
    ../requirements/development.in \
    ;

# Compile the production requirements.
pip-compile \
    ${pip_compile_options[*]} \
    --output-file=../requirements/production.txt \
    ../requirements/constraints.in.inc \
    ../requirements/production.in \
    ;
