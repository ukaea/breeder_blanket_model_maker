import shutil
import sys
sys.dont_write_bytecode = True
sys.path.append('/usr/lib/freecad-daily/lib/')
sys.path.append('/usr/lib/freecad/lib/')

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
import numpy as np
import heapq



def make_cylinder_slice(angle=10):
        radius = 20000
        height = 15000

        cylinder_slice = Part.makeCylinder(radius, height, Base.Vector(0.00, 0.00, -0.5 * height), Base.Vector(0.00, 0.00, 1),angle)
        cylinder_slice = Part.makeCompound([cylinder_slice])
        # cylinder_slice.exportStep(output_folder_stp+"cylinder_slice.stp")
        return cylinder_slice

def components(dictionary_of_parts):
    return dictionary_of_parts
    #return self.dictionary_of_parts




def save_components_as_stl(dictionary_of_parts,output_folder):

    try:
        os.makedirs(output_folder)
    except:
        pass


    for component in dictionary_of_parts:
        filename_list=[]
        file = dictionary_of_parts[component]['step_filename']
        multipart_step = Part.read(file)

        #path =os.path.join(output_folder, os.path.splitext(file)[0] + '_' + str(file_counter) + '.stl')

        file_counter=1
        for solid in multipart_step.Solids:
            solid_mesh = MeshPart.meshFromShape(solid, LinearDeflection=0.01)
            stl_filename= os.path.join(output_folder,os.path.splitext(os.path.split(file)[1])[0]+'_'+str(file_counter)+'.stl')
            filename_list.append(stl_filename)
            print('writing ',stl_filename)
            solid_mesh.write(stl_filename)
            file_counter=file_counter+1
        if len(multipart_step.Solids)==0:
            singlepart_step=multipart_step
            solid_mesh = MeshPart.meshFromShape(singlepart_step, LinearDeflection=0.01)
            stl_filename = os.path.join(output_folder,os.path.splitext(os.path.split(file)[1])[0] + '_' + str(file_counter) + '.stl')
            filename_list.append(stl_filename)
            print('writing ',stl_filename)
            solid_mesh.write(stl_filename)
            file_counter=file_counter+1

        dictionary_of_parts[component]['stl_filename']=filename_list

def fuse_compound_of_solids(all):
    starting_part = all.Solids[0]  # Part.makeSolid(Part.Shape)
    list_of_solids = []
    for solid in all.Solids[1:]:
        print(solid.Volume)
        list_of_solids.append(solid)

        starting_part = starting_part.fuse(solid)
    return starting_part

def save_components_as_step(dictionary_of_parts,output_folder,filename_prefix=''):

    try:
        os.makedirs(output_folder)
    except:
        pass

    for component in dictionary_of_parts:
        dictionary_of_parts[component]['step_filename'] = os.path.join(output_folder,component +filename_prefix+ '.step')
        print(dictionary_of_parts[component])
        print(dictionary_of_parts[component]['step_filename'])
        print(dictionary_of_parts[component]['part'])


        component_compound = Part.makeCompound(dictionary_of_parts[component]['part'])


        if component.startswith('slice_'):
    
            component_compound.exportStep(dictionary_of_parts[component]['step_filename'])
        else:
            
            component_compound_sliced_with_cylinder = component_compound.common(make_cylinder_slice(angle=10))
            # todo
            # allow different angles to be input
            print("dictionary_of_parts[component]['step_filename']",dictionary_of_parts[component]['step_filename'])
            component_compound_sliced_with_cylinder.exportStep(dictionary_of_parts[component]['step_filename'])
    return dictionary_of_parts

def save_components_as_h5m_file(dictionary_of_parts,output_folder,blanket_type):
    # this does not work at the moment
    #os.environ["CUBIT_PLUGIN_DIR"] = '/opt/Trelis-16.4/bin/plugins/svalinn/'
    try:
        os.makedirs(output_folder)
    except:
        pass
    aprepro_output_file_string = ' "output_folder='+"'"+output_folder+"'"+'"'
    aprepro_input_file_string=' "inputs='+"'"
    aprepro_part_name_string =' "parts='+"'"
    for component in dictionary_of_parts:
        aprepro_input_file_string = aprepro_input_file_string+ dictionary_of_parts[component]['step_filename']+','
        aprepro_part_name_string = aprepro_part_name_string + component + ','

    aprepro_input_file_string=aprepro_input_file_string[:-1]+"'" + '"'
    aprepro_part_name_string =aprepro_part_name_string[:-1]+"'" + '"'


    os.system('rm *.jou')
    os.system('export CUBIT_PLUGIN_DIR="/opt/Trelis-16.4/bin/plugins/svalinn/"')
    print('trelis convert_step_files_to_h5m_with_trelis.py'+aprepro_input_file_string+aprepro_part_name_string+aprepro_output_file_string)
    os.system('/opt/Trelis-16.4/bin/trelis  -nographics -batch geometry_utils/convert_step_files_to_h5m_with_trelis.py'+aprepro_input_file_string+aprepro_part_name_string+aprepro_output_file_string)
    #os.system('/opt/Trelis-16.4/bin/trelis -nographics -batch geometry_utils/convert_step_files_to_h5m_with_trelis.py'+aprepro_input_file_string+aprepro_part_name_string+aprepro_output_file_string)

    print('trelis h5m done')


