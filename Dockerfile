FROM ubuntu:16.04

MAINTAINER Jonathan Shimwell  

# This docker image contains all the dependencies required to run breeder_blanket_model_maker.
# More details on breeder_blanket_model_maker are on the github webpage
# https://github.com/ukaea/breeder_blanket_model_maker

# build with
#     sudo docker build -t shimwell/breeder_blanket_model_maker_dependencies:latest . 
# run with
#     docker run -it -v $(pwd):/breeder_blanket_model_maker breeder_blanket_model_maker
# push to docker store with 
#     docker login
#     docker push shimwell/breeder_blanket_model_maker:latest




# Install additional packages

RUN apt-get --yes update && apt-get --yes upgrade

RUN apt-get --yes install make gcc build-essential 

# RUN apt-get --yes install libssl-dev libgd-dev


RUN apt-get -y install wget

RUN apt-get --yes install libssl-dev

RUN export NCPUS=$(getconf _NPROCESSORS_ONLN)
         
RUN wget https://www.python.org/ftp/python/3.4.0/Python-3.4.0.tgz && tar xf Python-3.4.0.tgz && cd Python-3.4.0 && ./configure --prefix=/usr/local --with-ensurepip=install --enable-optimizations --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib" && make -j${NCPUS} && make install

# 
# 
# 
RUN apt-get --yes install git

RUN apt-get --yes install python3-tk
# 
# RUN apt-get --yes install python-dev
# 
RUN apt-get --yes install cmake

RUN apt-get --yes install qt4-default

RUN apt-get --yes install git
RUN pip3 install --upgrade pip
RUN pip3 install numpy 
RUN pip3 install pandas
RUN pip3 install codecov 
RUN pip3 install pytest-cov
RUN pip3 install pylint
RUN pip3 install PySide
# 
RUN apt-get --yes install libboost-all-dev
# 
RUN apt-get --yes install software-properties-common #python-software-properties
RUN add-apt-repository ppa:freecad-maintainers/freecad-stable
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get --yes install freecad
# 
# WORKDIR /
# 
# 