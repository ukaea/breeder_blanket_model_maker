# this example blanket script uses a design rules to ascertain the first wall thickness and cooling plate thickness from the poloidal height of the lithium lead

from main import *

poloidal_lithium_lead_in_mm = 35.4

smd = 274. * 1000000.  # units Pa

cooling_plates_channel_poloidal_mm = 3.0
cooling_plates_channel_toroidal_mm = 6.0
first_wall_channel_toroidal_mm = 10.0 * 1000.
first_wall_channel_poloidal_mm = 15.0
first_wall_channel_pitch_mm = 5.2

pressure_coolant = 10. * 1000000.  # in units Pa

first_walls_thickness_mm = (first_wall_channel_toroidal_mm/1000) + math.sqrt((pressure_coolant * (poloidal_lithium_lead_in_mm/1000) * (poloidal_lithium_lead_in_mm/1000) ) / (4. * smd))  # units in m

poloidal_cooling_plate_mm = (pressure_coolant * (poloidal_lithium_lead_in_mm)) / (1.1 * smd)

poloidal_cooling_plate_mm = max(poloidal_cooling_plate_mm, 0.002*1000) + cooling_plates_channel_poloidal_mm

cooling_channel_offset_from_first_wall = -(first_walls_thickness_mm - first_wall_channel_toroidal_mm) / 2.0


HCLL_blanket_parameters =  {

    'blanket_type' : 'HCLL',
    'envelope_filename' : 'sample_envelope.stp',
    'output_folder' : 'detailed_HCLL',
    'first_wall_poloidal_fillet_radius' : 50,
    'armour_thickness' : 2,
    'first_wall_thickness' : first_walls_thickness_mm,
    'end_cap_thickness' : 25,
    'back_walls_thicknesses' : [30,50,30,25,10],
    'poloidal_segmentations' : [poloidal_lithium_lead_in_mm,poloidal_cooling_plate_mm],

}

generated_detailed_module = detailed_module(HCLL_blanket_parameters)