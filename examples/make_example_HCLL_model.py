import sys
sys.dont_write_bytecode = True
from collections import OrderedDict
import multiprocessing

from breeder_blanket_model_maker import *

# from breeder_blanket_model_maker.HCLL_CAD_procedure import *

def generate_CAD_model(blanket_type):

    poloidal_lithium_lead_in_mm = 35.4

    smd = 274. * 1000000.  # units Pa

    cooling_plates_channel_poloidal_mm = 3.0
    cooling_plates_channel_radial_mm = 3.0
    cooling_plates_channel_toroidal_mm = 6.0
    first_wall_channel_radial_mm = 10.0
    first_wall_channel_poloidal_mm = 15.0
    first_wall_channel_pitch_mm = 5.2

    pressure_coolant = 10. * 1000000.  # in units Pa

    first_walls_thickness = (first_wall_channel_radial_mm/1000) + math.sqrt((pressure_coolant * (poloidal_lithium_lead_in_mm/1000) * (poloidal_lithium_lead_in_mm/1000) ) / (4. * smd))  # units in m
    first_walls_thickness_mm = first_walls_thickness *1000

    poloidal_cooling_plate_mm = (pressure_coolant * (poloidal_lithium_lead_in_mm)) / (1.1 * smd)

    poloidal_cooling_plate_mm = max(poloidal_cooling_plate_mm, 0.002*1000) + cooling_plates_channel_poloidal_mm

    cooling_channel_offset_from_first_wall = (first_walls_thickness_mm - first_wall_channel_radial_mm) / 2.0

    if cooling_channel_offset_from_first_wall < 1.0:
        print('first wall is too thin at ',cooling_channel_offset_from_first_wall, 'mm')
        sys.exit()

    poloidal_segmentations_ordered_dict=OrderedDict()
    poloidal_segmentations_ordered_dict['lithium_lead']=poloidal_lithium_lead_in_mm
    poloidal_segmentations_ordered_dict['cooling_plate']=poloidal_cooling_plate_mm

    back_walls_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
    back_walls_thicknesses_ordered_dict['back_wall_1']=30
    back_walls_thicknesses_ordered_dict['back_helium']=50
    back_walls_thicknesses_ordered_dict['back_wall_2']=30
    back_walls_thicknesses_ordered_dict['back_lithium_lead']=25
    back_walls_thicknesses_ordered_dict['back_wall_3']=10

    first_wall_channel_poloidal_segmentations_dict=OrderedDict()
    first_wall_channel_poloidal_segmentations_dict['first_wall_material']=first_wall_channel_poloidal_mm
    first_wall_channel_poloidal_segmentations_dict['first_wall_coolant']=first_wall_channel_pitch_mm



    module_filenames= ['sample_envelope_1.step','sample_envelope_2.step']
    list_of_compressed_arguments=[]
    for module in module_filenames:


        blanket_geometry_parameters =  {

            'blanket_type' : blanket_type,
            'envelope_filename' : module,
            'output_folder' : 'detailed_'+blanket_type,
            'first_wall_poloidal_fillet_radius' : 50,
            'armour_thickness' : 2,
            'first_wall_thickness' : first_walls_thickness_mm,
            'end_cap_thickness' : 25,
            'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict,
            'poloidal_segmentations' : poloidal_segmentations_ordered_dict,

            #The following three arguments are optional, if included the model will include cooling channels on the first wall
            'cooling_channel_offset_from_first_wall': cooling_channel_offset_from_first_wall,
            'first_wall_channel_radial_mm': first_wall_channel_radial_mm,
            'first_wall_channel_poloidal_segmentations': first_wall_channel_poloidal_segmentations_dict,  # 13.5,4.5

            #The following two arguments are optional, if included the model will include a slice of blanket and cooling channels in the cooling plate
            'cooling_plates_channel_poloidal_mm':cooling_plates_channel_poloidal_mm,
            'cooling_plates_channel_radial_mm':cooling_plates_channel_radial_mm
        }

        list_of_compressed_arguments.append(blanket_geometry_parameters)

    p = multiprocessing.Pool(multiprocessing.cpu_count()-1)

    if blanket_type=='HCLL':
        detailed_modules_parts = p.map(HCLL_detailed_module,list_of_compressed_arguments)

    return detailed_modules_parts

detailed_modules_parts = generate_CAD_model(blanket_type = 'HCLL')
