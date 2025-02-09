#!/usr/bin/env bash

set -ex

cd "$(dirname "$0")"

toml-sort \
    --in-place \
    --sort-inline-arrays \
    --sort-inline-tables \
    --sort-table-keys \
    --spaces-indent-inline-array 4 \
    --trailing-comma-inline-array \
    ../pyproject.toml