def save_components_as_merged_stl_file(dictionary_of_parts,output_folder,blanket_type):
    #os.environ["CUBIT_PLUGIN_DIR"] ='/opt/Trelis-16.4/bin/plugins/svalinn/'
    try:
        os.makedirs(output_folder)
    except:
        pass
    aprepro_output_file_string = ' "output_folder='+"'"+output_folder+"'"+'"'
    aprepro_input_file_string=' "inputs='+"'"
    aprepro_part_name_string =' "parts='+"'"
    for component in dictionary_of_parts:
        aprepro_input_file_string = aprepro_input_file_string+ dictionary_of_parts[component]['step_filename']+','
        aprepro_part_name_string = aprepro_part_name_string + component + ','

    aprepro_input_file_string=aprepro_input_file_string[:-1]+"'" + '"'
    aprepro_part_name_string =aprepro_part_name_string[:-1]+"'" + '"'


    os.system('rm *.jou')
    print('trelis -nographics -batch convert_step_files_to_stl_with_trelis.py'+aprepro_input_file_string+aprepro_part_name_string+aprepro_output_file_string)
    success = os.system('/opt/Trelis-16.4/bin/trelis -nographics -batch geometry_utils/convert_step_files_to_stl_with_trelis.py'+aprepro_input_file_string+aprepro_part_name_string+aprepro_output_file_string)
    #os.system('/opt/Trelis-16.4/bin/trelis -nographics -batch geometry_utils/convert_step_files_to_h5m_with_trelis.py'+aprepro_input_file_string+aprepro_part_name_string+aprepro_output_file_string)

    print('trelis merged stl done')

    if success == 0:
        return True
    else:
        return False

def find_common_bodies(chopper,chopped):
    common_parts=[]
    un_common_parts=[]

    #Part.makeCompound(chopped).exportStep(os.path.join(settings.output_folder, "chopped.step"))
    #Part.makeCompound(chopper).exportStep(os.path.join(settings.output_folder, "chopper.step"))

    for solid in chopped:
        common_material = solid.common(chopper)
        common_parts.append(common_material)
        un_common_parts.append(solid.cut(chopper))



    return common_parts,un_common_parts

def chop_off_first_wall(faces_not_in_first_wall,thickness,filleted_envelope):


    first_wall = filleted_envelope.makeThickness(faces_not_in_first_wall, -1*thickness, 0)
    smaller_filleted_envelope = filleted_envelope.cut(first_wall)


    return first_wall, smaller_filleted_envelope

def chop_off_first_wall_armour(armour_thickness,faces_not_in_first_wall,filleted_envelope,front_face):


    armour_every_where = filleted_envelope.makeThickness(faces_not_in_first_wall, -1*armour_thickness, 0)
    smaller_filleted_envelope = filleted_envelope.cut(armour_every_where)


    front_face.scale(2.0, front_face.CenterOfMass)
    #big_front_face = front_face#.scale(2.0,front_face.CenterOfMass)
    body1 = front_face.extrude(front_face.normalAt(0, 0) * 50.0)
    body2 = front_face.extrude(front_face.normalAt(0, 0) * -50.0)
    body3 = body2.fuse(body1)

    armour = armour_every_where.common(body3)

    return armour, smaller_filleted_envelope

def envelope_front_face_id(wedge,envelope_back_face):
    print('Finding front face for this wedge ')
    largest_distance = 0
    for counter, face in enumerate(wedge.Faces):
        distance = face.distToShape(envelope_back_face)[0]
        if distance > largest_distance:
            largest_distance = distance
            furthest_face = face
            furthest_face_id = counter
    if not furthest_face:
        print('Front face not found')
        return None
    return furthest_face_id

def find_front_face_polodial_edges_to_fillet(edges_under_consideration):
    list_of_edges_to_fillet = []
    list_of_edge_to_fillet_ids = []

    for counter, edge in enumerate(edges_under_consideration): #self.envelope_front_face.Edges
        #print('        z_diff=', round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z))
        if round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z) != 0:
            list_of_edges_to_fillet.append(edge)
            list_of_edge_to_fillet_ids.append(counter)

    return list_of_edges_to_fillet

def find_front_face_torodial_edges_to_fillet(edges_under_consideration):
    list_of_edges_to_fillet = []
    list_of_edge_to_fillet_ids = []

    for counter, edge in enumerate(edges_under_consideration):
        #print('        z_diff=', round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z))
        if round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z) == 0:
            list_of_edges_to_fillet.append(edge)
            list_of_edge_to_fillet_ids.append(counter)

    return list_of_edges_to_fillet

