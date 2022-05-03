#!/usr/bin/env bash

PYTHON_VERSION="$1"

case $PYTHON_VERSION in
3.7)
  FULL_VERSION=3.7.7
  ;;
3.8)
  FULL_VERSION=3.8.3
  ;;
3.9)
  FULL_VERSION=3.9.12
  ;;
3.10)
  FULL_VERSION=3.10.4
  ;;
esac

INSTALLER_NAME=python-$FULL_VERSION-macosx10.9.pkg
URL=https://www.python.org/ftp/python/$FULL_VERSION/$INSTALLER_NAME

PY_PREFIX=/Library/Frameworks/Python.framework/Versions

set -e -x

curl $URL > $INSTALLER_NAME

sudo installer -pkg $INSTALLER_NAME -target /

sudo rm /usr/local/bin/python
sudo ln -s /usr/local/bin/python$PYTHON_VERSION /usr/local/bin/python

which python
python --version
python -m ensurepip
python -m pip install --upgrade pip
python -m pip install setuptools twine wheel
