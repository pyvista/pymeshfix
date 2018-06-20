#!/bin/bash

# builds python wheels on docker container and tests installation

cd /root/source
mkdir wheels
for PYBIN in /opt/python/*/bin; do
    # skip Python 3.4 and 3.7
    if [[ $PYBIN =~ .*37.* ]]
    then
    	continue
    elif [[ $PYBIN =~ .*34.* ]]
    then
	continue
    elif [[ $PYBIN =~ .*27mu.* ]]
    then  # must be ucs4
	$PYBIN='/opt/_internal/cpython-2.7.15-ucs4/bin/python'
    fi

    echo 'Running for' $PYBIN
    "${PYBIN}/pip" install numpy -q  # required for setup.py
    "${PYBIN}/pip" install cython --upgrade -q

    # build wheel
    "${PYBIN}/python" setup.py -q bdist_wheel

    # test wheel
    wheelfile=$(ls /root/source/dist/*.whl)
    "${PYBIN}/pip" install $wheelfile -q

    # pytest doesn't seem to work here
    # "${PYBIN}/pip" install pytest -q
    # cd /
    # "${PYBIN}/python" -m pytest
    # cd /root/source

    "${PYBIN}/python" pymeshfix/examples/fix.py

    # get the wheel out of the way for next version
    mv $wheelfile wheels/
done

# repair wheels
for file in wheels/*linux*
do
    auditwheel repair $file
done
