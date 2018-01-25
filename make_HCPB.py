

# this example model generator
import sys
sys.dont_write_bytecode = True
from HCPB_procedure import *
from collections import OrderedDict


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

    #'envelope_filename' : 'sample_envelope.stp',
    'envelope_filename' : 'sample_envelope.step',
    'output_folder' : 'detailed_HCPB',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 25,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict, # OrderedDict({'back_wall_1':30,'back_helium_1':50,'back_wall_2':30,'back_helium_2':25,'back_wall_3':10}),
    'poloidal_segmentations' : poloidal_segmentations_ordered_dict, #OrderedDict({'neutron_multiplier':60,'cooling_plate_1':5,'breeder_material':15,'cooling_plate_2':5}),

    'cooling_channel_offset_from_first_wall': 3,
    'first_wall_channel_radial_mm': 13.5,
    'first_wall_channel_poloidal_segmentations': first_wall_channel_poloidal_segmentations_dict, #13.5,4.5
}

HCPB_module = HCPB_detailed_module(HCPB_blanket_geometry_parameters)
