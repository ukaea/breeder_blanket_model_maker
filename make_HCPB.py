from main import *

HCPB_blanket_parameters =  {

    'blanket_type' : 'HCPB',
    'envelope_filename' : 'sample_envelope.stp',
    'output_folder' : 'detailed_HCPB',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : 25,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : [30,50,30,25,10],
    'poloidal_segmentations' : [60,5,15,5],

    'cooling_channel_offset_from_first_wall': 3,
    'first_wall_channel_toroidal_mm': 13.5,
    'first_wall_channel_poloidal_mm': 13.5,
    'first_wall_channel_pitch_mm': 4.5,
}

generated_detailed_module = detailed_module(HCPB_blanket_parameters)