def find_poloidal_upper_and_lower_faces(front_face,back_face,envelope,envelope_front_face_id,envelope_back_face_id):

    list_of_edges_to_fillet = []
    list_of_edge_to_fillet_ids = []
    list_of_edge_to_fillet_lengths=[]

    for counter, edge in enumerate(front_face.Edges):
        #print('        z_diff=', round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z))
        if round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z) == 0:
            list_of_edges_to_fillet.append(edge)
            list_of_edge_to_fillet_ids.append(counter)
            list_of_edge_to_fillet_lengths.append(edge.Length)

    for counter, edge in enumerate(back_face.Edges):
        #print('        z_diff=', round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z))
        if round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z) == 0:
            list_of_edges_to_fillet.append(edge)
            list_of_edge_to_fillet_ids.append(counter)
            list_of_edge_to_fillet_lengths.append(edge.Length)

    print('list_of_edges_to_fillet',list_of_edges_to_fillet)
    print('list_of_edge_to_fillet_ids',list_of_edge_to_fillet_ids)

    faces_with_vectors_not_pointing_in_y = []

    for i, face in enumerate(envelope.Faces):
        if i != envelope_front_face_id and i != envelope_back_face_id:
            print(face.normalAt(0, 0))
            if abs(face.normalAt(0, 0).y) < max(abs(face.normalAt(0, 0).x), abs(face.normalAt(0, 0).z)):
                faces_with_vectors_not_pointing_in_y.append(face)
                print('appending top bottom face', face.normalAt(0, 0))

    if len(faces_with_vectors_not_pointing_in_y) == 2:
        print('faces_with_vectors_not_pointing_in_y[0].CenterOfMass.z', faces_with_vectors_not_pointing_in_y[0].CenterOfMass.z)
        if faces_with_vectors_not_pointing_in_y[0].CenterOfMass.z > faces_with_vectors_not_pointing_in_y[1].CenterOfMass.z:

            return faces_with_vectors_not_pointing_in_y
        else:
            return faces_with_vectors_not_pointing_in_y[::-1]
    else:
        print('method of finding top bottom faces failed, trying method 2, to many or few faces found')

        top_bottom_faces=[]

        for i, face in enumerate(envelope.Faces):
            if i != self.envelope_front_face_id and i!= self.envelope_back_face_id:

                print('new face')
                list_of_z_points=[]
                for vertexes in face.Vertexes:
                    list_of_z_points.append(round(vertexes.Point.z,1))
                    print('   ',vertexes.Point.z)
                print(list_of_z_points)
                number_of_matching_z_points = Counter(list_of_z_points)


                if number_of_matching_z_points.values() ==[2,2] or number_of_matching_z_points.values() ==[4]:
                    print('pass z')

                    top_bottom_faces.append(face)



        if len(top_bottom_faces)==2:

            # return top_bottom_faces
            print('top_bottom_faces[0].CenterOfMass',top_bottom_faces[0].CenterOfMass)
            if top_bottom_faces[0].CenterOfMass.Point.z > top_bottom_faces[1].CenterOfMass.Point.z:
                return top_bottom_faces
            else:
                return top_bottom_faces[::-1]

        else:

            print('method failed, on '+self.envelope_directory_filename+' to many or few faces found')
            print(top_bottom_faces)
            Part.makeCompound(top_bottom_faces).exportStep(os.path.join(self.output_folder,'error_top_bottom_faces.step'))
            Part.makeCompound([front_face]).exportStep(os.path.join(self.output_folder,'error_top_bottom_faces_ff.step'))

            sys.exit()

def filleted_envelope(fillet_radius,edges,envelope):

    wedge_filleted = envelope.makeFillet(fillet_radius,edges)
    return wedge_filleted

def find_end_cap_faces(faces_under_consideration):
    list_of_top_bottom_faces = []
    list_of_top_bottom_face_ids = []



    for counter, face in enumerate(faces_under_consideration):
        if len(face.Edges) == 6:
            print('found end cap face', face)

            if len(list_of_top_bottom_faces) > 0:
                z_value_of_this_face = face.Vertexes[0].Point.z
                z_value_of_previous_face = list_of_top_bottom_faces[0].Vertexes[0].Point.z

                if z_value_of_this_face > z_value_of_previous_face:
                    list_of_top_bottom_faces = [face] + list_of_top_bottom_faces
                    list_of_top_bottom_face_ids = [counter] + list_of_top_bottom_face_ids
                else:
                    list_of_top_bottom_faces.append(face)
                    list_of_top_bottom_face_ids.append(counter)
            else:
                list_of_top_bottom_faces.append(face)
                list_of_top_bottom_face_ids.append(counter)
    #else:
    #    pass
    #    sys.exit()
        # list_of_potential_faces = []
        #
        #     if len(face.Edges) != 6:
        #         list_of_potential_faces.append(face)




    return list_of_top_bottom_faces

def chop_of_end_caps(end_cap_faces,end_cap_thickness,envelope):

    end_cap_1 = end_cap_faces[0]
    end_cap_1.scale(2.0,end_cap_faces[0].CenterOfMass)
    end_cap_2 = end_cap_faces[1]
    end_cap_2.scale(2.0,end_cap_faces[1].CenterOfMass)

    large_end_cap_1 = end_cap_1.extrude(end_cap_1.normalAt(0, 0) * -end_cap_thickness)
    large_end_cap_2 = end_cap_2.extrude(end_cap_2.normalAt(0, 0) * -end_cap_thickness)

    common_end_cap_1 = large_end_cap_1.common(envelope)
    common_end_cap_2 = large_end_cap_2.common(envelope)

    envelope_end_caps_removed = envelope.cut(Part.makeCompound([common_end_cap_1,common_end_cap_2]))

    return  [common_end_cap_1,common_end_cap_2],envelope_end_caps_removed

