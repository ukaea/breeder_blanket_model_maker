import sys
sys.dont_write_bytecode = True

from HCPB_procedure import HCPB_detailed_module
from collections import OrderedDict
import multiprocessing


module_filenames= ['sample_envelope_1.step','sample_envelope_2.step']
list_of_compressed_arguments=[]
for module in module_filenames:



    back_walls_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
    back_walls_thicknesses_ordered_dict['back_wall_1']=30
    back_walls_thicknesses_ordered_dict['back_helium_1']=50
    back_walls_thicknesses_ordered_dict['back_wall_2']=30
    back_walls_thicknesses_ordered_dict['back_helium_2']=25
    back_walls_thicknesses_ordered_dict['back_wall_3']=10

    poloidal_segmentations_ordered_dict=OrderedDict()
    poloidal_segmentations_ordered_dict['neutron_multiplier']=60
    poloidal_segmentations_ordered_dict['cooling_plate_1']=5
    poloidal_segmentations_ordered_dict['breeder_material']=15
    poloidal_segmentations_ordered_dict['cooling_plate_2']=5

    first_wall_channel_poloidal_segmentations_dict=OrderedDict()
    first_wall_channel_poloidal_segmentations_dict['first_wall_material']=13.5
    first_wall_channel_poloidal_segmentations_dict['first_wall_coolant']=4.5


    HCPB_blanket_geometry_parameters =  {

        'envelope_filename' : module,
        'output_folder' : 'detailed_HCPB',
        'first_wall_poloidal_fillet_radius' : 50,
        'armour_thickness' : 2,
        'first_wall_thickness' : 25,
        'end_cap_thickness' : 25,
        'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict, # OrderedDict({'back_wall_1':30,'back_helium_1':50,'back_wall_2':30,'back_helium_2':25,'back_wall_3':10}),
        'poloidal_segmentations' : poloidal_segmentations_ordered_dict, #OrderedDict({'neutron_multiplier':60,'cooling_plate_1':5,'breeder_material':15,'cooling_plate_2':5}),

        #optional comment these three out if you don't want cooling channels in the first wall
        'cooling_channel_offset_from_first_wall': 3,
        'first_wall_channel_radial_mm': 13.5,
        'first_wall_channel_poloidal_segmentations': first_wall_channel_poloidal_segmentations_dict, #13.5,4.5

    }

    #HCPB_module = HCPB_detailed_module(HCPB_blanket_geometry_parameters)
    list_of_compressed_arguments.append(HCPB_blanket_geometry_parameters)



p = multiprocessing.Pool(multiprocessing.cpu_count())

detailed_modules_parts = p.map(HCPB_detailed_module,list_of_compressed_arguments)

