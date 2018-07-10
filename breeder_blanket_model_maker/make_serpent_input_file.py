import sys, re, os
from neutronics_material_maker import *
from collections import Counter
import collections
from collections import OrderedDict

def read_mccad_csg_mcnp_csg(list_of_detailed_modules_parts):
    
    print(list_of_detailed_modules_parts)
    for entry in list_of_detailed_modules_parts:
        if 'slice_envelope' in entry.keys():
            step_filename = entry['slice_envelope']['step_filename']
    
    print('step_filename',step_filename)
    #print(list_of_detailed_modules_parts['slice_envelope']['step_filename'])


    input_filename='D_'+os.path.basename(step_filename.split('.')[0]+'_MCNP.txt')
    input_dirname =os.path.dirname(step_filename)

    input_filename_and_path = os.path.join(input_dirname,input_filename)
    
    print('input_filename_and_path',input_filename_and_path)

    with open(input_filename_and_path) as f:
        contents = f.readlines()
    #print(contents)

        
    for i, line in enumerate(contents):
        if line.strip() == '':
            break
        if len(line)>0:
            if line[0].isdigit():
                #print('cell found')
                #print(line)
                cell_line = 'cell 10    0   fill all_um_geometry ' +' '.join(line.split()[2:])
    print('new cell_line',cell_line)
    
    
    surface_translate_dict= {'P':'plane','PY':'py','PZ':'pz','PX':'px'}
    
    new_surfaces =[]
    for line in contents[i+1:]:
        if line.strip() == '':
            break
        if len(line)>0:
            if line[0].isdigit():
                #print('surface found')
                #print(line)
                chop_up = line.split()
                new_surfaces.append('surf '+ ' '.join([chop_up[0],surface_translate_dict[chop_up[1]],' '.join(chop_up[2:]) ])+' % edge surface for blanket slice')
                
    return cell_line, new_surfaces

def return_serpent_file_head(include_um_mesh,list_of_detailed_modules_parts):
    lines_for_file=[]
    lines_for_file.append('% run this file using one of the following three commands')
    lines_for_file.append('%     sss2 filename -tracks 100 ')
    lines_for_file.append('%     sss2 filename -omp 2 ')
    lines_for_file.append('%     sss2 filename')
    lines_for_file.append('\n\n')

    lines_for_file.append('surf 20  sph 0 0 0 1000 % edge surface for the model \n\n')
    

    if include_um_mesh==True:
        cell_line, new_surfaces = read_mccad_csg_mcnp_csg(list_of_detailed_modules_parts)
        lines_for_file = lines_for_file + new_surfaces
        
        lines_for_file.append(cell_line)
        
        lines_for_file.append('cell 1000  0 fill sector -20  #10 % filled with solid 1 sector')

    else:
        lines_for_file.append('cell 1000  0 fill sector -20  % filled with solid 1 sector')
    #lines_for_file.append('cell 1999  0 outside 999')
    lines_for_file.append('cell 200  bg_for_um_and_stl void -20 % background cell for all universes')
    lines_for_file.append('cell 50  0 outside 20 % graveyard')# -998')  
    lines_for_file.append('\n\n')

    if include_um_mesh==True:

        lines_for_file.append('solid 1 all_um_geometry bg_for_um_and_stl')
        lines_for_file.append('1000 2 10 5   % search mesh parameters for octree')
        lines_for_file.append('scaled_points')
        lines_for_file.append('faces')
        lines_for_file.append('owner')
        lines_for_file.append('neighbour')
        lines_for_file.append('matfile_renamed')
        lines_for_file.append('\n\n')

    lines_for_file.append('\n\n% ------  stl cells in universe 1 ------\n% background is universe 2 which is just void')
    lines_for_file.append('solid 2  sector bg_for_um_and_stl   %solid 2 is stl.  <uni> <bg uni>')
    lines_for_file.append('100 3 10 5 5     %adaptive search mesh parameters')
    lines_for_file.append('%<max cells under mesh before split> <n levels> <size 1> < size 2> < size n>')
    lines_for_file.append('% here initial search mesh is 10x10x10, any mesh with > 5 cells under it is split into a 5x5x5 mesh.')
    lines_for_file.append('1 0.0000001   %1=fast, 2=safe tracking mode.  verticies snap tolerence.')
    lines_for_file.append('% these made no difference to error\n\n')

    return lines_for_file