def chop_off_back_walls(back_face,remaining_shapes,back_walls_thicknesses):

    back_face.scale(2.0, back_face.CenterOfMass)

    list_of_back_walls=[]
    cumlative_counter = 0
    print('back_walls_thicknesses',back_walls_thicknesses)

    for key in back_walls_thicknesses:
        distance = back_walls_thicknesses[key]
        print('back face distance = ',distance)

        #start_length = cumlative_counter
        cumlative_counter = cumlative_counter + distance
        stop_length = cumlative_counter

        back_face_exstruded = back_face.extrude(back_face.normalAt(0, 0) * -1*stop_length)

        new_shape = back_face_exstruded.common(remaining_shapes)

        #self.dictionary_of_parts[key]['part'] = new_shape

        list_of_back_walls.append(new_shape)

        remaining_shapes=remaining_shapes.cut(back_face_exstruded)


        #self.dictionary_of_parts[key]['part'] = [common_end_cap_1, common_end_cap_2]

    return list_of_back_walls ,remaining_shapes # self.envelope_removed_endcaps.cut(Part.makeCompound(list_of_back_walls))

def find_front_face_midpoint(front_face):
    an_index = 3
    list_of_all_z_vertexis = front_face.Vertexes[0].Point.z, front_face.Vertexes[1].Point.z, front_face.Vertexes[2].Point.z

    z_to_look_for = front_face.Vertexes[an_index].Point.z
    index_of_closest = min(range(len(list_of_all_z_vertexis)),key=lambda x: abs(list_of_all_z_vertexis[x] - z_to_look_for))

    lower_points = [an_index, index_of_closest]
    upper_points = range(4)
    upper_points.remove(an_index)
    upper_points.remove(index_of_closest)

    lower_points_mid_x = (front_face.Vertexes[lower_points[0]].Point.x + front_face.Vertexes[lower_points[1]].Point.x) / 2.0
    lower_points_mid_y = (front_face.Vertexes[lower_points[0]].Point.y + front_face.Vertexes[lower_points[1]].Point.y) / 2.0
    lower_points_mid_z = (front_face.Vertexes[lower_points[0]].Point.z + front_face.Vertexes[lower_points[1]].Point.z) / 2.0

    upper_points_mid_x = (front_face.Vertexes[upper_points[0]].Point.x + front_face.Vertexes[upper_points[1]].Point.x) / 2.0
    upper_points_mid_y = (front_face.Vertexes[upper_points[0]].Point.y + front_face.Vertexes[upper_points[1]].Point.y) / 2.0
    upper_points_mid_z = (front_face.Vertexes[upper_points[0]].Point.z + front_face.Vertexes[upper_points[1]].Point.z) / 2.0

    midpointx = (lower_points_mid_x + upper_points_mid_x) / 2.0
    midpointy = (lower_points_mid_y + upper_points_mid_y) / 2.0
    midpointz = (lower_points_mid_z + upper_points_mid_z) / 2.0

    midpoint = Base.Vector(midpointx, midpointy, midpointz)

    return midpoint

def common_and_uncommon_solids_with_envelope(list_of_solids, slice):
    list_of_common_solids = []
    list_of_not_common_solids = []
    for solid in list_of_solids:
        common_material = solid.common(slice)
        if common_material.Volume > 0:
            list_of_common_solids.append(common_material)
        list_of_not_common_solids.append(solid.cut(slice))
    return list_of_common_solids,list_of_not_common_solids

