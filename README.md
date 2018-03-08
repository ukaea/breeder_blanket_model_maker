
![all_blankets_image](images/all_blankets.jpg)


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

# Installation

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


# Getting started

In general to make a detailed breeder blanket you simply import the breeder_blanket_model_maker decide upon the dimentions of various components and provide a blanket envelope. The following code is incomplete but provides a skeleton example.

```python
from breeder_blanket_model_maker import *

blanket_geometry_parameters =  {
# identify a blanket type (WCLL, HCLL, HCPB, HCLL)
...
# assign dimentions to all required components
...
# provide a blanket envelope
}
detailed_module(blanket_geometry_parameters)
```

Two example blanket envelopes are provided with the package for users to experiment with. These can be used by setting the *envelope_filename* equal to "sample_envelope_1.step" or "sample_envelope_2.step". Sample 1 and 2 differ in terms of their position in the reactor.

![sample_envelope_1](images/sample_envelope_1_small.png)
![sample_envelope_2](images/sample_envelope_2_small.png)



### Making HCPB blankets

To make a Helium Cooled Pebble Bed Blanket (HCPB) the package must be imported. The envelope filename must be specified, here we use one of the example envelopes. The output folder for generated STL, STEP and h5m files must be specified. The dimentions of various componets must also be stated. The order of the back walls and poloidal segmentations is important so and orderedDict type has been used (Python 2 dones not presever order of dictionaries). Here is an example input:

```python
from breeder_blanket_model_maker import *

blanket_geometry_parameters =  {
    'blanket_type' : 'HCPB',
    'envelope_filename' : 'sample_envelope_1.step',
    'output_folder' : 'detailed_HCPB',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 25,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : OrderedDict({'back_wall_1':30,
                                            'back_helium_1':50,
                                            'back_wall_2':30,
                                            'back_helium_2':25,
                                            'back_wall_3':10}),
    'poloidal_segmentations' : OrderedDict({'neutron_multiplier':60,
                                            'cooling_plate_1':5,
                                            'breeder_material':15,
                                            'cooling_plate_2':5}),
    # 'cooling_channel_offset_from_first_wall': 3,
    # 'first_wall_channel_radial_mm': 13.5,
    # 'first_wall_channel_poloidal_segmentations': OrderedDict({'first_wall_material':13.5,
    #                                                          'first_wall_coolant':4.5})                                            
    }

detailed_blanket(blanket_geometry_parameters)
```
Running the above code will generate a 3D detailed blanket design for your enevelope. A slice through the resulting geometry will looks like the following image:

![sample_envelope_2](images/HCPB_small.png)

Additional detail can be added by uncommenting *cooling_channel_offset_from_first_wall*,*first_wall_channel_radial_mm* and *first_wall_channel_poloidal_segmentations* from the above example.



### Making HCLL blankets

```python

blanket_geometry_parameters =  {

    'blanket_type' : 'HCLL',
    'envelope_filename' : 'sample_envelope_1.step',,
    'output_folder' : 'detailed_HCLL',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 20,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : OrderedDict({'back_wall_1':30,
                                            'back_helium_1':50,
                                            'back_wall_2':30,
                                            'back_lithium_lead':25,
                                            'back_wall_3':10}),
    'poloidal_segmentations' : OrderedDict({'lithium_lead':30,
                                            'cooling_plate_1':50})

    # 'cooling_channel_offset_from_first_wall': 3,
    # 'first_wall_channel_radial_mm': 13.5,
    # 'first_wall_channel_poloidal_segmentations': OrderedDict({'first_wall_material':13.5,
    #                                                          'first_wall_coolant':4.5})
}

detailed_blanket(blanket_geometry_parameters)
```


### Making WCLL blankets

To make a basic Helium Cooled Pebble Bed breeder blanket you simply import the breeder_blanket_model_maker decide upon the dimentions of various components and provide a blanket envelope.

```python
from breeder_blanket_model_maker import *

back_walls_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
back_walls_thicknesses_ordered_dict['back_wall_1']=15
back_walls_thicknesses_ordered_dict['back_wall_2']=30
back_walls_thicknesses_ordered_dict['back_wall_3']=15
back_walls_thicknesses_ordered_dict['back_wall_4']=30
back_walls_thicknesses_ordered_dict['back_wall_5']=15

poloidal_segmentations_ordered_dict=OrderedDict()
poloidal_segmentations_ordered_dict['lithium_lead']=25
poloidal_segmentations_ordered_dict['structural_plate']=35

toroidal_segmentations_ordered_dict=OrderedDict()
toroidal_segmentations_ordered_dict['lithium_lead']=25
toroidal_segmentations_ordered_dict['structural_plate']=35

first_wall_channel_poloidal_segmentations_dict=OrderedDict()
first_wall_channel_poloidal_segmentations_dict['first_wall_material']=13.5
first_wall_channel_poloidal_segmentations_dict['first_wall_coolant']=4.5

blanket_geometry_parameters =  {

    'blanket_type' : 'WCLL',
    'envelope_filename' : 'sample_envelope_1.step',
    'output_folder' : 'detailed_WCLL',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 25,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict,
    'poloidal_segmentations' : poloidal_segmentations_ordered_dict,
    'toroidal_segmentations' : toroidal_segmentations_ordered_dict,
    'radial_segmentations' : [150],

}
WCLL_detailed_module(blanket_geometry_parameters)
```



### Making DCLL blankets

### Todos
 - Write MORE Tests
 - Upload tested source code
 - Write user documentation  
 - Write description of methods used to segment (nearly finished)
 - Combine with materials database
 - Generate neutronics output file for tritium production and volumetric heating tally
 - Make a GUI
 - Generate unstrucutred mesh of geometry
