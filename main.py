
import sys
sys.dont_write_bytecode = True
sys.path.append('/usr/lib/freecad-daily/lib/')
sys.path.append('/usr/local/lib/')
import math
import FreeCAD
from FreeCAD import Base
import Part
import os


class detailed_module:

    def __init__(self,blanket_parameters_dict):

        self.blanket_type = blanket_parameters_dict['blanket_type']
        self.envelope_directory_filename = blanket_parameters_dict['envelope_filename']
        self.output_folder = blanket_parameters_dict['output_folder']
        

        self.armour_thickness = blanket_parameters_dict['armour_thickness']
        self.first_wall_thickness = blanket_parameters_dict['first_wall_thickness']
        self.end_cap_thickness = blanket_parameters_dict['end_cap_thickness']
        self.back_walls_thicknesses = blanket_parameters_dict['back_walls_thicknesses']

        try:
            self.plasma_filename = blanket_parameters_dict['plasma_filename']
            self.plasma = Part.read(self.plasma_filename)
        except:
            self.plasma = Part.makeTorus(9100,2900)

        

        self.envelope = Part.read(self.envelope_directory_filename)
        self.envelope_back_face =find_envelope_back_face(self.envelope,self.plasma)
        self.envelope_front_face =find_envelope_front_face(self.envelope,self.envelope_back_face)
        self.front_face_midpoint = self.Find_front_face_midpoint(self.envelope_front_face)

        self.front_face_polodial_edges_to_fillet =self.Find_front_face_polodial_edges_to_fillet()
        self.front_face_torodial_edges_to_fillet =self.Find_front_face_torodial_edges_to_fillet()




        if self.blanket_type=='HCPB':
            self.first_wall_poloidal_fillet_radius = blanket_parameters_dict['first_wall_poloidal_fillet_radius']

            self.filleted_envelope = self.Filleted_envelope(self.first_wall_poloidal_fillet_radius,self.front_face_polodial_edges_to_fillet)

            self.filleted_envelope_back_face = find_envelope_back_face(self.filleted_envelope, self.plasma)
            self.filleted_envelope_front_face = find_envelope_front_face(self.filleted_envelope,
                                                                         self.filleted_envelope_back_face)
            self.filleted_envelope_front_face_id = self.Envelope_front_face_id(self.filleted_envelope)

            self.end_cap_faces = self.Find_end_cap_faces()

            self.first_wall_armour, self.envelope_removed_armour = self.Chop_off_first_wall_armour()

            self.armour_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_armour, self.plasma)
            self.armour_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_armour,
                                                                               self.armour_removed_envelope_back_face)

            self.first_wall, self.first_wall_removed_envelope = self.Chop_off_first_wall()
            self.first_wall_removed_envelope_back_face = find_envelope_back_face(self.first_wall_removed_envelope,
                                                                                 self.plasma)
            self.first_wall_removed_envelope_front_face = find_envelope_front_face(self.first_wall_removed_envelope,
                                                                                   self.first_wall_removed_envelope_back_face)
            self.first_wall_removed_envelope_midpoint = self.Find_front_face_midpoint(
                self.first_wall_removed_envelope_front_face)

            self.end_caps, self.envelope_removed_endcaps = self.Chop_of_end_caps()
            self.back_face_envelope_removed_caps = find_envelope_back_face(self.envelope_removed_endcaps, self.plasma)

            self.back_walls, self.envelope_removed_back_wall = self.Chop_off_back_walls()

            self.poloidal_segmentations = blanket_parameters_dict['poloidal_segmentations']
            self.envelope_poloidally_segmented = self.Chop_up_envelope_zone_poloidally()

            self.neutron_multiplier = self.envelope_poloidally_segmented[0]
            self.cooling_plate = self.envelope_poloidally_segmented[1] + self.envelope_poloidally_segmented[3]
            self.breeder_material = self.envelope_poloidally_segmented[2]

        if self.blanket_type=='HCLL':
            self.first_wall_poloidal_fillet_radius = blanket_parameters_dict['first_wall_poloidal_fillet_radius']

            self.filleted_envelope = self.Filleted_envelope(self.first_wall_poloidal_fillet_radius,self.front_face_polodial_edges_to_fillet)

            self.filleted_envelope_back_face = find_envelope_back_face(self.filleted_envelope, self.plasma)
            self.filleted_envelope_front_face = find_envelope_front_face(self.filleted_envelope,
                                                                         self.filleted_envelope_back_face)
            self.filleted_envelope_front_face_id = self.Envelope_front_face_id(self.filleted_envelope)

            self.end_cap_faces = self.Find_end_cap_faces()

            self.first_wall_armour, self.envelope_removed_armour = self.Chop_off_first_wall_armour()

            self.armour_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_armour, self.plasma)
            self.armour_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_armour,
                                                                               self.armour_removed_envelope_back_face)

            self.first_wall, self.first_wall_removed_envelope = self.Chop_off_first_wall()
            self.first_wall_removed_envelope_back_face = find_envelope_back_face(self.first_wall_removed_envelope,
                                                                                 self.plasma)
            self.first_wall_removed_envelope_front_face = find_envelope_front_face(self.first_wall_removed_envelope,
                                                                                   self.first_wall_removed_envelope_back_face)
            self.first_wall_removed_envelope_midpoint = self.Find_front_face_midpoint(
                self.first_wall_removed_envelope_front_face)

            self.end_caps, self.envelope_removed_endcaps = self.Chop_of_end_caps()
            self.back_face_envelope_removed_caps = find_envelope_back_face(self.envelope_removed_endcaps, self.plasma)

            self.back_walls, self.envelope_removed_back_wall = self.Chop_off_back_walls()

            self.poloidal_segmentations = blanket_parameters_dict['poloidal_segmentations']
            self.envelope_poloidally_segmented = self.Chop_up_envelope_zone_poloidally()

            self.lithium_lead = self.envelope_poloidally_segmented[0]
            self.cooling_plate = self.envelope_poloidally_segmented[1]

        if self.blanket_type=='WCLL':
            self.first_wall_poloidal_fillet_radius = blanket_parameters_dict['first_wall_poloidal_fillet_radius']

            self.filleted_envelope = self.Filleted_envelope(self.first_wall_poloidal_fillet_radius,self.front_face_polodial_edges_to_fillet)

            self.filleted_envelope_back_face = find_envelope_back_face(self.filleted_envelope, self.plasma)
            self.filleted_envelope_front_face = find_envelope_front_face(self.filleted_envelope,
                                                                         self.filleted_envelope_back_face)
            self.filleted_envelope_front_face_id = self.Envelope_front_face_id(self.filleted_envelope)

            self.end_cap_faces = self.Find_end_cap_faces()

            self.first_wall_armour, self.envelope_removed_armour = self.Chop_off_first_wall_armour()

            self.armour_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_armour, self.plasma)
            self.armour_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_armour,
                                                                               self.armour_removed_envelope_back_face)

            self.first_wall, self.first_wall_removed_envelope = self.Chop_off_first_wall()
            self.first_wall_removed_envelope_back_face = find_envelope_back_face(self.first_wall_removed_envelope,
                                                                                 self.plasma)
            self.first_wall_removed_envelope_front_face = find_envelope_front_face(self.first_wall_removed_envelope,
                                                                                   self.first_wall_removed_envelope_back_face)
            self.first_wall_removed_envelope_midpoint = self.Find_front_face_midpoint(
                self.first_wall_removed_envelope_front_face)

            self.end_caps, self.envelope_removed_endcaps = self.Chop_of_end_caps()
            self.back_face_envelope_removed_caps = find_envelope_back_face(self.envelope_removed_endcaps, self.plasma)

            self.back_walls, self.envelope_removed_back_wall = self.Chop_off_back_walls()

            self.poloidal_segmentations = blanket_parameters_dict['poloidal_segmentations']
            self.envelope_poloidally_segmented = self.Chop_up_envelope_zone_poloidally()

            self.toroidal_segmentations = blanket_parameters_dict['toroidal_segmentations']
            self.envelope_toroidally_segmented = self.Chop_up_breeder_zone_toroidally()

            self.radial_segmentations = blanket_parameters_dict['radial_segmentations']
            self.envelope_radially_segmented = self.Chop_up_envelope_zone_radially(number_required=1)

            list_of_plates_for_cutting = self.envelope_poloidally_segmented[0][2::4] + self.envelope_poloidally_segmented[0][3::4]
            self.additional_lithium_lead, self.reduced_solids = self.Find_common_bodies(self.envelope_radially_segmented[0],list_of_plates_for_cutting)

            self.envelope_poloidally_segmented[0] =  self.reduced_solids+ self.envelope_poloidally_segmented[0][0::4] + self.envelope_poloidally_segmented[0][1::4]
            self.envelope_poloidally_segmented[1] =  self.additional_lithium_lead + self.envelope_poloidally_segmented[1]

            self.lithium_lead =  []
            for poloidally_ll in self.envelope_poloidally_segmented[1]:
                for toroidally_ll in self.envelope_toroidally_segmented[0]:
                    self.lithium_lead.append(poloidally_ll.common(toroidally_ll))

            self.structural_plate = []
            for poloidally_div in self.envelope_poloidally_segmented[0]:
                for toroidal_div in self.envelope_toroidally_segmented[1]:
                    poloidally_div = poloidally_div.cut(toroidal_div)
                self.structural_plate.append(poloidally_div)
            self.structural_plate=self.structural_plate+self.envelope_toroidally_segmented[1]

        if self.blanket_type =='DCLL':

            self.first_wall_toroidal_fillet_radius = blanket_parameters_dict['first_wall_toroidal_fillet_radius']
            self.filleted_envelope = self.Filleted_envelope(self.first_wall_toroidal_fillet_radius,self.front_face_torodial_edges_to_fillet)

            self.filleted_envelope_back_face = find_envelope_back_face(self.filleted_envelope, self.plasma)
            self.filleted_envelope_front_face = find_envelope_front_face(self.filleted_envelope,
                                                                         self.filleted_envelope_back_face)
            self.filleted_envelope_front_face_id = self.Envelope_front_face_id(self.filleted_envelope)

            self.end_cap_faces = self.Find_end_cap_faces()

            self.first_wall_armour, self.envelope_removed_armour = self.Chop_off_first_wall_armour()

            self.armour_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_armour, self.plasma)
            self.armour_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_armour,
                                                                               self.armour_removed_envelope_back_face)

            self.first_wall, self.first_wall_removed_envelope = self.Chop_off_first_wall()
            self.first_wall_removed_envelope_back_face = find_envelope_back_face(self.first_wall_removed_envelope,
                                                                                 self.plasma)
            self.first_wall_removed_envelope_front_face = find_envelope_front_face(self.first_wall_removed_envelope,
                                                                                   self.first_wall_removed_envelope_back_face)
            self.first_wall_removed_envelope_midpoint = self.Find_front_face_midpoint(
                self.first_wall_removed_envelope_front_face)

            self.end_caps, self.envelope_removed_endcaps = self.Chop_of_end_caps()
            self.back_face_envelope_removed_caps = find_envelope_back_face(self.envelope_removed_endcaps, self.plasma)

            self.back_walls, self.envelope_removed_back_wall = self.Chop_off_back_walls()

            self.toroidal_segmentations = blanket_parameters_dict['toroidal_segmentations']
            self.envelope_toroidally_segmented = self.Chop_up_breeder_zone_toroidally()

            self.back_walls_removed_envelope_back_face = find_envelope_back_face(self.envelope_removed_back_wall, self.plasma)
            self.back_walls_removed_envelope_front_face = find_envelope_front_face(self.envelope_removed_back_wall, self.back_walls_removed_envelope_back_face)

            self.back_wall_removed_envelope_radial_depth = self.back_walls_removed_envelope_back_face.distToShape(self.back_walls_removed_envelope_front_face)[0]

            self.radial_segmentations = blanket_parameters_dict['radial_segmentations']
            self.envelope_radially_segmented = self.Chop_up_envelope_zone_radially_with_adjustable_rear_division(thinnest_two_layer_blanket=1500)

            self.top_and_bottom_faces_of_original_envelope = self.Find_poloidal_upper_and_lower_faces()

            self.poloidal_upper_offset_for_breeder_channel = blanket_parameters_dict['poloidal_upper_offset_for_breeder_channel']
            self.poloidal_lower_offset_for_breeder_channel = blanket_parameters_dict['poloidal_lower_offset_for_breeder_channel']
            self.breeder_zone_lithium_cutter_upper = exstrude_and_cut_solids(list_of_distances=[self.armour_thickness+self.first_wall_thickness+self.poloidal_upper_offset_for_breeder_channel],face=self.top_and_bottom_faces_of_original_envelope[0],envelope=self.envelope_removed_back_wall)

            self.poloidal_lower_offset_for_breeder_channel = blanket_parameters_dict['poloidal_lower_offset_for_breeder_channel']
            self.breeder_zone_lithium_cutter_lower = exstrude_and_cut_solids(list_of_distances=[self.armour_thickness+self.first_wall_thickness+self.poloidal_lower_offset_for_breeder_channel],face=self.top_and_bottom_faces_of_original_envelope[1],envelope=self.envelope_removed_back_wall)


            self.poloidal_upper_offset_for_plate = blanket_parameters_dict['radial_segmentations'][1]
            self.upper_plate = exstrude_and_cut_solids(list_of_distances=[self.armour_thickness + self.first_wall_thickness + self.poloidal_upper_offset_for_plate + self.poloidal_upper_offset_for_breeder_channel],face= self.top_and_bottom_faces_of_original_envelope[0],envelope=self.envelope_removed_back_wall)[0]
            self.upper_plate = self.upper_plate.cut(self.breeder_zone_lithium_cutter_upper)
            self.upper_plate = self.upper_plate.cut(self.envelope_radially_segmented[0][0])


            self.additional_lithium_lead_upper,self.reduced_solids_upper = self.Find_common_bodies(self.breeder_zone_lithium_cutter_upper,self.envelope_radially_segmented[1])
            self.additional_lithium_lead_lower,self.reduced_solids_lower = self.Find_common_bodies(self.breeder_zone_lithium_cutter_lower,self.envelope_radially_segmented[1])


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


        self.cylinder_slice = self.make_cylinder_slice(10)

        self.Save_file_as_step(os.path.splitext(os.path.basename(blanket_parameters_dict['envelope_filename']))[0])

    def make_cylinder_slice(self,angle=10):
        radius = 20000
        height = 15000

        cylinder_slice = Part.makeCylinder(radius, height, Base.Vector(0.00, 0.00, -0.5 * height), Base.Vector(0.00, 0.00, 1),angle)
        cylinder_slice = Part.makeCompound([cylinder_slice])
        # cylinder_slice.exportStep(output_folder_stp+"cylinder_slice.stp")
        return cylinder_slice

    def Save_file_as_step(self,module_filename):


        if self.blanket_type=='HCPB':
            filenames=["backwalls.step","firstwall.step","armour.step","end_caps.step","breeder_material.step","cooling_plate.step","neutron_multiplier.step"]
            filenames = [self.blanket_type +'_'+ module_filename+'_' + s for s in filenames]
            geometry_parts = [self.back_walls, self.first_wall, self.first_wall_armour, self.end_caps,self.breeder_material, self.cooling_plate, self.neutron_multiplier]

        if self.blanket_type == 'HCLL':
            filenames = ["backwalls.step", "firstwall.step", "armour.step", "end_caps.step", "lithium_lead.step", "cooling_plate.step"]
            filenames = [self.blanket_type +'_'+ module_filename+'_' + s for s in filenames]
            geometry_parts = [self.back_walls, self.first_wall, self.first_wall_armour, self.end_caps, self.lithium_lead, self.cooling_plate]

        if self.blanket_type == 'WCLL':
            filenames = ["backwalls.step", "firstwall.step", "armour.step", "end_caps.step", "lithium_lead.step","structural_plate.step"]
            filenames = [self.blanket_type +'_'+ module_filename+'_' + s for s in filenames]
            geometry_parts = [self.back_walls, self.first_wall, self.first_wall_armour, self.end_caps, self.lithium_lead, self.structural_plate]

        if self.blanket_type == 'DCLL':
            filenames = ["backwalls.step", "firstwall.step", "armour.step", "end_caps.step", "lithium_lead.step","structural_plate.step"]
            filenames = [self.blanket_type +'_' +module_filename+'_' + s for s in filenames]
            geometry_parts = [self.back_walls, self.first_wall, self.first_wall_armour, self.end_caps,self.lithium_lead, self.structural_plate]

        for item, filename in zip(geometry_parts,filenames):

            if type(item)==list:
                whole_compound=Part.makeCompound(item)
            else:
                whole_compound=Part.makeCompound([item])

            cylinder_sliced_whole_compound = whole_compound.common(self.cylinder_slice)
            cylinder_sliced_whole_compound.exportStep(os.path.join(self.output_folder, filename))


    def Find_common_bodies(self,chopper,chopped):
        common_parts=[]
        un_common_parts=[]

        #Part.makeCompound(chopped).exportStep(os.path.join(settings.output_folder, "chopped.step"))
        #Part.makeCompound(chopper).exportStep(os.path.join(settings.output_folder, "chopper.step"))

        for solid in chopped:
            common_material = solid.common(chopper)
            common_parts.append(common_material)
            un_common_parts.append(solid.cut(chopper))



        return common_parts,un_common_parts

    def Chop_off_first_wall(self):
        faces_not_in_first_wall= [self.filleted_envelope_back_face]  +self.end_cap_faces

        first_wall = self.filleted_envelope.makeThickness(faces_not_in_first_wall, -1*self.first_wall_thickness, 0)
        smaller_filleted_envelope = self.filleted_envelope.cut(first_wall)


        return first_wall, smaller_filleted_envelope

    def Chop_off_first_wall_armour(self):
        faces_not_in_first_wall= [self.filleted_envelope_back_face]  +self.end_cap_faces

        armour_every_where = self.filleted_envelope.makeThickness(faces_not_in_first_wall, -1*self.armour_thickness, 0)
        smaller_filleted_envelope = self.filleted_envelope.cut(armour_every_where)

        front_face = self.envelope_front_face
        front_face.scale(2.0, front_face.CenterOfMass)
        #big_front_face = front_face#.scale(2.0,front_face.CenterOfMass)
        body1 = front_face.extrude(self.envelope_front_face.normalAt(0, 0) * 50.0)
        body2 = front_face.extrude(self.envelope_front_face.normalAt(0, 0) * -50.0)
        body3 = body2.fuse(body1)

        armour = armour_every_where.common(body3)

        return armour, smaller_filleted_envelope

    def Envelope_front_face_id(self,wedge):
        print('Finding front face for this wedge ' ,self.envelope_directory_filename)
        largest_distance = 0
        for counter, face in enumerate(wedge.Faces):
            distance = face.distToShape(self.envelope_back_face)[0]
            if distance > largest_distance:
                largest_distance = distance
                furthest_face = face
                furthest_face_id = counter
        if not furthest_face:
            print('Front face of ' ,self.envelope_directory_filename,' not found')
            return None
        return furthest_face_id

    def Find_front_face_polodial_edges_to_fillet(self):
        list_of_edges_to_fillet = []
        list_of_edge_to_fillet_ids = []

        for counter, edge in enumerate(self.envelope_front_face.Edges):
            #print('        z_diff=', round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z))
            if round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z) != 0:
                list_of_edges_to_fillet.append(edge)
                list_of_edge_to_fillet_ids.append(counter)

        return list_of_edges_to_fillet

    def Find_front_face_torodial_edges_to_fillet(self):
        list_of_edges_to_fillet = []
        list_of_edge_to_fillet_ids = []

        for counter, edge in enumerate(self.envelope_front_face.Edges):
            #print('        z_diff=', round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z))
            if round(edge.Vertexes[0].Point.z - edge.Vertexes[1].Point.z) == 0:
                list_of_edges_to_fillet.append(edge)
                list_of_edge_to_fillet_ids.append(counter)

        return list_of_edges_to_fillet

    def Find_poloidal_upper_and_lower_faces(self):
        # this is not a very robust method of finding top bottom faces
        # todo improve this method
        list_of_edges_to_fillet = []
        list_of_edge_to_fillet_ids = []
        list_of_edge_to_fillet_lengths=[]


        front_face = self.envelope_front_face
        back_face = self.envelope_back_face
        envelope = self.envelope

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

        top_bottom_faces=[]
        for face in envelope.Faces:
            if face.Area !=back_face.Area:
                for edge in face.Edges:

                    #if edge in list_of_edges_to_fillet:
                    if edge.Length in list_of_edge_to_fillet_lengths:#.append(edge.Length):
                        print('found edge with correct length', edge.Length)
                        if face not in top_bottom_faces :
                            top_bottom_faces.append(face)
        if len(top_bottom_faces)==2:

            return top_bottom_faces
        else:
            print('method failed, to many or few faces found')

    def Filleted_envelope(self,fillet_radius,edges):

        wedge_filleted = self.envelope.makeFillet(fillet_radius,edges)
        return wedge_filleted


    def Find_end_cap_faces(self):
        list_of_top_bottom_faces = []
        list_of_top_bottom_face_ids = []



        for counter, face in enumerate(self.filleted_envelope.Faces):
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

    def Chop_of_end_caps(self):

        end_cap_1 = self.end_cap_faces[0]
        end_cap_1.scale(2.0,self.end_cap_faces[0].CenterOfMass)
        end_cap_2 = self.end_cap_faces[1]
        end_cap_2.scale(2.0,self.end_cap_faces[1].CenterOfMass)

        large_end_cap_1 = end_cap_1.extrude(end_cap_1.normalAt(0, 0) * -self.end_cap_thickness)
        large_end_cap_2 = end_cap_2.extrude(end_cap_2.normalAt(0, 0) * -self.end_cap_thickness)

        common_end_cap_1 = large_end_cap_1.common(self.first_wall_removed_envelope)
        common_end_cap_2 = large_end_cap_2.common(self.first_wall_removed_envelope)

        envelope_end_caps_removed = self.first_wall_removed_envelope.cut(Part.makeCompound([common_end_cap_1,common_end_cap_2]))

        return  [common_end_cap_1,common_end_cap_2],envelope_end_caps_removed

    def Chop_off_back_walls(self):

        back_face = self.back_face_envelope_removed_caps
        back_face.scale(2.0, back_face.CenterOfMass)

        remaining_shapes=self.envelope_removed_endcaps

        list_of_back_walls=[]
        cumlative_counter = 0
        print('self.back_walls_thicknesses',self.back_walls_thicknesses)

        for distance in self.back_walls_thicknesses:
            #print('back face distance = ',distance)

            #start_length = cumlative_counter
            cumlative_counter = cumlative_counter + distance
            stop_length = cumlative_counter

            back_face_exstruded = back_face.extrude(back_face.normalAt(0, 0) * -1*stop_length)

            list_of_back_walls.append(back_face_exstruded.common(remaining_shapes))

            remaining_shapes=remaining_shapes.cut(back_face_exstruded)

        return list_of_back_walls ,remaining_shapes # self.envelope_removed_endcaps.cut(Part.makeCompound(list_of_back_walls))

    def Find_front_face_midpoint(self,front_face):
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

        # first_wall_height = distance_between_two_points(lower_points_mid_x, lower_points_mid_y, lower_points_mid_z,upper_points_mid_x, upper_points_mid_y, upper_points_mid_z)
        #
        #
        # print('first_wall_height', first_wall_height)

        return midpoint

    def Chop_up_envelope_zone_poloidally(self):#settings,list_of_remaining_shapes, list_of_front_faces,stp, stl):

        if self.poloidal_segmentations ==[]:
            return self.envelope_removed_back_wall
        else:

            #midpoint = self.Find_front_face_midpoint(self.first_wall_removed_envelope_front_face)
            midpoint = self.first_wall_removed_envelope_midpoint

            top_bottom_edges= self.front_face_torodial_edges_to_fillet

            longest = 0
            for edge in self.envelope_removed_back_wall.Edges:
                if edge.Length > longest:
                    longest = edge.Length
                    longest_edge = edge
            print('longest length is ', longest_edge.Length)

            number_of_steps = int(math.ceil(  len(self.poloidal_segmentations)*((longest_edge.Length*1.15)/ sum(self.poloidal_segmentations)  )))

            cumlative_extrusion_lengths1 = convert_distances_into_cumlative_distances(distances =self.poloidal_segmentations, number_of_distances=number_of_steps, half_first_layer=True)

            cumlative_extrusion_lengths2 = [i * -1 for i in cumlative_extrusion_lengths1]

            point1 = FreeCAD.Vector(midpoint + (2000 * self.envelope_front_face.normalAt(0, 0)))
            point2 = FreeCAD.Vector(midpoint - (2000 * top_bottom_edges[1].tangentAt(0)))
            point3 = FreeCAD.Vector(midpoint - (2000 * self.envelope_front_face.normalAt(0, 0)))
            point4 = FreeCAD.Vector(midpoint + (2000 * top_bottom_edges[1].tangentAt(0)))

            poly = Part.makePolygon([point1, point2, point3, point4, point1])
            poly_face = Part.Face(poly)

            if self.blanket_type =='HCPB':
                print('Assuming the HCPB selected, treading the triangular corners differently')

                slices_of_blanket1=exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_extrusion_lengths1,face=poly_face,envelope=self.envelope_removed_back_wall,backtrack_id=4,offset=0)
                slices_of_blanket2=exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_extrusion_lengths2, face=poly_face,envelope=self.envelope_removed_back_wall,backtrack_id=4,offset=0)

            if self.blanket_type == 'WCLL':
                print('Assuming the WCLL selected, treading the triangular corners differently')

                slices_of_blanket1 = exstrude_and_cut_solids_up_to_change_in_shape_WCLL(list_of_distances=cumlative_extrusion_lengths1, face=poly_face,envelope=self.envelope_removed_back_wall,backtrack_id=4,offset=1)
                slices_of_blanket2 = exstrude_and_cut_solids_up_to_change_in_shape_WCLL(list_of_distances=cumlative_extrusion_lengths2, face=poly_face,envelope=self.envelope_removed_back_wall,backtrack_id=4,offset=1)

            else:

                slices_of_blanket1 = exstrude_and_cut_solids(cumlative_extrusion_lengths1, poly_face, self.envelope_removed_back_wall)
                slices_of_blanket2 = exstrude_and_cut_solids(cumlative_extrusion_lengths2, poly_face, self.envelope_removed_back_wall)

            collection_of_solids=[]
            for counter in range(0,len(self.poloidal_segmentations)):

                list_from_middle_out_1 = slices_of_blanket1[counter::len(self.poloidal_segmentations)]
                list_from_middle_out_2 = slices_of_blanket2[counter::len(self.poloidal_segmentations)]

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



            return collection_of_solids

    def Chop_up_breeder_zone_toroidally(self,number_required=1000): # settings,list_of_envelopes, list_of_front_faces,stp, stl):

        if self.toroidal_segmentations ==[]:
            return self.envelope_removed_back_wall
        else:
            midpoint = self.first_wall_removed_envelope_midpoint
            #midpoint,ff_height = find_midpoint_and_height_of_face(front_face)
            #print('midpoint',midpoint,'ff_height',ff_height )
            #top_bottom_edges = find_front_face_top_bottom_edges([front_face])
            top_bottom_edges = self.front_face_torodial_edges_to_fillet

            #print(top_bottom_edges[0].CenterOfMass)

            point1 = top_bottom_edges[0].CenterOfMass
            point2 = FreeCAD.Vector(point1 + self.first_wall_removed_envelope_front_face.normalAt(0, 0)*3000)
            point3 = top_bottom_edges[1].CenterOfMass
            point4 = FreeCAD.Vector(point3 + self.first_wall_removed_envelope_front_face.normalAt(0, 0)*3000)

            poly = Part.makePolygon([point1, point2, point4, point3, point1])
            poly_face = Part.Face(poly)

            poly_face.scale(2.0, poly_face.CenterOfMass)
            #poly_face.exportStep(os.path.join(settings.output_folder_stp, 'poly_face.step'))

            # max_distance=0
            # for face in self.envelope_removed_back_wall.Faces:
            #     dist = face.distToShape(self.first_wall_removed_envelope_front_face)[0]
            #     if dist> max_distance:
            #         max_distance=dist

            cumlative_distance_list_left  = convert_distances_into_cumlative_distances(distances=self.toroidal_segmentations,number_of_distances=number_required, half_first_layer=True)
            cumlative_distance_list_right  = [i * -1 for i in cumlative_distance_list_left]

            slices_of_blanket_left  = exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_distance_list_left ,face=poly_face, envelope=self.envelope_removed_back_wall,backtrack_id=2,offset=0)
            slices_of_blanket_right  = exstrude_and_cut_solids_up_to_change_in_shape(list_of_distances=cumlative_distance_list_right ,face=poly_face, envelope=self.envelope_removed_back_wall,backtrack_id=2,offset=0)

            toroidal_lithium_lead_left , toroidal_cooling_plates_left  = slices_of_blanket_left[::2] , slices_of_blanket_left[1::2]
            toroidal_lithium_lead_right, toroidal_cooling_plates_right = slices_of_blanket_right[::2], slices_of_blanket_right[1::2]

            toroidal_lithium_lead = toroidal_lithium_lead_left + toroidal_lithium_lead_right
            toroidal_cooling_plates = toroidal_cooling_plates_left +toroidal_cooling_plates_right

            #print(toroidal_cooling_plates)

            #Part.makeCompound(toroidal_lithium_lead).exportStep(os.path.join(settings.output_folder_stp, 'toroidal_lithium_lead.step'))
            #Part.makeCompound(toroidal_cooling_plates).exportStep(os.path.join(settings.output_folder_stp, 'toroidal_cooling_plates.step'))

            return [toroidal_lithium_lead,toroidal_cooling_plates]

    def Chop_up_envelope_zone_radially(self,number_required=1000):  # (settings, list_of_remaining_shapes, list_of_front_faces):

        if self.radial_segmentations == []:
            return self.envelope_removed_back_wall
        else:
            cumlative_distance_list = convert_distances_into_cumlative_distances(self.radial_segmentations,
                                                                                 number_required)
            slices_of_blanket = exstrude_and_cut_solids(cumlative_distance_list, self.first_wall_removed_envelope_front_face, self.envelope_removed_back_wall)

            #print('len(slices_of_blanket)', len(slices_of_blanket))
            #print('slices_of_blanket', slices_of_blanket)

            collection_of_solids = []
            for counter in range(0, len(self.radial_segmentations)):
                collection_of_solids.append(slices_of_blanket[counter::len(self.radial_segmentations)] + slices_of_blanket[counter::len(self.radial_segmentations)])
            return collection_of_solids

    def Chop_up_envelope_zone_radially_with_adjustable_rear_division(self,thinnest_two_layer_blanket):  # (settings, list_of_remaining_shapes, list_of_front_faces):

        if self.radial_segmentations == []:
            return self.envelope_removed_back_wall
        else:

            print('this blanket is ',self.back_wall_removed_envelope_radial_depth , 'mm')
            print('thinnest_two_layer_blanket is ',thinnest_two_layer_blanket , 'mm')
            if self.back_wall_removed_envelope_radial_depth > thinnest_two_layer_blanket:
                number_required=5 #maxvalue
            else:
                number_required=3

            cumlative_distance_list = convert_distances_into_cumlative_distances(self.radial_segmentations,number_required)
            #print('cumlative_distance_list',cumlative_distance_list)
            cumlative_distance_list[-1]= self.back_wall_removed_envelope_radial_depth*1.5

            if number_required==5:
                cumlative_distance_list[-2] = (cumlative_distance_list[1] + ((self.back_wall_removed_envelope_radial_depth  - cumlative_distance_list[1])/2)) - self.radial_segmentations[-1]
                cumlative_distance_list[-3] = cumlative_distance_list[-2] - self.radial_segmentations[-1]

                print('modified cumlative_distance_list', cumlative_distance_list)

            if number_required==3:
                print('not yet programmed')
                cumlative_distance_list=[]
                cumlative_distance_list.append( (self.back_wall_removed_envelope_radial_depth - self.radial_segmentations[1])/2.0)
                cumlative_distance_list.append( cumlative_distance_list[0] + self.radial_segmentations[1])
                cumlative_distance_list.append( self.back_wall_removed_envelope_radial_depth*1.5)




            slices_of_blanket = exstrude_and_cut_solids(cumlative_distance_list, self.first_wall_removed_envelope_front_face, self.envelope_removed_back_wall)

            #print('len(slices_of_blanket)', len(slices_of_blanket))
            #print('slices_of_blanket', slices_of_blanket)

            collection_of_solids = []
            for counter in range(0, len(self.radial_segmentations)):
                collection_of_solids.append(slices_of_blanket[counter::len(self.radial_segmentations)])# + slices_of_blanket[counter::len(self.radial_segmentations)])
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
        print(remaining_thick_face.Volume)
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


if __name__ == "__main__":
    print('this class is designed to be imported and called from an external file, see make_WCLL.py for an example')

