
import sys
sys.dont_write_bytecode = True
sys.path.append('/usr/lib/freecad-daily/lib/')
#sys.path.append('/usr/local/lib/')
import math
import FreeCAD
from FreeCAD import Base
import Part
import os
from collections import Counter
import collections
from collections import OrderedDict
import rewrite_cad_files
import Mesh
import Draft
import MeshPart
from common_functions import *

class HCPB_detailed_module:


    def __init__(self,blanket_parameters_dict):

        #loads in parameters
        self.envelope_directory_filename = blanket_parameters_dict['envelope_filename']
        self.output_folder = blanket_parameters_dict['output_folder']
        self.output_folder_step = self.output_folder + '/step'
        self.output_folder_stl = self.output_folder + '/stl'
        self.armour_thickness = blanket_parameters_dict['armour_thickness']
        self.first_wall_thickness = blanket_parameters_dict['first_wall_thickness']
        self.end_cap_thickness = blanket_parameters_dict['end_cap_thickness']
        self.back_walls_thicknesses = blanket_parameters_dict['back_walls_thicknesses']

        if 'plasma_filename' in blanket_parameters_dict:
            self.plasma_filename = blanket_parameters_dict['plasma_filename']
            self.plasma = Part.read(self.plasma_filename)
        else:
            self.plasma = Part.makeTorus(9100, 2900)

        self.envelope = Part.read(self.envelope_directory_filename)

        self.envelope_back_face = find_envelope_back_face(self.envelope, self.plasma)

        self.envelope_front_face = find_envelope_front_face(self.envelope, self.envelope_back_face)

        self.front_face_midpoint = find_front_face_midpoint(self.envelope_front_face)

        self.envelope_front_face_id = envelope_front_face_id(self.envelope,self.envelope_back_face)

        self.envelope_back_face_id = find_envelope_back_face_id(self.envelope, self.plasma)

        self.front_face_polodial_edges_to_fillet = find_front_face_polodial_edges_to_fillet(self.envelope_front_face.Edges)

        self.front_face_torodial_edges_to_fillet = find_front_face_torodial_edges_to_fillet(self.envelope_front_face.Edges)

        self.first_wall_poloidal_fillet_radius = blanket_parameters_dict['first_wall_poloidal_fillet_radius']

        self.filleted_envelope = filleted_envelope(fillet_radius=self.first_wall_poloidal_fillet_radius,
                                                   edges=self.front_face_polodial_edges_to_fillet,
                                                   envelope=self.envelope)

        self.filleted_envelope_back_face = find_envelope_back_face(self.filleted_envelope, self.plasma)

        self.filleted_envelope_front_face = find_envelope_front_face(self.filleted_envelope,self.filleted_envelope_back_face)

        self.filleted_envelope_front_face_id = envelope_front_face_id(wedge=self.filleted_envelope,
                                                                      envelope_back_face=self.filleted_envelope_back_face)

        self.end_cap_faces = find_end_cap_faces(faces_under_consideration=self.filleted_envelope.Faces)

        self.first_wall_armour, self.envelope_removed_armour = chop_off_first_wall_armour(armour_thickness=self.armour_thickness,
                                                                                          faces_not_in_first_wall=[self.filleted_envelope_back_face] +self.end_cap_faces,
                                                                                          filleted_envelope=self.filleted_envelope,
                                                                                          front_face=self.envelope_front_face)

        self.dictionary_of_parts = collections.defaultdict(dict)

        self.dictionary_of_parts['armour']['part'] = self.first_wall_armour

        self.envelope_removed_armour_end_cap_faces = find_end_cap_faces(faces_under_consideration=self.envelope_removed_armour.Faces)

        self.armour_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_armour, self.plasma)

        self.armour_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_armour,
                                                                           self.armour_removed_envelope_back_face)


        self.first_wall, self.first_wall_removed_envelope = chop_off_first_wall(faces_not_in_first_wall=[self.armour_removed_envelope_back_face] + self.envelope_removed_armour_end_cap_faces,
                                                                                thickness=self.first_wall_thickness,
                                                                                filleted_envelope= self.envelope_removed_armour)


        self.dictionary_of_parts['first_wall_homogenised']['part'] = self.first_wall

        self.first_wall_removed_envelope_back_face = find_envelope_back_face(self.first_wall_removed_envelope, self.plasma)

        self.first_wall_removed_envelope_front_face = find_envelope_front_face(self.first_wall_removed_envelope,self.first_wall_removed_envelope_back_face)

        self.first_wall_removed_envelope_midpoint = find_front_face_midpoint(self.first_wall_removed_envelope_front_face)

        if 'cooling_channel_offset_from_first_wall' in blanket_parameters_dict and 'first_wall_channel_radial_mm' in blanket_parameters_dict and 'first_wall_channel_poloidal_segmentations' in blanket_parameters_dict:

            self.cooling_channel_offset_from_first_wall = blanket_parameters_dict['cooling_channel_offset_from_first_wall']

            self.first_wall_channel_radial_mm = blanket_parameters_dict['first_wall_channel_radial_mm']

            self.first_wall_front_layer, self.first_wall_removed_envelope_temp1 = chop_off_first_wall(faces_not_in_first_wall=[self.armour_removed_envelope_back_face] + self.envelope_removed_armour_end_cap_faces,
                                                                                                      thickness=self.cooling_channel_offset_from_first_wall,
                                                                                                      filleted_envelope=self.envelope_removed_armour)

            self.first_wall_back_layer, self.first_wall_removed_envelope_temp2 = chop_off_first_wall(faces_not_in_first_wall=[self.armour_removed_envelope_back_face] + self.envelope_removed_armour_end_cap_faces,
                                                                                                     thickness=self.first_wall_channel_radial_mm + self.cooling_channel_offset_from_first_wall,
                                                                                                     filleted_envelope=self.envelope_removed_armour)

            self.first_wall_middle_layer = self.first_wall.common(self.first_wall_back_layer).cut(self.first_wall_front_layer)

            self.first_wall_back_layer = self.first_wall.cut(self.first_wall_back_layer)

            self.dictionary_of_parts['first_wall_material']['part'] = [self.first_wall_front_layer, self.first_wall_back_layer]

            self.first_wall_poloidally_segmented = chop_up_poloidally(midpoint=self.first_wall_removed_envelope_midpoint,
                                                                      poloidal_segmentations=blanket_parameters_dict['first_wall_channel_poloidal_segmentations'],
                                                                      envelope=self.first_wall_middle_layer,
                                                                      method='first_wall',
                                                                      top_bottom_edges=self.front_face_torodial_edges_to_fillet,
                                                                      front_face=self.envelope_front_face)

            for i, key in enumerate(blanket_parameters_dict['first_wall_channel_poloidal_segmentations']):
                self.dictionary_of_parts[key]['part'] = self.first_wall_poloidally_segmented[i]

            self.dictionary_of_parts['first_wall_material']['part'] = self.dictionary_of_parts['first_wall_material']['part'] \
                                                                      + [self.first_wall_front_layer, self.first_wall_back_layer]

        self.end_caps, self.envelope_removed_endcaps = chop_of_end_caps(self.end_cap_faces,self.end_cap_thickness,self.first_wall_removed_envelope)

        self.dictionary_of_parts['end_caps_homogenised']['part'] = self.end_caps

        self.back_face_envelope_removed_caps = find_envelope_back_face(self.envelope_removed_endcaps, self.plasma)

        self.back_walls, self.envelope_removed_back_wall = chop_off_back_walls(back_face=self.back_face_envelope_removed_caps,
                                                                               remaining_shapes=self.envelope_removed_endcaps,
                                                                               back_walls_thicknesses=self.back_walls_thicknesses)


        for i, key in enumerate(blanket_parameters_dict['back_walls_thicknesses']):
            self.dictionary_of_parts[key]['part'] = self.back_walls[i]

        self.poloidal_segmentations = blanket_parameters_dict['poloidal_segmentations']

        self.envelope_poloidally_segmented = chop_up_poloidally(midpoint=self.first_wall_removed_envelope_midpoint,
                                                                poloidal_segmentations=self.poloidal_segmentations,
                                                                envelope=self.envelope_removed_back_wall,
                                                                method='HCPB',top_bottom_edges=self.front_face_torodial_edges_to_fillet,
                                                                front_face=self.envelope_front_face)

        self.neutron_multiplier = self.envelope_poloidally_segmented[0]

        self.cooling_plate = self.envelope_poloidally_segmented[1] + self.envelope_poloidally_segmented[3]

        self.breeder_material = self.envelope_poloidally_segmented[2]

        for i, key in enumerate(blanket_parameters_dict['poloidal_segmentations']):
            self.dictionary_of_parts[key]['part'] = self.envelope_poloidally_segmented[i]

        self.cylinder_slice = make_cylinder_slice(10)

        prefix='_' + os.path.splitext(os.path.split(self.envelope_directory_filename)[-1])[0]

        save_components_as_step(dictionary_of_parts = self.dictionary_of_parts, output_folder = self.output_folder_step, filename_prefix =prefix)

        save_components_as_stl(dictionary_of_parts = self.dictionary_of_parts, output_folder = self.output_folder_stl)