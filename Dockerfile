

# build with
#     sudo docker build -t shimwell/breeder_blanket_model_maker:latest . 
# run with
# docker run -it -v $(pwd):/breeder_blanket_model_maker shimwell/breeder_blanket_model_maker:latest  


FROM ubuntu:xenial

RUN apt-get update \
 && apt-get install -y software-properties-common \
 \
 && apt-add-repository -y ppa:freecad-maintainers/freecad-daily \
 && apt-get update \
 && apt-get install -y freecad-daily \
 \
 && apt-get clean

RUN apt-get --yes install git
RUN apt-get --yes install python-pip
RUN pip install setuptools

RUN git clone https://github.com/ukaea/neutronics_material_maker.git
RUN cd neutronics_material_maker && pip install -r requirements.txt && python setup.py install



RUN git clone https://github.com/inr-kit/McCad.git

RUN apt-get install -y openmpi-bin openmpi-doc libopenmpi-dev
RUN apt-get install -y libx11-dev
RUN apt-get install -y tk8.5-dev
RUN apt-get install -y ftgl-dev
RUN apt-get install -y libxmu-dev
RUN apt-get install -y libqt4-dev
RUN apt-get install -y wget
RUN apt-get install -y cmake

RUN apt-get --yes install make gcc build-essential 
RUN apt-get --yes install libssl-dev
RUN apt-get --yes install qt4-default
RUN apt-get --yes install libboost-all-dev
RUN apt-get --yes install libxerces-c3-dev
RUN apt-get --yes install libfreetype6-dev

RUN export NCPUS=$(getconf _NPROCESSORS_ONLN)


# RUN git clone https://github.com/tpaviot/oce.git
# RUN cd oce && mkdir build && cd build && cmake .. 
# RUN cd oce && cd build && make -j${NCPUS} 
# RUN cd oce && cd build && make install 

RUN apt-get --yes install wget
RUN wget -O OCE-0.9.0.tar.gz https://github.com/tpaviot/oce/archive/OCE-0.9.0.tar.gz
RUN tar -xzvf OCE-0.9.0.tar.gz
RUN cd oce-OCE-0.9.0 && mkdir build 
RUN cd oce-OCE-0.9.0 && cd build && cmake ..
RUN cd oce-OCE-0.9.0 && cd build && make -j${NCPUS}
RUN cd oce-OCE-0.9.0 && cd build && make install


# RUN export CASROOT=/usr/local/share/oce-0.9.0-dev
RUN export CASROOT=/usr/local/share/oce-0.9.0
RUN export CSF_GraphicShr=/usr/local/lib/libTKOpenGl.so 
RUN export CSF_MDTVFontDirectory=$CASROOT/src/FontMFT
RUN export CSF_LANGUAGE=us
RUN export MMGT_CLEAR=1
RUN export CSF_EXCEPTION_PROMPT=1
RUN export CSF_SHMessage=$CASROOT/src/SHMessage
RUN export CSF_MDTVTexturesDirectory=$CASROOT/src/Textures
RUN export CSF_XSMessage=$CASROOT/src/XSMessage
RUN export CSF_StandardDefaults=$CASROOT/src/StdResource
RUN export CSF_PluginDefaults=$CASROOT/src/StdResource
RUN export CSF_XCAFDefaults=$CASROOT/src/StdResource
RUN export CSF_StandardLiteDefaults=$CASROOT/src/StdResource
RUN export CSF_UnitsLexicon=$CASROOT/src/UnitsAPI/Lexi_Expr.dat
RUN export CSF_UnitsDefinition=$CASROOT/src/UnitsAPI/Units.dat
RUN export CSF_IGESDefaults=$CASROOT/src/XSTEPResource
RUN export CSF_STEPDefaults=$CASROOT/src/XSTEPResource
RUN export CSF_XmlOcafResource=$CASROOT/src/XmlOcafResource
RUN export CSF_MIGRATION_TYPES=$CASROOT/src/StdResource/MigrationSheet.txt

RUN git clone https://github.com/Shimwell/McCad-0.5.git


RUN cd McCad-0.5 && mkdir build
RUN cd McCad-0.5 && cd build && cmake ..
RUN cd McCad-0.5 && cd build && make -j${NCPUS}
RUN cd McCad-0.5 && cd build && make install


