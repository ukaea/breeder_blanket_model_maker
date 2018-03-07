
![all_blankets_image](https://raw.githubusercontent.com/ukaea/breeder_blanket_model_maker/master/all_blankets.jpg)


[![N|Python](https://www.python.org/static/community_logos/python-powered-w-100x40.png)](https://www.python.org)
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
  
### Tech
Breeder_blanket_model_maker uses a number of open source projects to work properly:
* [FreeCAD](https://www.freecadweb.org) -  a fully scriptable open source parametric 3D modeler
* [Python](https://www.python.org) - a programming language that lets you work quickly and integrate systems more effectively.
* [Trelis](http://www.csimsoft.com) - meshing software that also performs imprint and merge opperations required for non overlapping STL geometry.

And of course Breeder_blanket_model_maker itself is open source with a [public repository](https://github.com/ukaea/breeder_blanket_model_maker) on GitHub.

### Installation

Breeder_blanket_model_maker requires [FreeCAD](https://www.freecadweb.org/wiki/Installing) v0.16.670x + to run, Python 2.7 and aptionally Trelis.

### Todos
 - Write MORE Tests
 - Upload tested source code
 - Write user documentation  
 - Write description of methods used to segment (nearly finished)
 - Combine with materials database
 - Generate neutronics output file for tritium production and volumetric heating tally
 - Make a GUI
 - Generate unstrucutred mesh of geometry


   
   
