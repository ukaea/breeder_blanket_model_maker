from main import *

DCLL_blanket_parameters =  {

    'blanket_type' : 'DCLL',
    'envelope_filename' : 'sample_envelope.stp',
    'output_folder' : 'detailed_DCLL',
    'first_wall_toroidal_fillet_radius':50,
    'armour_thickness':2,
    'first_wall_thickness':25,
    'end_cap_thickness':25,
    'back_walls_thicknesses':[20,10,45,10,45,10,20],
    'toroidal_segmentations':[80,20],
    'radial_segmentations':[250, 15],
    'poloidal_upper_offset_for_breeder_channel':150,
    'poloidal_lower_offset_for_breeder_channel':150

}

generated_detailed_module = detailed_module(DCLL_blanket_parameters)