from main import *

WCLL_blanket_parameters =  {

    'blanket_type' : 'WCLL',
    'envelope_filename' : 'sample_envelope.stp',
    'output_folder' : 'detailed_WCLL',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 25,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : [15,30,15,30,15],
    'poloidal_segmentations' : [20,35],
    'toroidal_segmentations' : [250,50],
    'radial_segmentations' : [150],
}

detailed_module_WCLL = detailed_module(WCLL_blanket_parameters)