def chop_up_poloidally(midpoint,poloidal_segmentations,envelope,method,top_bottom_edges,front_face):
    poloidal_segmentations_list=[]
    for key in poloidal_segmentations:
        poloidal_segmentations_list.append(poloidal_segmentations[key])
        print(poloidal_segmentations[key])
    #sys.exit()

    longest = 0
    for edge in envelope.Edges:
        if edge.Length > longest:
            longest = edge.Length
            longest_edge = edge
    print('longest length is ', longest_edge.Length)

    number_of_steps = int(math.ceil(  len(poloidal_segmentations_list)*((longest_edge.Length*1.15)/ sum(poloidal_segmentations_list)  )))

    cumlative_extrusion_lengths1 = convert_distances_into_cumlative_distances(distances =poloidal_segmentations_list, number_of_distances=number_of_steps, half_first_layer=True)

    cumlative_extrusion_lengths2 = [i * -1 for i in cumlative_extrusion_lengths1]

    point1 = FreeCAD.Vector(midpoint + (2000 * front_face.normalAt(0, 0)))
    point2 = FreeCAD.Vector(midpoint - (2000 * top_bottom_edges[1].tangentAt(0)))
    point3 = FreeCAD.Vector(midpoint - (2000 * front_face.normalAt(0, 0)))
    point4 = FreeCAD.Vector(midpoint + (2000 * top_bottom_edges[1].tangentAt(0)))

    poly = Part.makePolygon([point1, point2, point3, point4, point1])
    poly_face = Part.Face(poly)

    if method =='HCPB':
        print('HCPB selected, treading the triangular corners differently')

        slices_of_blanket1=exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_extrusion_lengths1,face=poly_face,envelope=envelope,backtrack_id=4,offset=0)
        slices_of_blanket2=exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_extrusion_lengths2, face=poly_face,envelope=envelope,backtrack_id=4,offset=0)

    if method == 'WCLL':
        print(' WCLL selected, treading the triangular corners differently')

        slices_of_blanket1 = exstrude_and_cut_solids_up_to_change_in_shape_WCLL(list_of_distances=cumlative_extrusion_lengths1, face=poly_face,envelope=envelope,backtrack_id=4,offset=1)
        slices_of_blanket2 = exstrude_and_cut_solids_up_to_change_in_shape_WCLL(list_of_distances=cumlative_extrusion_lengths2, face=poly_face,envelope=envelope,backtrack_id=4,offset=1)

    if method =='first_wall':
        print('first wall selected, treading the triangular corners differently')

        slices_of_blanket1=exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_extrusion_lengths1, face=poly_face,envelope=envelope,backtrack_id=2,offset=0)
        slices_of_blanket2=exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_extrusion_lengths2, face=poly_face,envelope=envelope,backtrack_id=2,offset=0)

    if method =='HCLL':

        slices_of_blanket1 = exstrude_and_cut_solids(list_of_distances=cumlative_extrusion_lengths1, face=poly_face, envelope=envelope)
        slices_of_blanket2 = exstrude_and_cut_solids(list_of_distances=cumlative_extrusion_lengths2, face=poly_face, envelope=envelope)

    if method =='HCLL_slice':

        return exstrude_and_cut_solids(list_of_distances=[cumlative_extrusion_lengths1[0]+
                                                          cumlative_extrusion_lengths1[1]],
                                       face=poly_face, envelope=envelope)



    collection_of_solids=[]

    for counter , key in enumerate( poloidal_segmentations):

        list_from_middle_out_1 = slices_of_blanket1[counter::len(poloidal_segmentations_list)]
        list_from_middle_out_2 = slices_of_blanket2[counter::len(poloidal_segmentations_list)]

        new_list = []
        for i in range(max(len(list_from_middle_out_1), len(list_from_middle_out_2))):
            #print i
            try:
                new_list.append(list_from_middle_out_1[i])
            except:
                pass
            try:
                new_list.append(list_from_middle_out_2[i])
            except:
                pass

        collection_of_solids.append(new_list)

#            self.dictionary_of_parts[key]['part'] = new_list

    return collection_of_solids

def find_largest_face(solid_or_list_of_faces,n=1):
    if type(solid_or_list_of_faces) == list:
        print('a list')
        list_of_faces = solid_or_list_of_faces
    else:
        print('not a list')
        list_of_faces = solid_or_list_of_faces.Faces

    face_sizes=[]
    face_ids=[]
    for face_id, face in enumerate(list_of_faces):
        face_sizes.append(face.Area)
        face_ids.append(face_id)

    print('face_sizes',face_sizes)
    largest_size = heapq.nlargest(n, face_sizes)[-1]

    index_to_return = face_sizes.index(largest_size)


    return list_of_faces[index_to_return] , face_ids[index_to_return]


def chop_top_and_bottom_from_cooling_plate(plate, channel_poloidal_height,plate_poloidal_height):

    print('plate',plate)

    largest_face, largest_face_id=find_largest_face(plate)

    thickness_of_top_bottom_layers = (plate_poloidal_height-channel_poloidal_height)/2.0

#    poly_face.scale(2.0, poly_face.CenterOfMass)

    new_face1 = plate.Faces[largest_face_id].extrude(largest_face.normalAt(0, 0) * thickness_of_top_bottom_layers)

    new_face2 = plate.Faces[largest_face_id].extrude(largest_face.normalAt(0, 0) * -thickness_of_top_bottom_layers)

    top = new_face1.fuse(new_face2)

    new_face1 = plate.Faces[largest_face_id].extrude(largest_face.normalAt(0, 0) * -(channel_poloidal_height +thickness_of_top_bottom_layers ))

    new_face2 = plate.Faces[largest_face_id].extrude(largest_face.normalAt(0, 0) * (channel_poloidal_height +thickness_of_top_bottom_layers ))

    middle = new_face1.fuse(new_face2)

    pre_skinny_div_to_cool = plate.common(middle)
    skinny_div_to_cool = pre_skinny_div_to_cool.cut(top)

    top_bottom = plate.cut(skinny_div_to_cool)

    return skinny_div_to_cool, top_bottom