def return_serpent_file_stl_parts(components,material_dictionary,output_folder_stl,output_folder):


    print(output_folder_stl)
    print(output_folder)
    print(os.path.commonprefix([output_folder_stl,output_folder]))

    relative_dir= output_folder_stl[len(os.path.commonprefix([output_folder_stl, output_folder])):].lstrip('/')

    print('relative director for stl files ' ,relative_dir)

    print('material_dictionary',material_dictionary)

    lines_for_file = []
    #number_of_stl_parts=0
    for component in components:
        # print(component)
        # if component['stl']==True:
        if component != 'slice_envelope' and component != 'slice_first_wall_homogenised':
            print('body ' + component + '-b ' + component + '-c ')
            lines_for_file.append('body ' + component + '-b ' + component + '-c ' + material_dictionary[component].material_card_name)
            for part in components[component]:
                stl_filepaths = part['stl_filename']
                for stl_filepath in stl_filepaths:
                    stl_filename = os.path.split(stl_filepath)[-1]
                    stl_filename_base = os.path.splitext(stl_filename)[0]
                    # print('stl_filepath',stl_filepath)
                    # print('stl_filename',stl_filename)
                    # print('stl_filename_base',stl_filename_base)


                    relative_filepath = os.path.join(relative_dir, stl_filename)
                    lines_for_file.append('    file ' + component + '-b "' + relative_filepath + '" 0.1 0 0 0  ')

                #number_of_stl_parts=number_of_stl_parts+1
            lines_for_file.append('\n\n')

    return lines_for_file#,number_of_stl_parts

def return_serpent_file_run_params(plot_serpent_geometry,tallies,nps):


    lines_for_file=[]
    lines_for_file.append('  ')
    lines_for_file.append('  ')
    lines_for_file.append('% ---- RUN ----')
    lines_for_file.append('set outp 1000')
    lines_for_file.append('set srcrate 1.0')
    lines_for_file.append('set acelib "/opt/serpent2/xsdir.serp"')

    lines_for_file.append('\n\n')

    lines_for_file.append("set gcu -1")
    # # lines_for_file += ["set opti 1"] # can be used to limit memory use

    lines_for_file.append("set lost 100")  # allows for 100 lost particles
    lines_for_file.append("set usym sector 3 2 0.0 0.0 0 10") #a 10 degree slice with boundary conditions

    for tally in tallies:
        particle_type= tally['particle_type']
        if particle_type =='p':
            print('Tally with photons found, including photons in the simulation')
            lines_for_file += ["set ngamma 2 %analog gamma"]
            lines_for_file += ['set pdatadir "/opt/serpent2/photon_data/"']
            lines_for_file += ['set ekn']
            break

    
    batch_size = min(0.5 * nps, 5000)
    # make batch size 1e4 regardless of nps
    batches = int(nps / batch_size)
    print('nps ', nps)
    print('batch_size ', batch_size)
    print('batches ', batches)

    lines_for_file.append('set nps ' + str(nps) + ' ' + str(batches) + ' % neutron population, bunch count')
    lines_for_file.append('set outp ' + str(batches + 1) + ' %only prints output after batchs +1, ie at the end')



    if plot_serpent_geometry == True:

        lines_for_file.append('plot 1 10000 10000 0.2  -2100 2100 -2100 2100')
        lines_for_file.append('plot 2 10000 10000 0.2  -2100 2100 -2100 2100 %plot py pixels pixels origin')
        lines_for_file.append('plot 3 10000 10000 0.2  -2100 2100 -2100 2100')
        
        lines_for_file.append('plot 1 16800 16800 -2  -2100 2100 -2100 2100')
        lines_for_file.append('plot 2 16800 16800 -2  -2100 2100 -2100 2100 %plot py pixels pixels origin')
        lines_for_file.append('plot 3 16800 16800 -2  -2100 2100 -2100 2100')
    lines_for_file.append('\n\n')

    return lines_for_file

def return_serpent_macroscopic_detectors(list_of_bodies_to_tally,mt_number,detector_name,particle_type):#,material_description=''):
  
    lines_list = []
    lines_list.append('\n')
    lines_list.append('% ------------ DETECTOR INPUT (macroscopic) ---------------')
    lines_list.append('det ' + detector_name + ' ' + particle_type)
    for body in list_of_bodies_to_tally:
        lines_list.append("\tdc " + body + "-c")
    lines_list.append('\tdr '+str(mt_number)+' void') # void can be replaced with the material_description but this is not needed
    lines_list.append('\n')
    return lines_list

