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
        poloidal_segmentations_ordered_dict['neutron_multiplier']=60
        poloidal_segmentations_ordered_dict['cooling_plate_1']=5
        poloidal_segmentations_ordered_dict['breeder_material']=15
        poloidal_segmentations_ordered_dict['cooling_plate_2']=5

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
                                            'bodies':['breeder_material','neutron_multiplier'],
                                            'mt_number':-55,
                                            'particle_type':'n'},
                                        {'name':'neutron_heating',
                                            'bodies':['armour','breeder_material','neutron_multiplier','back_plate_1','back_plate_2','back_plate_3','back_helium_1','back_helium_2','cooling_plate_1','cooling_plate_2','end_caps_homogenised','first_wall_homogenised'],
                                            'mt_number':-4,
                                            'particle_type':'n'},
                                        {'name':'photon_heating',
                                            'bodies':['armour','breeder_material','neutron_multiplier','back_plate_1','back_plate_2','back_plate_3','back_helium_1','back_helium_2','cooling_plate_1','cooling_plate_2','end_caps_homogenised','first_wall_homogenised'],
                                            'mt_number':-26,
                                            'particle_type':'p'},                                            
                                       ]
                             }

    return neutronics_parameters

output_directory='/home/jshim/detailed_HCPB'
list_of_geometry_parameters = define_blanket_geometry_parmeters(blanket_type ='HCPB',
                                                                input_files= ['sample_envelope_1.step','sample_envelope_2.step'],
                                                                output_directory = output_directory)

list_of_detailed_modules_parts = detailed_module(list_of_geometry_parameters)

material_dictionary=define_neutronics_materials(enrichment_fraction=0.8)

neutronics_parameters = define_neutronics_model_parmeters(list_detailed_modules_parts=list_of_detailed_modules_parts,
                                                          material_dictionary=material_dictionary,
                                                          output_directory=output_directory,
                                                          nps=4000)

directory_path_to_serpent_output,number_of_stl_parts= make_serpent_stl_based_input_file(neutronics_parameters)

tally_dict = run_serpent_locally(directory_path_to_serpent_output)    