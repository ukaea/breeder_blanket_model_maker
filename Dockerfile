FROM ubuntu:16.04

MAINTAINER Jonathan Shimwell  

# This docker image contains all the dependencies required to run breeder_blanket_model_maker.
# More details on breeder_blanket_model_maker are on the github webpage
# https://github.com/ukaea/breeder_blanket_model_maker

# build with
#     sudo docker build -t shimwell/breeder_blanket_model_maker_dependencies:latest . 
# run with
#     docker run breeder_blanket_model_maker_dependencies 
# push to docker store with 
#     docker login
#     docker push shimwell/breeder_blanket_model_maker_dependencies:latest




# Install additional packages

RUN apt-get --yes update && apt-get --yes upgrade

RUN apt-get --yes install make gcc build-essential libgd2-noxpm-dev libgd-dev

RUN apt-get --yes install python-pip python-tk

RUN apt-get --yes install build-essential python-dev

RUN apt-get --yes install cmake

RUN apt-get --yes install qt4-default

RUN apt-get --yes install git

RUN pip install --upgrade pip
RUN pip install numpy 
RUN pip install pandas
RUN pip install codecov 
RUN pip install pytest-cov
RUN pip install pylint
RUN pip install PySide


RUN apt-get --yes install software-properties-common python-software-properties
RUN add-apt-repository ppa:freecad-maintainers/freecad-stable
RUN apt-get --yes update && apt-get --yes upgrade
RUN apt-get --yes install freecad

WORKDIR /

