#!/bin/bash
# builds python wheels on docker container and tests installation

set -e -x

# Collect python bin and filter out Python 3.4 and 2.7
pys=(/opt/python/*/bin)
pys=(${pys[@]//*27*/})
pys=(${pys[@]//*34*/})
# pys=(${pys[@]//*35*/})
pys=(${pys[@]//*38*/})  # waiting for vtk on python 3.8

# debug set pybin
# PYBIN="/opt/python/cp37-cp37m/bin"

# Compile wheels and test
for PYBIN in "${pys[@]}"; do
    "${PYBIN}/pip" install -r /io/requirements_build.txt
    "${PYBIN}/pip" wheel /io/ -w /io/wheelhouse/

    # install and test
    "${PYBIN}/python" -m pip install $package_name --no-index -f /io/wheelhouse

    "${PYBIN}/pip" install -r /io/requirements_test.txt
    "${PYBIN}/pip" install pytest-azurepipelines  # extra for azure
    "${PYBIN}/pytest" /io/tests -v

done
