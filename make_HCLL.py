from main import *

HCLL_blanket_parameters =  {

    'blanket_type' : 'HCLL',
    'envelope_filename' : 'sample_envelope.stp',
    'output_folder' : 'detailed_HCLL',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 25,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : [30,50,30,25,10],
    'poloidal_segmentations' : [60,3],

}

generated_detailed_module = detailed_module(HCLL_blanket_parameters)