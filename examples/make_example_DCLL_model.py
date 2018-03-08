import sys
sys.dont_write_bytecode = True
from collections import OrderedDict
import multiprocessing

from breeder_blanket_model_maker import *


def generate_CAD_model(blanket_type):

    module_filenames= ['sample_envelope_1.step','sample_envelope_2.step']
    list_of_compressed_arguments=[]
    for module in module_filenames:

        back_walls_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
        back_walls_thicknesses_ordered_dict['back_wall_1']=20
        back_walls_thicknesses_ordered_dict['back_wall_2']=10
        back_walls_thicknesses_ordered_dict['back_helium_1']=45
        back_walls_thicknesses_ordered_dict['back_wall_3']=10
        back_walls_thicknesses_ordered_dict['back_helium_2']=45
        back_walls_thicknesses_ordered_dict['back_wall_4']=10
        back_walls_thicknesses_ordered_dict['back_wall_5']=20

        toroidal_segmentations_ordered_dict=OrderedDict()
        toroidal_segmentations_ordered_dict['lithium_lead']=25
        toroidal_segmentations_ordered_dict['structural_plate']=35

        first_wall_channel_toroidal_segmentations_dict=OrderedDict()
        first_wall_channel_toroidal_segmentations_dict['first_wall_material']=13.5
        first_wall_channel_toroidal_segmentations_dict['first_wall_coolant']=4.5

        blanket_geometry_parameters =  {

            'blanket_type' : blanket_type,
            'envelope_filename' : module,
            'output_folder' : 'detailed_'+blanket_type,
            'first_wall_toroidal_fillet_radius':50,
            'armour_thickness':2,
            'first_wall_thickness':25,
            'end_cap_thickness':25,
            'back_walls_thicknesses':back_walls_thicknesses_ordered_dict,
            'toroidal_segmentations':toroidal_segmentations_ordered_dict,
            'radial_segmentations':[250, 15],
            'poloidal_upper_offset_for_breeder_channel':150,
            'poloidal_lower_offset_for_breeder_channel':150,

            # 'cooling_channel_offset_from_first_wall': 3,
            # 'first_wall_channel_radial_mm': 13.5,
            # 'first_wall_channel_toroidal_segmentations': first_wall_channel_toroidal_segmentations_dict,  # 13.5,4.5

        }

        list_of_compressed_arguments.append(blanket_geometry_parameters)

    p = multiprocessing.Pool(multiprocessing.cpu_count()-1)

    if blanket_type=='DCLL':
        detailed_modules_parts = p.map(DCLL_detailed_module,list_of_compressed_arguments)

    return detailed_modules_parts

generate_CAD_model(blanket_type = 'DCLL')