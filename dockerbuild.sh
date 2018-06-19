#!/bin/bash


# script to build manylinux binary wheel using docker
# inspired by/copied from:
# https://github.com/pypa/python-manylinux-demo/blob/master/travis/build-wheels.sh


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# start docker image and store the id
docker run -d -i quay.io/pypa/manylinux1_x86_64 /bin/bash
CONTAINERID=$(docker ps -q)

# required for vtk(?)
# docker exec -it $CONTAINERID yum install libXtst -y

# copy source
tarfile=source.tar.gz
tarsource=/tmp/$tarfile
tar -czf $tarsource .
docker cp $tarsource $CONTAINERID:/root/

# untar and 
docker exec -it $CONTAINERID rm -rf /root/source  # temp
docker exec -it $CONTAINERID mkdir /root/source
docker exec -it $CONTAINERID tar -xf /root/$tarfile -C /root/source

# build wheels
docker exec -it $CONTAINERID chmod +x /root/source/docker.sh
docker exec -it $CONTAINERID ./root/source/docker.sh

# copy them back here
docker cp $CONTAINERID:/root/source/dist /tmp/
mv /tmp/dist/*.whl dist/

echo 'Stopping docker:'
docker stop $CONTAINERID
echo 'Stopped'