def add_cooling_pipes_to_div(div_to_cool,channel_poloidal_height,channel_radial_height,plate_poloidal_height,plasma):

    middle, top_bottom = chop_top_and_bottom_from_cooling_plate(plate=div_to_cool,
                                                                channel_poloidal_height=channel_poloidal_height,
                                                                plate_poloidal_height=plate_poloidal_height)

   
    largest_face, largest_face_id = find_largest_face(div_to_cool)

    second_largest_face, second_largest_face_id = find_largest_face(div_to_cool,2)

    back_face = find_envelope_back_face(div_to_cool,plasma)
    back_face_id = find_envelope_back_face_id(div_to_cool,plasma)

    print('face ids ',largest_face_id,second_largest_face_id,back_face_id)

    #faces_not_in_first_wall = [div_to_cool.Faces[largest_face_id],div_to_cool.Faces[second_largest_face_id],div_to_cool.Faces[back_face_id]]
    faces_not_in_first_wall = [largest_face,back_face,second_largest_face]
    print(faces_not_in_first_wall)
    
    #print('poloidal_cooling_plate_mm',poloidal_cooling_plate_mm)

    step_list=[0]
    for c in range(34):#must be and even number to make sure pipe has both front back walls
        if c % 2 == 0:
            step_list.append(step_list[c]+10+c)
            print(step_list[c]+10+(c*1.5))
        else:
            step_list.append(step_list[c]+channel_radial_height)
    print('step_list',step_list)
    print('faces_not_in_first_wall',faces_not_in_first_wall)

    list_of_cooling_pipes=[]
    list_of_structure=[]

    try:
        for counter, step in enumerate(step_list[1:]):
            print(counter,step)

            #cooling_solid = div_to_cool.makeThickness(faces_not_in_first_wall, -step, 0, True)
            cooling_solid = div_to_cool.makeThickness(faces_not_in_first_wall, -step, 0, True)
            print(counter,cooling_solid.Volume)


            if counter==0:

                #save_list_of_solids_to_stp(cooling_solid, 'cooling_solid' + str(counter))
                cooling_solid = cooling_solid.cut(top_bottom)
                list_of_structure.append(cooling_solid)
            else:
                cut_solid= cooling_solid.cut(previous_solid)

                #save_list_of_solids_to_stp(cut_solid, 'cooling_solid' + str(counter))
                #all_solids = cooling_solid.fuse(previous_solid)

                if counter % 2 == 0:
                    cut_solid = cut_solid.cut(top_bottom)
                    list_of_structure.append(cut_solid)
                else:
                    cut_solid=cut_solid.cut(top_bottom)
                    list_of_cooling_pipes.append(cut_solid)


            #if counter!=0 and cut_solid.Volume < 3000000:
            #    break

            previous_solid=cooling_solid
    except:
        print('error the end of the cooling channels has been reached')

    list_of_structure.append(middle.cut(cooling_solid))
    list_of_structure.append(top_bottom)


    return list_of_cooling_pipes,list_of_structure


def chop_up_toroidally(toroidal_segmentations,envelope,front_face_torodial_edges_to_fillet,front_face,number_required=1000): # settings,list_of_envelopes, list_of_front_faces,stp, stl):
    print('chopping up toroidally')
    toroidal_segmentations_list=[]
    for key in toroidal_segmentations:
        #print(toroidal_segmentations[key])
        toroidal_segmentations_list.append(toroidal_segmentations[key])
        #print(toroidal_segmentations[key])

    top_bottom_edges = front_face_torodial_edges_to_fillet

    print('top_bottom_edges com',top_bottom_edges[0].CenterOfMass)

    point1 = top_bottom_edges[0].CenterOfMass
    point2 = FreeCAD.Vector(point1 + front_face.normalAt(0, 0)*3000)
    point3 = top_bottom_edges[1].CenterOfMass
    point4 = FreeCAD.Vector(point3 + front_face.normalAt(0, 0)*3000)

    poly = Part.makePolygon([point1, point2, point4, point3, point1])
    poly_face = Part.Face(poly)

    poly_face.scale(2.0, poly_face.CenterOfMass)

    cumlative_distance_list_left  = convert_distances_into_cumlative_distances(distances=toroidal_segmentations_list,number_of_distances=number_required, half_first_layer=True)
    cumlative_distance_list_right  = [i * -1 for i in cumlative_distance_list_left]

    slices_of_blanket_left  = exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_distance_list_left ,face=poly_face, envelope=envelope,backtrack_id=2,offset=0)
    slices_of_blanket_right  = exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_distance_list_right ,face=poly_face, envelope=envelope,backtrack_id=2,offset=0)

    toroidal_lithium_lead_left , toroidal_cooling_plates_left  = slices_of_blanket_left[::2] , slices_of_blanket_left[1::2]
    toroidal_lithium_lead_right, toroidal_cooling_plates_right = slices_of_blanket_right[::2], slices_of_blanket_right[1::2]

    toroidal_lithium_lead = toroidal_lithium_lead_left + toroidal_lithium_lead_right
    toroidal_cooling_plates = toroidal_cooling_plates_left +toroidal_cooling_plates_right



    #print(toroidal_cooling_plates)

    #Part.makeCompound(toroidal_lithium_lead).exportStep(os.path.join(settings.output_folder_stp, 'toroidal_lithium_lead.step'))
    #Part.makeCompound(toroidal_cooling_plates).exportStep(os.path.join(settings.output_folder_stp, 'toroidal_cooling_plates.step'))
    print('finished chopping up toroidally')
    return [toroidal_lithium_lead,toroidal_cooling_plates]

