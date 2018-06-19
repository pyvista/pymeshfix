#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# clean dist folder
rm $DIR/dist/*

# build dist
python3 setup.py sdist

# make manylinux wheels
dockerbuild.sh

# build windows wheels