def write_list_to_file(filename_and_path,list_of_lines):
    with open(filename_and_path, 'w') as serpent_input_file:
        for line in list_of_lines:
            serpent_input_file.write(line + '\n')
    print('file written to ',filename_and_path)

def return_serpent_file_material_cards(components,material_dictionary,output_folder):

    #relative_dir = os.path.basename(settings.output_folder_stl)

    lines_for_file = []
    materials_already_added=[]
    for component in components:
        if component != 'slice_envelope':  
            print(component)
            if material_dictionary[component].material_card_name not in materials_already_added:
                lines_for_file.append('\n\n')

                lines_for_file.append(material_dictionary[component].material_card(code='serpent'))
                materials_already_added.append(material_dictionary[component].material_card_name)
            else:
                print('material previous added')

    write_list_to_file(os.path.join(output_folder,'materials'),lines_for_file)
        

    return ['include "materials"','\n','\n'] #lines_for_file



def create_matfile_with_material_names(output_folder,material_dictionary):
    #read in the matfile line by line, looks up the step files in the material dictionary
    fname = os.path.join(output_folder,'matfile')
    with open(fname) as f:
        content = f.readlines()


    new_content=[content[0]]
    for i, line in enumerate(content[1:]):
        filename=os.path.basename(line)
        for material_name in material_dictionary.keys():
            if filename.startswith(material_name):
                new_content.append(material_dictionary[material_name].material_card_name+'\n')
#                print('found', filename, material_name,material_dictionary[material_name].material_card_name )
                break
    
    fname = os.path.join(output_folder,'matfile_renamed')
    file_contents = ''.join(new_content)
    with open(fname, 'w') as f:   
        f.write(file_contents)
        

def return_plasma_source(plasma_source_name='EU_baseline_2015') :

    if plasma_source_name == 'EU_baseline_2015':
        idum1 = "1 "
        idum2_number_of_cells_to_follow = "1 "
        idum3_valid_source_cells = "67 " #todo currently hard coded as 67
        rdum1_reactopm_selector = "2.0 " #DT, =1 for DD else is DT
        rdum2_t_in_kev = "10.5 " 
        rdum3_major_rad = "900 "
        rdum4_minor_rad = "225 "
        rdum5_elongation = "1.56 "
        rdum6_triangularity = "0.33 "

        rdum7_plasma_shift = "0.0 " 
        rdum8_plasma_peaking = "1.7 " 
        rdum9_plasma_vertical_shift = "0.0 " 
        rdum10_ang_start = "0 " #todo
        rdum11_ang_extent = "360.0 " #todo


        lines_for_file=[]
        lines_for_file.append('% --------------------- SOURCE SPECIFICATION ---------------------')
        lines_for_file.append('% MUIR GAUSSIAN FUSION ENERGY SPECTRUM IN USER DEFINED SUBROUTINE')
        lines_for_file.append('% PARAMETERS TO DESCRIBE THE PLASMA:')
        lines_for_file.append('src 1 si 16')
        lines_for_file.append('3 11')
        lines_for_file.append(idum1+' % IDUM(1) ')
        lines_for_file.append(idum2_number_of_cells_to_follow+' % IDUM(2) = number of valid cell numbers to follow')
        lines_for_file.append(idum3_valid_source_cells+' % IDUM(3) to IDUM(IDUM(2)+1) = valid source cells')
        lines_for_file.append(rdum1_reactopm_selector+' % RDUM(1) = Reaction selector 1=DD otherwise DT')
        lines_for_file.append(rdum2_t_in_kev+' % RDUM(2) = TEMPERATURE OF PLASMA IN KEV')
        lines_for_file.append(str(float(rdum3_major_rad))+' % RDUM(3) = RM  = MAJOR RADIUS')
        lines_for_file.append(str(float(rdum4_minor_rad))+' % RDUM(4) = AP  = MINOR RADIUS')
        lines_for_file.append(rdum5_elongation+' % RDUM(5) = E   = ELONGATION')
        lines_for_file.append(rdum6_triangularity+' % RDUM(6) = CP  = TRIANGUARITY')
        lines_for_file.append(rdum7_plasma_shift+' % RDUM(7) = ESH = PLASMA SHIFT')
        lines_for_file.append(rdum8_plasma_peaking+' % RDUM(8) = EPK = PLASMA PEAKING')
        lines_for_file.append(rdum9_plasma_vertical_shift+' % RDUM(9) = DELTAZ = PLASMA VERTICAL SHIFT (+=UP)')
        lines_for_file.append(rdum10_ang_start+' % RDUM(10) = Start of angular extent')
        lines_for_file.append(rdum11_ang_extent+'% RDUM(11) = Range of angular extent')
        lines_for_file.append('\n\n')

        return lines_for_file