def chop_up_envelope_zone_radially(radial_segmentations,front_face,envelope,number_required=1000):  # (settings, list_of_remaining_shapes, list_of_front_faces):


    cumlative_distance_list = convert_distances_into_cumlative_distances(radial_segmentations,number_required)

    slices_of_blanket = exstrude_and_cut_solids(cumlative_distance_list, front_face, envelope)

    #print('len(slices_of_blanket)', len(slices_of_blanket))
    #print('slices_of_blanket', slices_of_blanket)

    collection_of_solids = []
    for counter in range(0, len(radial_segmentations)):
        collection_of_solids.append(slices_of_blanket[counter::len(radial_segmentations)] + slices_of_blanket[counter::len(radial_segmentations)])
    return collection_of_solids

def chop_up_envelope_zone_radially_with_adjustable_rear_division(envelope_radial_depth,thinnest_two_layer_blanket,front_face,radial_segmentations,envelope):  # (settings, list_of_remaining_shapes, list_of_front_faces):


    print('this blanket is ',envelope_radial_depth , 'mm')
    print('thinnest_two_layer_blanket is ',thinnest_two_layer_blanket , 'mm')
    if envelope_radial_depth > thinnest_two_layer_blanket:
        number_required=5 #maxvalue
    else:
        number_required=3

    cumlative_distance_list = convert_distances_into_cumlative_distances(radial_segmentations,number_required)
    #print('cumlative_distance_list',cumlative_distance_list)
    cumlative_distance_list[-1]= envelope_radial_depth*1.5

    if number_required==5:
        cumlative_distance_list[-2] = (cumlative_distance_list[1] + ((envelope_radial_depth  - cumlative_distance_list[1])/2)) - radial_segmentations[-1]
        cumlative_distance_list[-3] = cumlative_distance_list[-2] - radial_segmentations[-1]

        print('modified cumlative_distance_list', cumlative_distance_list)

    if number_required==3:
        cumlative_distance_list=[]
        cumlative_distance_list.append( (envelope_radial_depth - radial_segmentations[1])/2.0)
        cumlative_distance_list.append( cumlative_distance_list[0] + radial_segmentations[1])
        cumlative_distance_list.append( envelope_radial_depth*1.5)


    slices_of_blanket = exstrude_and_cut_solids(cumlative_distance_list, front_face, envelope)

    #print('len(slices_of_blanket)', len(slices_of_blanket))
    #print('slices_of_blanket', slices_of_blanket)

    collection_of_solids = []
    for counter in range(0, len(radial_segmentations)):
        collection_of_solids.append(slices_of_blanket[counter::len(radial_segmentations)])# + slices_of_blanket[counter::len(self.radial_segmentations)])
    return collection_of_solids

def convert_distances_into_cumlative_distances(distances, number_of_distances, half_first_layer=False):
    distance_list = []




    for counter in range(0, number_of_distances):#/ len(distances)))):
        for counter2 in distances:
            distance_list.append(counter2)
    distance_list=distance_list[:number_of_distances]

    if half_first_layer == True:
        distance_list[0] = distance_list[0] * 0.5

    #print('distance_list', distance_list)
    #print('sum(distance_list)', sum(distance_list))
    cumlative_distance_list = []
    for x in distance_list:
        if len(cumlative_distance_list) > 0:
            cumlative_distance_list.append(cumlative_distance_list[-1] + x)
        else:
            cumlative_distance_list.append(x)

    #print('cumlative_distance_list', cumlative_distance_list)
    return cumlative_distance_list

def exstrude_and_cut_solids(list_of_distances,face,envelope):
    large_face = face
    large_face.scale(2.0, large_face.CenterOfMass)
    list_of_thick_faces = []
    for counter, sweep in enumerate(list_of_distances):
        distance = -1 *sweep
        if counter == 0:
            thick_face = large_face.extrude(large_face.normalAt(0, 0) * distance)
            remaining_thick_face = thick_face.common(envelope)
        else:
            thick_face = large_face.extrude(large_face.normalAt(0, 0) * distance)
            old_thick_face = large_face.extrude(large_face.normalAt(0, 0) *-1*list_of_distances[counter-1])
            remaining_thick_face=thick_face.cut(old_thick_face)
            remaining_thick_face = remaining_thick_face.common(envelope)
        #print(remaining_thick_face.Volume)
        if remaining_thick_face.Volume == 0:
            #print('zero volume found, no longer exstruding')
            break
        list_of_thick_faces.append(remaining_thick_face)

    return list_of_thick_faces

def exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances, face, envelope, backtrack_id,offset):
    large_face = face
    large_face.scale(2.0, large_face.CenterOfMass)
    list_of_thick_faces = []
    for counter, sweep in enumerate(list_of_distances):
        distance = -1 * sweep
        if counter == 0:
            thick_face = large_face.extrude(large_face.normalAt(0, 0) * distance)
            remaining_thick_face = thick_face.common(envelope)
            number_of_faces_in_each_sweep = len(remaining_thick_face.Faces)
        else:
            thick_face = large_face.extrude(large_face.normalAt(0, 0) * distance)
            old_thick_face = large_face.extrude(large_face.normalAt(0, 0) * -1 * list_of_distances[counter - 1])
            remaining_thick_face = thick_face.cut(old_thick_face)
            remaining_thick_face = remaining_thick_face.common(envelope)

            if (counter +offset)% backtrack_id == 0:
                #print('first layer repeate', list_of_distances[counter])
                previous_neutron_multiplier_layer = counter
        print(counter,remaining_thick_face.Volume)
        if remaining_thick_face.Volume == 0:
            print('zero volume found, no longer exstruding')
            break
        if len(remaining_thick_face.Faces) != number_of_faces_in_each_sweep:
            print('solids have got the wrong number of faces, no longer exstruding')
            break
        list_of_thick_faces.append(remaining_thick_face)

    #print('before', len(list_of_thick_faces))
    list_of_thick_faces = list_of_thick_faces[:previous_neutron_multiplier_layer]
    #print('after', len(list_of_thick_faces))

    both_end_caps = envelope.cut(list_of_thick_faces[-1]).Solids

    if len(both_end_caps) == 2:
        if both_end_caps[0].Volume > both_end_caps[1].Volume:
            list_of_thick_faces.append(both_end_caps[1])
        else:
            list_of_thick_faces.append(both_end_caps[0])

    return list_of_thick_faces

def exstrude_and_cut_solids_up_to_change_in_shape_WCLL(list_of_distances, face, envelope, backtrack_id,offset):
    large_face = face
    large_face.scale(2.0, large_face.CenterOfMass)
    list_of_thick_faces = []
    for counter, sweep in enumerate(list_of_distances):
        distance = -1 * sweep
        if counter == 0:
            thick_face = large_face.extrude(large_face.normalAt(0, 0) * distance)
            remaining_thick_face = thick_face.common(envelope)
            number_of_faces_in_each_sweep = len(remaining_thick_face.Faces)
        else:
            thick_face = large_face.extrude(large_face.normalAt(0, 0) * distance)
            old_thick_face = large_face.extrude(large_face.normalAt(0, 0) * -1 * list_of_distances[counter - 1])
            remaining_thick_face = thick_face.cut(old_thick_face)
            remaining_thick_face = remaining_thick_face.common(envelope)

        if remaining_thick_face.Volume == 0:
            print('zero volume found, no longer exstruding')
            break
        if len(remaining_thick_face.Faces) != number_of_faces_in_each_sweep:
            print('solids have got the wrong number of faces, no longer exstruding')
            break
        list_of_thick_faces.append(remaining_thick_face)

    print('number of wcll layers before', len(list_of_thick_faces))
    if len(list_of_thick_faces)%2==0:  #even
        print('even, removing one layer')
        list_of_thick_faces = list_of_thick_faces[:-1]
    if (len(list_of_thick_faces)+1) % 4 != 0:  # this is a long layer, we can't end with this
        print('long, removing two layers')
        list_of_thick_faces = list_of_thick_faces[:-2]


    print('number of wcll layers  after', len(list_of_thick_faces))

    both_end_caps = envelope.cut(list_of_thick_faces[-1]).Solids

    if len(both_end_caps) == 2:
        if both_end_caps[0].Volume > both_end_caps[1].Volume:
            list_of_thick_faces.append(both_end_caps[1])
        else:
            list_of_thick_faces.append(both_end_caps[0])

    return list_of_thick_faces

def find_envelope_back_face(wedge,plasma):
    print('Finding face furthest from the plasma for ',wedge)
    largest_distance = 0

    #for counter, face in enumerate(self.envelope.Faces):
    for counter, face in enumerate(wedge.Faces):
        distance = face.distToShape(plasma)[0]
        if distance > largest_distance:
            largest_distance = distance
            furthest_face = face
            furthest_face_id = counter
    if not furthest_face:
        print('Back face not found')
        return None
    return wedge.Faces[furthest_face_id]

def find_envelope_back_face_id(wedge,plasma):
    print('Finding face furthest from the plasma for ',wedge)
    largest_distance = 0

    #for counter, face in enumerate(self.envelope.Faces):
    for counter, face in enumerate(wedge.Faces):
        distance = face.distToShape(plasma)[0]
        if distance > largest_distance:
            largest_distance = distance
            furthest_face = face
            furthest_face_id = counter
    if not furthest_face:
        print('Back face not found')
        return None
    return furthest_face_id

def find_envelope_front_face(wedge,back_face):
    print('Finding front face for ' ,wedge)
    largest_distance = 0
    if not back_face :
        back_face=find_envelope_back_face(wedge)
    for counter, face in enumerate(wedge.Faces):
        distance = face.distToShape(back_face)[0]
        #print('distance',distance)
        if distance > largest_distance:
            largest_distance = distance
            furthest_face = face
            furthest_face_id = counter
    if not furthest_face:
        print('Front face not found')
        return None
    return furthest_face

