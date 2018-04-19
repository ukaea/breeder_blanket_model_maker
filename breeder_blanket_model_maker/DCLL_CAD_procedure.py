import sys
sys.dont_write_bytecode = True
sys.path.append('/usr/lib/freecad-daily/lib/')
sys.path.append('/usr/lib/freecad/lib/')
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
from common_CAD_functions import *

def DCLL_detailed_module(blanket_parameters_dict):

        #loads in parameters
        envelope_directory_filename = blanket_parameters_dict['envelope_filename']
        output_folder = blanket_parameters_dict['output_folder']
        output_folder_step = output_folder + '/step'
        output_folder_stl = output_folder + '/stl'
        output_folder_h5m = output_folder + '/h5m'
        output_folder_merged_stl = output_folder + '/merged_stl'
        armour_thickness = blanket_parameters_dict['armour_thickness']
        first_wall_thickness = blanket_parameters_dict['first_wall_thickness']
        end_cap_thickness = blanket_parameters_dict['end_cap_thickness']
        back_walls_thicknesses = blanket_parameters_dict['back_walls_thicknesses']

        if 'plasma_filename' in blanket_parameters_dict:
            plasma_filename = blanket_parameters_dict['plasma_filename']
            plasma = Part.read(plasma_filename)
        else:
            plasma = Part.makeTorus(9100, 2900)

        envelope = Part.read(envelope_directory_filename)

        envelope_back_face = find_envelope_back_face(envelope, plasma)

        envelope_front_face = find_envelope_front_face(envelope, envelope_back_face)

        front_face_midpoint = find_front_face_midpoint(envelope_front_face)

        original_envelope_front_face_id = envelope_front_face_id(envelope,envelope_back_face)

        envelope_back_face_id = find_envelope_back_face_id(envelope, plasma)

        front_face_polodial_edges_to_fillet = find_front_face_polodial_edges_to_fillet(envelope_front_face.Edges)

        front_face_torodial_edges_to_fillet = find_front_face_torodial_edges_to_fillet(envelope_front_face.Edges)


        first_wall_toroidal_fillet_radius = blanket_parameters_dict['first_wall_toroidal_fillet_radius']
        filleted_envelope_solid = filleted_envelope(fillet_radius=first_wall_toroidal_fillet_radius,
                                                   edges=front_face_torodial_edges_to_fillet,
                                                   envelope=envelope)

        filleted_envelope_back_face = find_envelope_back_face(filleted_envelope_solid, plasma)

        filleted_envelope_front_face = find_envelope_front_face(filleted_envelope_solid,filleted_envelope_back_face)

        filleted_envelope_front_face_id = envelope_front_face_id(wedge=filleted_envelope_solid,
                                                                      envelope_back_face=filleted_envelope_back_face)

        end_cap_faces = find_end_cap_faces(faces_under_consideration=filleted_envelope_solid.Faces)

        first_wall_armour, envelope_removed_armour = chop_off_first_wall_armour(armour_thickness = armour_thickness,
                                                                                     faces_not_in_first_wall = [filleted_envelope_back_face] + end_cap_faces,
                                                                                     filleted_envelope = filleted_envelope_solid,
                                                                                     front_face = envelope_front_face)

        dictionary_of_parts = collections.defaultdict(dict)

        dictionary_of_parts['armour']['part'] = [first_wall_armour]

        envelope_removed_armour_end_cap_faces = find_end_cap_faces(faces_under_consideration=envelope_removed_armour.Faces)

        armour_removed_envelope_back_face = find_envelope_back_face(envelope_removed_armour, plasma)

        armour_removed_envelope_front_face = find_envelope_front_face(envelope_removed_armour,
                                                                           armour_removed_envelope_back_face)


        first_wall, first_wall_removed_envelope = chop_off_first_wall(faces_not_in_first_wall=[armour_removed_envelope_back_face] + envelope_removed_armour_end_cap_faces,
                                                                                thickness=first_wall_thickness,
                                                                                filleted_envelope= envelope_removed_armour)

        dictionary_of_parts['first_wall_homogenised']['part'] = [first_wall]

        first_wall_removed_envelope_back_face = find_envelope_back_face(first_wall_removed_envelope,
                                                                             plasma)

        first_wall_removed_envelope_front_face = find_envelope_front_face(first_wall_removed_envelope,
                                                                               first_wall_removed_envelope_back_face)

        first_wall_removed_envelope_midpoint = find_front_face_midpoint(first_wall_removed_envelope_front_face)


        if 'cooling_channel_offset_from_first_wall' in blanket_parameters_dict and 'first_wall_channel_radial_mm' in blanket_parameters_dict and 'first_wall_channel_toroidal_segmentations' in blanket_parameters_dict:

            cooling_channel_offset_from_first_wall = blanket_parameters_dict['cooling_channel_offset_from_first_wall']

            first_wall_channel_radial_mm = blanket_parameters_dict['first_wall_channel_radial_mm']

            first_wall_front_layer, first_wall_removed_envelope_temp1 = chop_off_first_wall(faces_not_in_first_wall=[armour_removed_envelope_back_face] + envelope_removed_armour_end_cap_faces,
                                                                                                      thickness=cooling_channel_offset_from_first_wall,
                                                                                                      filleted_envelope=envelope_removed_armour)

            first_wall_back_layer, first_wall_removed_envelope_temp2 = chop_off_first_wall(faces_not_in_first_wall=[armour_removed_envelope_back_face] + envelope_removed_armour_end_cap_faces,
                                                                                                     thickness=first_wall_channel_radial_mm + cooling_channel_offset_from_first_wall,
                                                                                                     filleted_envelope=envelope_removed_armour)

            first_wall_middle_layer = first_wall.common(first_wall_back_layer).cut(first_wall_front_layer)

            first_wall_back_layer = first_wall.cut(first_wall_back_layer)

            dictionary_of_parts['first_wall_material']['part']=[first_wall_front_layer,first_wall_back_layer]

            first_wall_toroidally_segmented = chop_up_toroidally(toroidal_segmentations =blanket_parameters_dict['first_wall_channel_toroidal_segmentations'],
                                                                      envelope=first_wall_middle_layer,
                                                                      front_face= first_wall_removed_envelope_front_face,
                                                                      front_face_torodial_edges_to_fillet=front_face_torodial_edges_to_fillet)

            for i, key in enumerate(blanket_parameters_dict['first_wall_channel_toroidal_segmentations']):
                dictionary_of_parts[key]['part'] = first_wall_toroidally_segmented[i]

            dictionary_of_parts['first_wall_material']['part'] = dictionary_of_parts['first_wall_material']['part'] + [first_wall_front_layer,first_wall_back_layer]

        end_caps, envelope_removed_endcaps = chop_of_end_caps(end_cap_faces, end_cap_thickness,
                                                                            first_wall_removed_envelope)

        dictionary_of_parts['end_caps_homogenised']['part'] = end_caps

        back_face_envelope_removed_caps = find_envelope_back_face(envelope_removed_endcaps, plasma)

        back_walls, envelope_removed_back_wall = chop_off_back_walls(back_face=back_face_envelope_removed_caps,
                                                                               remaining_shapes=envelope_removed_endcaps,
                                                                               back_walls_thicknesses=back_walls_thicknesses)

        for i, key in enumerate(blanket_parameters_dict['back_walls_thicknesses']):
            dictionary_of_parts[key]['part'] = [back_walls[i]]

        toroidal_segmentations = blanket_parameters_dict['toroidal_segmentations']

        envelope_toroidally_segmented = chop_up_toroidally(toroidal_segmentations=blanket_parameters_dict['toroidal_segmentations'],
                                                                envelope=envelope_removed_back_wall,
                                                                front_face = first_wall_removed_envelope_front_face,
                                                                front_face_torodial_edges_to_fillet = front_face_torodial_edges_to_fillet)

        back_walls_removed_envelope_back_face = find_envelope_back_face(envelope_removed_back_wall, plasma)

        back_walls_removed_envelope_front_face = find_envelope_front_face(envelope_removed_back_wall, back_walls_removed_envelope_back_face)

        back_wall_removed_envelope_radial_depth = back_walls_removed_envelope_back_face.distToShape(back_walls_removed_envelope_front_face)[0]

        radial_segmentations = blanket_parameters_dict['radial_segmentations']

        envelope_radially_segmented = chop_up_envelope_zone_radially_with_adjustable_rear_division(front_face=first_wall_removed_envelope_front_face,
                                                                                                        radial_segmentations=radial_segmentations,
                                                                                                        envelope=envelope_removed_back_wall,
                                                                                                        envelope_radial_depth=back_wall_removed_envelope_radial_depth,
                                                                                                        thinnest_two_layer_blanket=1500)

        top_and_bottom_faces_of_original_envelope = find_poloidal_upper_and_lower_faces(front_face = envelope_front_face,
                                                                                             back_face = envelope_back_face,
                                                                                             envelope = envelope,
                                                                                             envelope_front_face_id=original_envelope_front_face_id,
                                                                                             envelope_back_face_id=envelope_back_face_id)

        poloidal_upper_offset_for_breeder_channel = blanket_parameters_dict['poloidal_upper_offset_for_breeder_channel']

        poloidal_lower_offset_for_breeder_channel = blanket_parameters_dict['poloidal_lower_offset_for_breeder_channel']

        breeder_zone_lithium_cutter_upper = exstrude_and_cut_solids(list_of_distances=[armour_thickness+first_wall_thickness+poloidal_upper_offset_for_breeder_channel],face=top_and_bottom_faces_of_original_envelope[0],envelope=envelope_removed_back_wall)

        poloidal_lower_offset_for_breeder_channel = blanket_parameters_dict['poloidal_lower_offset_for_breeder_channel']

        breeder_zone_lithium_cutter_lower = exstrude_and_cut_solids(list_of_distances=[armour_thickness+first_wall_thickness+poloidal_lower_offset_for_breeder_channel],face=top_and_bottom_faces_of_original_envelope[1],envelope=envelope_removed_back_wall)

        poloidal_upper_offset_for_plate = blanket_parameters_dict['radial_segmentations'][1]

        upper_plate = exstrude_and_cut_solids(list_of_distances=[armour_thickness + first_wall_thickness + poloidal_upper_offset_for_plate + poloidal_upper_offset_for_breeder_channel],face= top_and_bottom_faces_of_original_envelope[0],envelope=envelope_removed_back_wall)[0]

        upper_plate = upper_plate.cut(breeder_zone_lithium_cutter_upper)

        upper_plate = upper_plate.cut(envelope_radially_segmented[0][0])

        additional_lithium_lead_upper,reduced_solids_upper = find_common_bodies(breeder_zone_lithium_cutter_upper,envelope_radially_segmented[1])

        additional_lithium_lead_lower,reduced_solids_lower = find_common_bodies(breeder_zone_lithium_cutter_lower,envelope_radially_segmented[1])

        envelope_radially_segmented[0]= envelope_radially_segmented[0] +additional_lithium_lead_upper + additional_lithium_lead_lower

        lithium_lead =  []
        for radial_ll in envelope_radially_segmented[0]:
            for toroidally_ll in envelope_toroidally_segmented[0]:
                lithium_lead.append((radial_ll.common(toroidally_ll)).cut(upper_plate))

        structural_plate = []
        for radial_plate in envelope_radially_segmented[1]:
            #print('vol=',radial_plate.Volume)
            for chopper in additional_lithium_lead_upper:
                radial_plate=radial_plate.cut(chopper)
                #print('    vol=', radial_plate.Volume)
            for chopper in additional_lithium_lead_lower:
                radial_plate=radial_plate.cut(chopper)
                #print('    vol=', radial_plate.Volume)
            radial_plate=radial_plate.cut(upper_plate)
            #print('')
            for toroidal_plate in envelope_toroidally_segmented[1]:
                upper_plate=upper_plate.cut(toroidal_plate)
                radial_plate = radial_plate.cut(toroidal_plate)

            structural_plate.append(radial_plate)
        structural_plate=structural_plate+envelope_toroidally_segmented[1]+upper_plate.Solids


        available_breezer_zone_materials = [lithium_lead,structural_plate]
        for i,key in enumerate(blanket_parameters_dict['toroidal_segmentations']):

            dictionary_of_parts[key]['part'] = available_breezer_zone_materials[i]


        cylinder_slice = make_cylinder_slice(10)

        prefix='_' + os.path.splitext(os.path.split(envelope_directory_filename)[-1])[0]

        save_components_as_step(dictionary_of_parts = dictionary_of_parts, output_folder = output_folder_step, filename_prefix =prefix)


        save_components_as_merged_stl_file(dictionary_of_parts=dictionary_of_parts,
                                           output_folder=output_folder_merged_stl,
                                           blanket_type=blanket_parameters_dict['blanket_type'])

        save_components_as_stl(dictionary_of_parts = dictionary_of_parts, output_folder = output_folder_stl)

        save_components_as_h5m_file(dictionary_of_parts = dictionary_of_parts, output_folder = output_folder_h5m, blanket_type=blanket_parameters_dict['blanket_type'])


        return dictionary_of_parts