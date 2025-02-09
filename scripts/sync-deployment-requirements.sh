#!/usr/bin/env bash

set -ex

# Change the current working directory to the directory of the script.
cd "$(dirname "$0")"

# Ensure that the bootstrap requirements are up-to-date within our python environment.
pip install -r ../requirements/bootstrap.txt

# Sync the development requirements.
pip-sync \
    ../requirements/bootstrap.txt \
    ../requirements/deployment.txt \
    ../requirements/development.txt \
    ../requirements/production.txt \
    ;

# This is fairly fast and adds to verbosity but also allows us to use PIP_FORCE_REINSTALL=1 as an env var before calling
# this script.
pip install \
    -r ../requirements/bootstrap.txt \
    -r ../requirements/deployment.txt \
    -r ../requirements/development.txt \
    -r ../requirements/production.txt \
    ;

# Install the source we are working on as an editable package.
pip install --no-build-isolation --no-deps \
    -e ..[development,deployment] \
    ;
