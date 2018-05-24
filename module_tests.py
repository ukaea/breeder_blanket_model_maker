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

import random
import unittest
import pytest




class HCLL_tests(unittest.TestCase):


    list_of_compressed_arguments=[]
    for module in ['sample_envelope_1.step','sample_envelope_2.step']: #mod 1 is cut

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

            'blanket_type' : 'HCPB',      
            'envelope_filename' : module,
            'output_folder' : '/home/detailed_HCPB2',
            'output_files':['step','stl'],
            'first_wall_poloidal_fillet_radius' : 50,
            'armour_thickness' : 2,
            'first_wall_thickness' : 25,
            'end_cap_thickness' : 25,
            'back_walls_thicknesses' : back_walls_thicknesses_ordered_dict,
            'poloidal_segmentations' : poloidal_segmentations_ordered_dict, 
        }

        list_of_compressed_arguments.append(blanket_geometry_parameters)

    global HCPB_dictionary_of_parts 

    HCPB_dictionary_of_parts=detailed_module_non_para(list_of_compressed_arguments)




    def test_armour_number_of_solids(self):
        for blanket_module in HCPB_dictionary_of_parts:
            multipart_step = Part.read(blanket_module['armour']['step_filename'])
            print('number of solids =', len(multipart_step.Solids) )
            assert len(multipart_step.Solids) == 1

    # def test_armour_number_of_faces(self):
    #     multipart_step = Part.read(HCPB_dictionary_of_parts_envelope_1['armour']['step_filename'])
    #     print('number of faces =', len(multipart_step.Solids[0].Faces ))
    #     assert len(multipart_step.Solids[0].Faces) == 10

    # def test_first_wall_homogenised_number_of_solids(self):
    #     multipart_step = Part.read(HCPB_dictionary_of_parts_envelope_1['first_wall_homogenised']['step_filename'])
    #     print('number of solids =', len(multipart_step.Solids) )
    #     assert len(multipart_step.Solids) == 1

    # def test_first_wall_homogenised_number_of_faces(self):
    #     multipart_step = Part.read(HCPB_dictionary_of_parts_envelope_1['first_wall_homogenised']['step_filename'])
    #     print('number of faces =', len(multipart_step.Solids[0].Faces ))
    #     assert len(multipart_step.Solids[0].Faces) == 10        

    # def test_end_caps_number_of_solids(self):
    #     multipart_step = Part.read(HCPB_dictionary_of_parts_envelope_1['end_caps_homogenised']['step_filename'])
    #     print('number of solids =', len(multipart_step.Solids) )
    #     assert len(multipart_step.Solids) == 2

    # def test_end_caps_number_of_faces(self):
    #     multipart_step = Part.read(HCPB_dictionary_of_parts_envelope_1['end_caps_homogenised']['step_filename'])
    #     print('number of faces =',len(multipart_step.Solids[0].Faces ))
    #     print('number of faces =',len(multipart_step.Solids[1].Faces ))
    #     assert len(multipart_step.Solids[0].Faces) == 7           
    #     assert len(multipart_step.Solids[1].Faces) == 7           

    #todo
    #def test_armour_thickness(self):
    #def test_first_wall_thickness
    #def test_first_wall_number_of_solids
    #def test_first_wall_number_of_faces
    #def test volumes compared to STL files
    #def test volumes compared to other STEP files (ratio of thicknesses)
    #def test watertightness of all STL and STEP?







class DCLL_tests(unittest.TestCase):

    #todo tests go here
    def test_element_protons(self):

        assert 2==2



class WCLL_tests(unittest.TestCase):
    #todo tests go here
    def test_compound_class_name(self):

        assert 1==1



class HCPB_tests(unittest.TestCase):
    #todo tests go here
    def test_material_serpent_card_creation(self):

        assert 1==1
 