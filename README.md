
![all_blankets_image](https://raw.githubusercontent.com/ukaea/breeder_blanket_model_maker/master/all_blankets.jpg)


[![N|Python](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org)

- [Design goals](#design-goals)
- [Features](#features)
- [Installation](#installation)
- [Getting started](#getting-started)
- [Making HCPB blankets](#making-isotopes)
- [Making HCLL blankets](#making-elements)
- [Making WCLL blankets](#making-compounds)
- [Making DCLL blankets](#making-materials)
- [Todo](#todo)

# Design goals

Breeder_blanket_model_maker is a parametric 3D geometry maker for creating detailed CAD designs of breeder blankets. The main goals of the software are:
  - Automate the process of creating different blanket models
  - Accelerate the use of parametric design in fusion
  - Ease the process of optimising blanket designs across disciplines

# Features
  - Create detailed parametric HCPB, HCLL and WCLL blanket designs
  - Import a blanket envelope model and start forming parts from it
  - Export geometries of different components in STEP and STL format
  - Export first wall armour with your specified thickness
  - Export a first wall with a specified thickness and optional cooling channels
  - Export end caps with a specified thickness
  - Export the desired number of rear walls with desired thicknesses
  - Export polodially segmented breeder zones with uniform or repeating structures
  - Export radially segmented breeder zones with uniform or repeating structures
  - Export toroidally segmented breeder zones with uniform or repeating structures

### Installation

- install the package using pip
```sh
$ pip install breeder_blanket_model_maker
```

- Alternatively install the package by cloning this git repository and install locally
```sh
$ git clone git@github.com:ukaea/breeder_blanket_model_maker.git
$ cd breeder_blanket_model_maker
$ python setup.py install
```

### Installation of dependencies

Breeder_blanket_model_maker relies on a number dependencies of to work properly:
* [FreeCAD](https://www.freecadweb.org) -  a fully scriptable open source parametric 3D modeler
* [Python](https://www.python.org) - a programming language that lets you work quickly and integrate systems more effectively, currently the only Python 2 is suported.
* [Trelis](http://www.csimsoft.com) - (optinal) scriptable meshing software that also performs imprint and merge opperations required for non overlapping STL geometry.


You can [install the latest release of FreeCAD](https://www.freecadweb.org/wiki/Installing) in Ubuntu with the following command :

```sh
sudo apt-get install freecad
```

Alternativly you can install the most recent pre-release version straight from the repository with these commands:
```sh
$ sudo apt-get install software-properties-common python-software-properties
$ sudo add-apt-repository ppa:freecad-maintainers/freecad-daily
$ sudo apt-get update
$ sudo apt-get install freecad-daily && sudo apt-get upgrade
```

You will also need Python installing, currently FreeCAD is supported best by Python 2 and a Python 3 version is under intense development. I hope to upgrade this repository to Python3 soon. To install Python 2 and pip
```sh
$ wget https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz
$ tar -xvf Python-2.7.14.tar.xz
$ cd Python-2.7.14
$ ./configure
$ make
$ make test
$ sudo make install
$ wget https://bootstrap.pypa.io/get-pip.py
$ python get-pip.py

```

Installation of Trelis is best described on the [CSimSoft website](http://www.csimsoft.com/). The DAGMC Trelis plugin is also required and available on the [DAGMC website](https://svalinn.github.io/DAGMC/install/plugin.html)  


### Getting started



### Todos
 - Write MORE Tests
 - Upload tested source code
 - Write user documentation  
 - Write description of methods used to segment (nearly finished)
 - Combine with materials database
 - Generate neutronics output file for tritium production and volumetric heating tally
 - Make a GUI
 - Generate unstrucutred mesh of geometry