# def find_components(list_of_detailed_modules_components):
#     print('parts = ',list_of_detailed_modules_components)
#     print(type)
#     dictionary_of_components=collections.defaultdict(list)
#     if type(list_of_detailed_modules_components) !='list':
#         list_of_detailed_modules_components=[list_of_detailed_modules_components]
#     for item in list_of_detailed_modules_components['parts']:
#         if type(item)==list:
#             for entry in item:
#                 for key,value in entry.iteritems():
#                     dictionary_of_components[key].append(value)
#         else:
#             for key,value in item.iteritems():
#                 dictionary_of_components[key].append(value)
#     return dictionary_of_components

# def find_components(list_of_detailed_modules_components):

#     dictionary_of_components=collections.defaultdict(list)
#     for item in list_of_detailed_modules_components:
#         #print(item)
#         for key,value in item.iteritems():
#             dictionary_of_components[key].append(value)

#     return dictionary_of_components

def find_components(list_of_detailed_modules_components):
    #print('parts = ',list_of_detailed_modules_components)
    #print(type)
    dictionary_of_components=collections.defaultdict(list)

    for list_entry in list_of_detailed_modules_components:
            for key,value in list_entry.iteritems():
                dictionary_of_components[key].append(value)

    return dictionary_of_components


def make_serpent_stl_based_input_file(neutronics_parameters_dictionary):

    components=find_components(neutronics_parameters_dictionary['parts'])
    
    if 'include_umesh' in neutronics_parameters_dictionary.keys():
        pass
    else:
        neutronics_parameters_dictionary['include_umesh']=False


    material_dictionary=neutronics_parameters_dictionary['material_dictionary']
    #material_description_for_tbr_tally=neutronics_parameters_dictionary['material_description_for_tbr_tally']

    #particle_type=neutronics_parameters_dictionary['particle_type']
        
    serpent_file = []

    serpent_file += return_serpent_file_head(neutronics_parameters_dictionary['include_umesh'],neutronics_parameters_dictionary['parts'])
    serpent_file += return_serpent_file_stl_parts(components,
                                                  material_dictionary,neutronics_parameters_dictionary['output_folder_stl'],
                                                  neutronics_parameters_dictionary['output_folder'])

    number_of_stl_parts=0
    for line in serpent_file:
        number_of_stl_parts=number_of_stl_parts+line.count('.stl')

    serpent_file += return_serpent_file_run_params(neutronics_parameters_dictionary['plot_serpent_geometry'],
                                                   neutronics_parameters_dictionary['tallies'],
                                                   neutronics_parameters_dictionary['nps'])

    serpent_file += return_serpent_file_material_cards(components, material_dictionary, neutronics_parameters_dictionary['output_folder'])


    if neutronics_parameters_dictionary['include_umesh'] == True:
        create_matfile_with_material_names(output_folder=neutronics_parameters_dictionary['output_folder'],material_dictionary=material_dictionary)
    
    serpent_file += return_plasma_source()

    for tally in neutronics_parameters_dictionary['tallies']:
        print(tally)
        serpent_file += return_serpent_macroscopic_detectors(list_of_bodies_to_tally=tally['bodies'],
                                                             mt_number=tally['mt_number'],
                                                             detector_name=tally['name'],
                                                             particle_type=tally['particle_type'],
                                                             #material_description=materials[0], void is used 
                                                             )

    if neutronics_parameters_dictionary['include_umesh'] == True:
        serpent_file +=['include "detector_n"']
        serpent_file +=['include "detector_p"']


    #
    # mesh = False
    # if mesh == True:
    #     serpent_file += return_serpent_file_mesh('li6_mt205')
    #     serpent_file += return_serpent_file_mesh('li7_mt205')
    #     serpent_file += return_serpent_file_mesh('neutron_multiplication')
    directory_path_to_serpent_output = os.path.join(neutronics_parameters_dictionary['output_folder'], 'serpent_input_file.serp')

    write_list_to_file(filename_and_path=directory_path_to_serpent_output,list_of_lines=serpent_file)

    return directory_path_to_serpent_output, number_of_stl_parts




if __name__ == "__main__":

    simulate_the_model_step_by_step()

