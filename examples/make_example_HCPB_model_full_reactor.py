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


def define_blanket_geometry_parmeters(blanket_type,input_files,output_directory):


    list_of_compressed_arguments=[]
    for module in input_files:

        back_walls_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
        back_walls_thicknesses_ordered_dict['back_plate_1']=30
        back_walls_thicknesses_ordered_dict['back_helium_1']=50
        back_walls_thicknesses_ordered_dict['back_plate_2']=30
        back_walls_thicknesses_ordered_dict['back_helium_2']=25
        back_walls_thicknesses_ordered_dict['back_plate_3']=10

        poloidal_segmentations_ordered_dict=OrderedDict()
        poloidal_segmentations_ordered_dict['neutron_multiplier']=90 #60
        poloidal_segmentations_ordered_dict['cooling_plate_1']=30 #5
        poloidal_segmentations_ordered_dict['breeder_material']=45 #15
        poloidal_segmentations_ordered_dict['cooling_plate_2']=30 #5

        first_wall_channel_poloidal_segmentations_dict=OrderedDict()
        first_wall_channel_poloidal_segmentations_dict['first_wall_material']=13.5
        first_wall_channel_poloidal_segmentations_dict['first_wall_coolant']=4.5

        blanket_geometry_parameters =  {

            'blanket_type' : blanket_type,
            'plasma_filename' :'/home/jshim/Eurofusion_baseline_2016/envelopes/plasma.step',            
            'envelope_filename' : module,
            'output_folder' : output_directory,
            'output_files':['step','stl'],
            'first_wall_poloidal_fillet_radius' : 50,
            'armour_thickness' : 2,
            'first_wall_thickness' : 25,
            'end_cap_thickness' : 25,
            'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict,
            'poloidal_segmentations' : poloidal_segmentations_ordered_dict, 

            # 'cooling_channel_offset_from_first_wall': 3,
            # 'first_wall_channel_radial_mm': 13.5,
            # 'first_wall_channel_poloidal_segmentations': first_wall_channel_poloidal_segmentations_dict, #13.5,4.5

        }

        list_of_compressed_arguments.append(blanket_geometry_parameters)

    return list_of_compressed_arguments


def define_neutronics_materials(enrichment_fraction):


    mat_Li4SiO4 = Compound('Li4SiO4',
                           volume_of_unit_cell_cm3=1.1543e-21,
                           atoms_per_unit_cell=14,
                           packing_fraction=0.6,
                           enriched_isotopes=[Isotope('Li',6,abundance=enrichment_fraction),
                                              Isotope('Li',7,abundance=1.0-enrichment_fraction)])

    mat_Be12Ti = Compound('Be12Ti',
                          volume_of_unit_cell_cm3= 0.22724e-21,
                          atoms_per_unit_cell=2,
                          packing_fraction=0.6)

    material_dictionary = {  'armour': mat_Tungsten,
                             'breeder_material': mat_Li4SiO4,
                             'neutron_multiplier': mat_Be12Ti,
                             'back_plate_1': mat_Eurofer,
                             'back_plate_2': mat_Eurofer,
                             'back_plate_3': mat_Eurofer,
                             'back_helium_1': mat_He_coolant_back_plate,
                             'back_helium_2': mat_He_coolant_back_plate,
                             'cooling_plate_1': mat_cooling_plates_homogenised, #
                             'cooling_plate_2': mat_cooling_plates_homogenised, #
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

                          }
    return material_dictionary

def define_neutronics_model_parmeters(list_detailed_modules_parts,material_dictionary,output_directory,nps=1000,**kwargs):

    neutronics_parameters= { 'output_folder':output_directory,
                             'parts':list_detailed_modules_parts,
                             'include_um_mesh':False,
                             'particle_type':['n'],
                             'output_folder_stl':os.path.join(output_directory,'stl'),
                             'material_dictionary':material_dictionary,
                             'plot_serpent_geometry':False,
                             'nps':nps,
                             'tallies':[{'name':'tbr',
                                            'bodies':['breeder_material','neutron_multiplier'],
                                            'mt_number':-55,
                                            'particle_type':'n'},
                                       ]
                             }



    return neutronics_parameters

output_directory='/home/jshim/detailed_HCPB'
list_of_geometry_parameters = define_blanket_geometry_parmeters(blanket_type ='HCPB',
                                                                input_files= ['/home/jshim/Eurofusion_baseline_2016/envelopes/mod' + str(x) + '.step' for x in range(1, 27)],#27,
                                                                #input_files= ['/home/jshim/Eurofusion_baseline_2016/envelopes/mod1.step'],
                                                                #input_files= ['sample_envelope_1.step','sample_envelope_2.step'],
                                                                output_directory = output_directory)

list_of_detailed_modules_parts = detailed_module(list_of_geometry_parameters)



extra_parts = read_in_step_files_and_save_as_seperate_stl_files(read_folder='/home/jshim/Eurofusion_baseline_2016/reactor_step_files',
                                                                write_folder=os.path.join(output_directory,'stl'),
                                                                ignore_files=['shell.stp'])

list_of_detailed_modules_parts.append(extra_parts)

material_dictionary=define_neutronics_materials(enrichment_fraction=0.8)

neutronics_parameters = define_neutronics_model_parmeters(list_detailed_modules_parts=list_of_detailed_modules_parts,
                                                          material_dictionary=material_dictionary,
                                                          output_directory=output_directory,
                                                          nps=1000)

directory_path_to_serpent_output,number_of_stl_parts= make_serpent_stl_based_input_file(neutronics_parameters)

tally_dict = run_serpent_locally(directory_path_to_serpent_output)    