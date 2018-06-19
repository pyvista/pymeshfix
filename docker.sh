#!/bin/bash

cd /root/source
for PYBIN in /opt/python/*/bin; do
    # skip Python 3.4 and 3.7
    if [[ $PYBIN =~ .*37.* ]]
    then
    	continue
    elif [[ $PYBIN =~ .*34.* ]]
    then
	continue
    fi

    echo 'Running for' $PYBIN
    "${PYBIN}/pip" install numpy  # required for setup.py

    # build wheel
    "${PYBIN}/python" setup.py -q bdist_wheel

    # test
    "${PYBIN}/pip" install vtkInterface  # required for testing
    "${PYBIN}/python" setup.py install
    "${PYBIN}/python" pymeshfix/examples/fix.py
done
