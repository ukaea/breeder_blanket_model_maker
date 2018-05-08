import sys
sys.dont_write_bytecode = True
from collections import OrderedDict
import multiprocessing
import math
from breeder_blanket_model_maker import *
from breeder_blanket_model_maker.rewrite_cad_files import *
from breeder_blanket_model_maker.serpent_tools import *
from breeder_blanket_model_maker.make_serpent_input_file import *

from neutronics_material_maker import *
from neutronics_material_maker.examples import *



# from breeder_blanket_model_maker.HCLL_CAD_procedure import *

def define_blanket_geometry_parmeters(blanket_type,poloidal_lithium_lead_in_mm = 35.4):

    # poloidal_lithium_lead_in_mm = 35.4

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
        raise ValueError('first wall is too thin at ',cooling_channel_offset_from_first_wall, 'mm')

    poloidal_segmentations_ordered_dict=OrderedDict()
    poloidal_segmentations_ordered_dict['lithium_lead']=poloidal_lithium_lead_in_mm
    poloidal_segmentations_ordered_dict['cooling_plate_homogenised']=poloidal_cooling_plate_mm

    back_plates_thicknesses_ordered_dict=OrderedDict()  #these are special ordereddict types required in python 2.7 but in python 3.6 onwards dictionaries are ordered by default, sadly freecad is not yet avaialbe in python 3
    back_plates_thicknesses_ordered_dict['back_plate_1']=30
    back_plates_thicknesses_ordered_dict['back_helium']=50
    back_plates_thicknesses_ordered_dict['back_plate_2']=30
    back_plates_thicknesses_ordered_dict['back_lithium_lead']=25
    back_plates_thicknesses_ordered_dict['back_plate_3']=10

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
            'output_files':['step','stl'],
            'first_wall_poloidal_fillet_radius' : 50,
            'armour_thickness' : 2,
            'first_wall_thickness' : first_walls_thickness_mm,
            'end_cap_thickness' : 25,
            'back_plates_thicknesses' : back_plates_thicknesses_ordered_dict,
            'poloidal_segmentations' : poloidal_segmentations_ordered_dict,

            # #The following three arguments are optional, if included the model will include cooling channels on the first wall
            # 'cooling_channel_offset_from_first_wall': cooling_channel_offset_from_first_wall,
            # 'first_wall_channel_radial_mm': first_wall_channel_radial_mm,
            # 'first_wall_channel_poloidal_segmentations': first_wall_channel_poloidal_segmentations_dict,  # 13.5,4.5

            # #The following two arguments are optional, if included the model will include a slice of blanket and cooling channels in the cooling plate
            # 'cooling_plates_channel_poloidal_mm':cooling_plates_channel_poloidal_mm,
            # 'cooling_plates_channel_radial_mm':cooling_plates_channel_radial_mm
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

                             'back_lithium_lead': mat_lithium_lead,

                             'back_helium': mat_He_coolant_back_plate,

                             'cooling_plate_homogenised': mat_cooling_plates_homogenised,

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

def define_neutronics_model_parmeters(list_detailed_modules_parts,blanket_geometry_parameters,material_dictionary,**kwargs):

    dictionary_of_blanket_parts = list_detailed_modules_parts[0]

    for dictionary_of_parts in list_of_detailed_modules_parts[1:]:
        for key, value in dictionary_of_parts.items():
            print('key=',key)
            for subkey, subvalue in value.items():
                #print('    subkey=',subkey)
                #print('        type(subkey)=',type(subkey))
                dictionary_of_blanket_parts[key][subkey]=dictionary_of_blanket_parts[key][subkey]+dictionary_of_parts[key][subkey]


    dictionary_of_parts = dictionary_of_blanket_parts.copy()

    if extra_parts in kwargs.keys():
        dictionary_of_parts.update(extra_parts)




    for component in dictionary_of_parts:
            if component in material_dictionary.keys():
                dictionary_of_parts[component]['material']=material_dictionary[component]
                #print('adding ',component)
            elif component.replace('slice_', '') in material_dictionary.keys():
                dictionary_of_parts[component]['material']=material_dictionary[component.replace('slice_', '')]
            else:
                raise ValueError('Error. component not found in materials dictionary',component)

    neutronics_parameters= { 'output_folder':blanket_geometry_parameters['output_folder'],
                             'parts':dictionary_of_parts,
                             'include_um_mesh':False,
                             'output_folder_stl':os.path.join(blanket_geometry_parameters['output_folder'],'stl'),
                             'material_dictionary':material_dictionary,
                             'material_description_for_tbr_tally':material_dictionary['lithium_lead'].material_card_name,
                             'list_of_cells_to_tbr_tally':['lithium_lead']+['back_lithium_lead'],
                             'plot_serpent_geometry':False,
                             'include_photons':False,
                             'nps':1000
                             }



    return neutronics_parameters



list_of_geometry_parameters = define_blanket_geometry_parmeters(blanket_type ='HCLL',
                                                                poloidal_lithium_lead_in_mm =34.5)

list_of_detailed_modules_parts = detailed_module(list_of_geometry_parameters)


extra_parts = read_in_step_files_and_save_as_seperate_stl_files(read_folder='Eurofusion_baseline_2016/reactor_step_files',
                                                               write_folder=os.path.join(list_of_geometry_parameters[0]['output_folder'],'stl'),
                                                               ignore_files=['shell.stp'])

material_dictionary=define_neutronics_materials(0.8)

neutronics_parameters = define_neutronics_model_parmeters(list_of_detailed_modules_parts,
                                                          list_of_geometry_parameters[0],
                                                          material_dictionary,
                                                          extra_parts=extra_parts)

directory_path_to_serpent_output,number_of_stl_parts= make_serpent_stl_based_input_file(neutronics_parameters)

tally_dict = run_serpent_locally(directory_path_to_serpent_output)

print(tally_dict['tbr'])
print(tally_dict['tbr_error'])
