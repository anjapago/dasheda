# dasheda

Running a jupyter notebook in a pod. 

First build the docker image: 

docker build -t $name/$imagename:$tag ./ugroup/

Then run the script bash run_notebook.sh. Export the variables in the terminal. Example commands are shown in the sh file.

## Questions

Entrypoint and CMD:

* what options mean in each
* entrypoint vs cmd

What base image to use?

What is tini, tini version?
