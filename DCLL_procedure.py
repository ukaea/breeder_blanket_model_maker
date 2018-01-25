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

class DCLL_detailed_module:

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


        self.first_wall_toroidal_fillet_radius = blanket_parameters_dict['first_wall_toroidal_fillet_radius']
        self.filleted_envelope = filleted_envelope(fillet_radius=self.first_wall_toroidal_fillet_radius,
                                                   edges=self.front_face_torodial_edges_to_fillet,
                                                   envelope=self.envelope)

        self.filleted_envelope_back_face = find_envelope_back_face(self.filleted_envelope, self.plasma)

        self.filleted_envelope_front_face = find_envelope_front_face(self.filleted_envelope,self.filleted_envelope_back_face)

        self.filleted_envelope_front_face_id = envelope_front_face_id(wedge=self.filleted_envelope,
                                                                      envelope_back_face=self.filleted_envelope_back_face)

        self.end_cap_faces = find_end_cap_faces(faces_under_consideration=self.filleted_envelope.Faces)

        self.first_wall_armour, self.envelope_removed_armour = chop_off_first_wall_armour(armour_thickness = self.armour_thickness,
                                                                                     faces_not_in_first_wall = [self.filleted_envelope_back_face] + self.end_cap_faces,
                                                                                     filleted_envelope = self.filleted_envelope,
                                                                                     front_face = self.envelope_front_face)

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

        self.first_wall_removed_envelope_back_face = find_envelope_back_face(self.first_wall_removed_envelope,
                                                                             self.plasma)

        self.first_wall_removed_envelope_front_face = find_envelope_front_face(self.first_wall_removed_envelope,
                                                                               self.first_wall_removed_envelope_back_face)

        self.first_wall_removed_envelope_midpoint = find_front_face_midpoint(self.first_wall_removed_envelope_front_face)


        if 'cooling_channel_offset_from_first_wall' in blanket_parameters_dict and 'first_wall_channel_radial_mm' in blanket_parameters_dict and 'first_wall_channel_toroidal_segmentations' in blanket_parameters_dict:

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

            self.dictionary_of_parts['first_wall_material']['part']=[self.first_wall_front_layer,self.first_wall_back_layer]

            self.first_wall_toroidally_segmented = chop_up_toroidally(toroidal_segmentations =blanket_parameters_dict['first_wall_channel_toroidal_segmentations'],
                                                                      envelope=self.first_wall_middle_layer,
                                                                      front_face= self.first_wall_removed_envelope_front_face,
                                                                      front_face_torodial_edges_to_fillet=self.front_face_torodial_edges_to_fillet)

            for i, key in enumerate(blanket_parameters_dict['first_wall_channel_toroidal_segmentations']):
                self.dictionary_of_parts[key]['part'] = self.first_wall_toroidally_segmented[i]

            self.dictionary_of_parts['first_wall_material']['part'] = self.dictionary_of_parts['first_wall_material']['part'] + [self.first_wall_front_layer,self.first_wall_back_layer]

        self.end_caps, self.envelope_removed_endcaps = chop_of_end_caps(self.end_cap_faces, self.end_cap_thickness,
                                                                            self.first_wall_removed_envelope)

        self.dictionary_of_parts['end_caps_homogenised']['part'] = self.end_caps

        self.back_face_envelope_removed_caps = find_envelope_back_face(self.envelope_removed_endcaps, self.plasma)

        self.back_walls, self.envelope_removed_back_wall = chop_off_back_walls(back_face=self.back_face_envelope_removed_caps,
                                                                               remaining_shapes=self.envelope_removed_endcaps,
                                                                               back_walls_thicknesses=self.back_walls_thicknesses)

        for i, key in enumerate(blanket_parameters_dict['back_walls_thicknesses']):
            self.dictionary_of_parts[key]['part'] = self.back_walls[i]

        self.toroidal_segmentations = blanket_parameters_dict['toroidal_segmentations']

        self.envelope_toroidally_segmented = chop_up_toroidally(toroidal_segmentations=blanket_parameters_dict['toroidal_segmentations'],
                                                                envelope=self.envelope_removed_back_wall,
                                                                front_face = self.first_wall_removed_envelope_front_face,
                                                                front_face_torodial_edges_to_fillet = self.front_face_torodial_edges_to_fillet)

        self.back_walls_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_back_wall, self.plasma)

        self.back_walls_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_back_wall, self.back_walls_removed_envelope_back_face)

        self.back_wall_removed_envelope_radial_depth = self.back_walls_removed_envelope_back_face.distToShape(self.back_walls_removed_envelope_front_face)[0]

        self.radial_segmentations = blanket_parameters_dict['radial_segmentations']

        self.envelope_radially_segmented = chop_up_envelope_zone_radially_with_adjustable_rear_division(front_face=self.first_wall_removed_envelope_front_face,
                                                                                                        radial_segmentations=self.radial_segmentations,
                                                                                                        envelope=self.envelope_removed_back_wall,
                                                                                                        envelope_radial_depth=self.back_wall_removed_envelope_radial_depth,
                                                                                                        thinnest_two_layer_blanket=1500)

        self.top_and_bottom_faces_of_original_envelope = find_poloidal_upper_and_lower_faces(front_face = self.envelope_front_face,
                                                                                             back_face = self.envelope_back_face,
                                                                                             envelope = self.envelope,
                                                                                             envelope_front_face_id=self.envelope_front_face_id,
                                                                                             envelope_back_face_id=self.envelope_back_face_id)

        self.poloidal_upper_offset_for_breeder_channel = blanket_parameters_dict['poloidal_upper_offset_for_breeder_channel']

        self.poloidal_lower_offset_for_breeder_channel = blanket_parameters_dict['poloidal_lower_offset_for_breeder_channel']

        self.breeder_zone_lithium_cutter_upper = exstrude_and_cut_solids(list_of_distances=[self.armour_thickness+self.first_wall_thickness+self.poloidal_upper_offset_for_breeder_channel],face=self.top_and_bottom_faces_of_original_envelope[0],envelope=self.envelope_removed_back_wall)

        self.poloidal_lower_offset_for_breeder_channel = blanket_parameters_dict['poloidal_lower_offset_for_breeder_channel']

        self.breeder_zone_lithium_cutter_lower = exstrude_and_cut_solids(list_of_distances=[self.armour_thickness+self.first_wall_thickness+self.poloidal_lower_offset_for_breeder_channel],face=self.top_and_bottom_faces_of_original_envelope[1],envelope=self.envelope_removed_back_wall)

        self.poloidal_upper_offset_for_plate = blanket_parameters_dict['radial_segmentations'][1]

        self.upper_plate = exstrude_and_cut_solids(list_of_distances=[self.armour_thickness + self.first_wall_thickness + self.poloidal_upper_offset_for_plate + self.poloidal_upper_offset_for_breeder_channel],face= self.top_and_bottom_faces_of_original_envelope[0],envelope=self.envelope_removed_back_wall)[0]

        self.upper_plate = self.upper_plate.cut(self.breeder_zone_lithium_cutter_upper)

        self.upper_plate = self.upper_plate.cut(self.envelope_radially_segmented[0][0])

        self.additional_lithium_lead_upper,self.reduced_solids_upper = find_common_bodies(self.breeder_zone_lithium_cutter_upper,self.envelope_radially_segmented[1])

        self.additional_lithium_lead_lower,self.reduced_solids_lower = find_common_bodies(self.breeder_zone_lithium_cutter_lower,self.envelope_radially_segmented[1])

        self.envelope_radially_segmented[0]= self.envelope_radially_segmented[0] +self.additional_lithium_lead_upper + self.additional_lithium_lead_lower

        self.lithium_lead =  []
        for radial_ll in self.envelope_radially_segmented[0]:
            for toroidally_ll in self.envelope_toroidally_segmented[0]:
                self.lithium_lead.append((radial_ll.common(toroidally_ll)).cut(self.upper_plate))

        self.structural_plate = []
        for radial_plate in self.envelope_radially_segmented[1]:
            #print('vol=',radial_plate.Volume)
            for chopper in self.additional_lithium_lead_upper:
                radial_plate=radial_plate.cut(chopper)
                #print('    vol=', radial_plate.Volume)
            for chopper in self.additional_lithium_lead_lower:
                radial_plate=radial_plate.cut(chopper)
                #print('    vol=', radial_plate.Volume)
            radial_plate=radial_plate.cut(self.upper_plate)
            #print('')
            for toroidal_plate in self.envelope_toroidally_segmented[1]:
                self.upper_plate=self.upper_plate.cut(toroidal_plate)
                radial_plate = radial_plate.cut(toroidal_plate)

            self.structural_plate.append(radial_plate)
        self.structural_plate=self.structural_plate+self.envelope_toroidally_segmented[1]+self.upper_plate.Solids


        available_breezer_zone_materials = [self.lithium_lead,self.structural_plate]
        for i,key in enumerate(blanket_parameters_dict['toroidal_segmentations']):

            self.dictionary_of_parts[key]['part'] = available_breezer_zone_materials[i]


        self.cylinder_slice = make_cylinder_slice(10)

        prefix='_' + os.path.splitext(os.path.split(self.envelope_directory_filename)[-1])[0]

        save_components_as_step(dictionary_of_parts = self.dictionary_of_parts, output_folder = self.output_folder_step, filename_prefix =prefix)

        save_components_as_stl(dictionary_of_parts = self.dictionary_of_parts, output_folder = self.output_folder_stl)