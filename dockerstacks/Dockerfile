 # Let's extend from the base notebook
 # https://github.com/jupyter/docker-stacks/blob/master/base-notebook
 FROM jupyter/base-notebook

 # Install required packages on top of base Jupyter image
 RUN pip install --no-cache \
   scipy \
   numpy \
   pandas \
   scikit-learn \
   matplotlib 

 # Copy all files (current directory onwards) into the image
 COPY . /