import sys
sys.dont_write_bytecode = True
from collections import OrderedDict
import multiprocessing
import math
from breeder_blanket_model_maker import *
from breeder_blanket_model_maker.rewrite_cad_files import *
from breeder_blanket_model_maker.serpent_tools import *
from breeder_blanket_model_maker.make_serpent_input_file import *

from neutronics_material_maker.nmm import *
from neutronics_material_maker.examples import *

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def define_blanket_geometry_parmeters(blanket_type,input_files,output_directory):


    list_of_compressed_arguments=[]
    for module in input_files:

        back_walls_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
        back_walls_thicknesses_ordered_dict['back_plate_1']=20
        back_walls_thicknesses_ordered_dict['back_plate_2']=10
        back_walls_thicknesses_ordered_dict['back_helium_1']=45
        back_walls_thicknesses_ordered_dict['back_plate_3']=10
        back_walls_thicknesses_ordered_dict['back_helium_2']=45
        back_walls_thicknesses_ordered_dict['back_plate_4']=10
        back_walls_thicknesses_ordered_dict['back_plate_5']=20

        toroidal_segmentations_ordered_dict=OrderedDict()
        toroidal_segmentations_ordered_dict['lithium_lead']=25
        toroidal_segmentations_ordered_dict['structural_plate']=35

        first_wall_channel_toroidal_segmentations_dict=OrderedDict()
        first_wall_channel_toroidal_segmentations_dict['first_wall_material']=13.5
        first_wall_channel_toroidal_segmentations_dict['first_wall_coolant']=4.5

        blanket_geometry_parameters =  {

            'blanket_type' : blanket_type,
            'plasma_filename' :'/home/jshim/Eurofusion_baseline_2016/envelopes/plasma.step',            
            'envelope_filename' : module,
            'output_folder' : output_directory,
            'output_files':['step','stl'],            
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

    return list_of_compressed_arguments


def define_neutronics_materials(enrichment_fraction):

    mat_lithium_lead =Compound('Pb84.2Li15.8',
                              density_atoms_per_barn_per_cm=3.2720171E-2,
                              enriched_isotopes=[Isotope('Li',6,abundance=enrichment_fraction),
                                                 Isotope('Li',7,abundance=1.0-enrichment_fraction)])

    material_dictionary = {  'armour': mat_Tungsten,
                             'lithium_lead': mat_lithium_lead,
                             'back_plate_1': mat_Eurofer,
                             'back_plate_2': mat_Eurofer,
                             'back_plate_3': mat_Eurofer,
                             'back_plate_4': mat_Eurofer,
                             'back_plate_5': mat_Eurofer,
                             'back_lithium_lead': mat_lithium_lead,
                             'back_helium_1': mat_He_coolant_back_plate,
                             'back_helium_2': mat_He_coolant_back_plate,
                             'structural_plate': mat_cooling_plates_homogenised, #
                             'end_caps_homogenised': mat_end_caps_homogenised,
                             'first_wall_homogenised': mat_first_wall_homogenised,
                             'plasma': mat_DT_plasma,
                             'central_solenoid': mat_central_solenoid_m25,
                             'divertor_1st_layer': mat_divertor_layer_1_m15, 
                             'divertor_2nd_layer': mat_divertor_layer_2_m74, 
                             'divertor_3rd_layer': mat_divertor_layer_3_m15,
                             'divertor_4th_layer': mat_divertor_layer_4_m75,
                             'manifolder': mat_VV_Body_m60 ,
                             'ports': mat_TF_Casing_m50,
                             #'shell': , # outer shell ignored
                             'shield': mat_TF_Casing_m50,
                             'tf_case': mat_TF_Casing_m50,
                             'tf_coils': mat_TF_Magnet_m25,
                             'vacuum_1st_layer': mat_VV_Shell_m50,
                             'vacuum_2nd_layer': mat_VV_Body_m60,
                             'vacuum_3rd_layer': mat_VV_Shell_m50,
                             'vaccum_vessel_shield': mat_ShieldPort_m60,
                             'blanket_support':mat_Eurofer,

                             'first_wall_coolant':mat_He_in_first_walls,
                             'first_wall_material':mat_He_in_first_walls,

                             'slice_lithium_lead':mat_lithium_lead,
                             'slice_armour':mat_Tungsten,
                             'slice_first_wall_material':mat_Eurofer,
                             'slice_first_wall_homogenised':mat_first_wall_homogenised, #ignore
                             'slice_first_wall_coolant':mat_He_in_first_walls,
                             'slice_cooling_plate_material':mat_cooling_plates_homogenised,
                             'slice_cooling_plate_coolant':mat_He_in_coolant_plates,
                             'slice_back_plate_1':mat_Eurofer,
                             'slice_back_helium':mat_He_coolant_back_plate,
                             'slice_back_plate_2':mat_Eurofer,
                             'slice_back_lithium_lead':mat_lithium_lead,
                             'slice_back_plate_3':mat_Eurofer,
                          }
    return material_dictionary



def define_neutronics_model_parmeters(list_detailed_modules_parts,material_dictionary,output_directory,nps=1e7,**kwargs):

    neutronics_parameters= { 'output_folder':output_directory,
                             'parts':list_detailed_modules_parts,
                             'include_um_mesh':False,
                             'output_folder_stl':os.path.join(output_directory,'stl'),
                             'material_dictionary':material_dictionary,
                             'plot_serpent_geometry':False,
                             'nps':nps,
                             'tallies':[{'name':'tbr',
                                            'bodies':['lithium_lead'],
                                            'mt_number':-55,
                                            'particle_type':'n'},
                                        {'name':'neutron_heating',
                                            'bodies':['armour','lithium_lead','back_plate_1','back_plate_2','back_plate_3','back_plate_4','back_plate_5','back_helium_1','back_helium_2','structural_plate','end_caps_homogenised','first_wall_homogenised'],
                                            'mt_number':-4,
                                            'particle_type':'n'},
                                        {'name':'photon_heating',
                                            'bodies':['armour','lithium_lead','back_plate_1','back_plate_2','back_plate_3','back_plate_4','back_plate_5','back_helium_1','back_helium_2','structural_plate','end_caps_homogenised','first_wall_homogenised'],
                                            'mt_number':-26,
                                            'particle_type':'p'},                                            
                                       ]
                             }

    return neutronics_parameters


output_directory='/home/jshim/detailed_DCLL'
list_of_geometry_parameters = define_blanket_geometry_parmeters(blanket_type = 'DCLL',
                                                                input_files= ['/home/jshim/Eurofusion_baseline_2016/envelopes/mod' + str(x) + '.step' for x in range(1, 27)],#27,['sample_envelope_1.step','sample_envelope_2.step'],
                                                                output_directory=output_directory)


list_of_detailed_modules_parts = detailed_module(list_of_geometry_parameters)

extra_parts = read_in_step_files_and_save_as_seperate_stl_files(read_folder='/home/jshim/Eurofusion_baseline_2016/reactor_step_files',
                                                                write_folder=os.path.join(output_directory,'stl'),
                                                                ignore_files=['shell.stp'])

list_of_detailed_modules_parts.append(extra_parts)

material_dictionary=define_neutronics_materials(enrichment_fraction=0.9)

neutronics_parameters = define_neutronics_model_parmeters(list_detailed_modules_parts=list_of_detailed_modules_parts,
                                                          material_dictionary=material_dictionary,
                                                          output_directory=output_directory,
                                                          nps=10000)

directory_path_to_serpent_output,number_of_stl_parts= make_serpent_stl_based_input_file(neutronics_parameters)

tally_dict = run_serpent_locally(directory_path_to_serpent_output)




