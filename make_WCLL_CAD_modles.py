import sys
sys.dont_write_bytecode = True
from collections import OrderedDict
import multiprocessing

from geometry_utils.WCLL_CAD_procedure import *

module_filenames= ['sample_envelope_1.step','sample_envelope_2.step']
list_of_compressed_arguments=[]
for module in module_filenames:

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

    WCLL_blanket_geometry_parameters =  {

        'envelope_filename' : module,
        'output_folder' : 'detailed_WCLL',
        'first_wall_poloidal_fillet_radius' : 50,
        'armour_thickness' : 2,
        'first_wall_thickness' : 25,
        'end_cap_thickness' : 25,
        'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict,
        'poloidal_segmentations' : poloidal_segmentations_ordered_dict,
        'toroidal_segmentations' : toroidal_segmentations_ordered_dict,
        'radial_segmentations' : [150],

        'cooling_channel_offset_from_first_wall': 3,
        'first_wall_channel_radial_mm': 13.5,
        'first_wall_channel_poloidal_segmentations': first_wall_channel_poloidal_segmentations_dict,  # 13.5,4.5

    }

    #detailed_module_WCLL = WCLL_detailed_module(WCLL_blanket_parameters)

    list_of_compressed_arguments.append(WCLL_blanket_geometry_parameters)


p = multiprocessing.Pool(multiprocessing.cpu_count()-1)

detailed_modules_parts = p.map(WCLL_detailed_module,list_of_compressed_arguments)