#!/bin/bash

#docker run -p 8888:8888 -v ~/PycharmProjects/dasheda/notebook:/home/jovyan ajp/test-notebook:v2

#docker run -p 8888:8888 -v ~/PycharmProjects/dasheda/notebook:/src ajp/test-notebook-ugroup:v1

# export: routedir, name, imagename
export codedir=~/PycharmProjects
export name=ajp
export imagename=test-notebook-ugroup
export tag=v1

pip3 freeze > ugroup/requirements.txt

docker run -p 8888:8888 -v ${codedir}/dasheda/notebook:/src ${name}/${imagename}:${tag}

