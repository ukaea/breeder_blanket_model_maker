#!python


import os
import sys

print('example use')
#trelis -nographics -batch mesh_with_trelis_for_serpent.py "inputs='m1.stp,m2.stp,m3.stp'" "materials='lithium,steel,copper'"  > output.txt

#trelis mesh_with_trelis_for_serpent_2.py "output_dir='serpent_mesh/constant/polyMesh'" "element_type='hex'" "inputs='step/armour_sample_envelope_1.step,step/back_helium_sample_envelope_1.step,step/back_lithium_lead_sample_envelope_1.step,step/back_plate_1_sample_envelope_1.step,step/back_plate_2_sample_envelope_1.step,step/back_plate_3_sample_envelope_1.step,step/cooling_plate_homogenised_sample_envelope_1.step,step/end_caps_homogenised_sample_envelope_1.step,step/first_wall_homogenised_sample_envelope_1.step,step/lithium_lead_sample_envelope_1.step'" "materials='Tungsten,back_helium,Pb84.2Li15.8,Eurofer,Eurofer,Eurofer,Eurofer_vf_0.727_He_vf_0.273,Eurofer_vf_0.9_He_vf_0.1,Eurofer_vf_0.727_He_vf_0.273,Pb84.2Li15.8'" >output.txt
#trelis mesh_with_trelis_for_serpent_2.py "output_dir='serpent_mesh/constant/polyMesh'" "element_type='hex'" "inputs='step/armour_sample_envelope_1.step,step/back_helium_sample_envelope_1.step'" "materials='Tungsten,He'" >output.txt
#trelis mesh_with_trelis_for_serpent_2.py "output_dir='serpent_mesh/constant/polyMesh'" "element_type='tet'" "folder='step'" "materials='Tungsten,He,Pb84.2Li15.8,Eurofer,Eurofer,Eurofer,Eurofer_vf_0.727_He_vf_0.273,Eurofer_vf_0.9_He_vf_0.1,Eurofer_vf_0.727_He_vf_0.273,Pb84.2Li15.8'"  >output.txt
#trelis mesh_with_trelis_for_serpent_2.py "output_dir='serpent_mesh/constant/polyMesh'" "element_type='hex'" "folder='small_step'" "materials='Tungsten,He,Pb84.2Li15.8,Eurofer,Eurofer'"  >output.txt
#trelis mesh_with_trelis_for_serpent_2.py "output_dir='different_module'" "element_type='hex'" "folder='different_module/step'" "materials='Tungsten,He,Pb84.2Li15.8,Eurofer'"  >output.txt

#trelis mesh_with_trelis_for_serpent_2.py "output_dir='different_module'" "element_type='hex'" "folder='different_module/step'" "materials='Tungsten,He,Pb84.2Li15.8,Eurofer,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He,He'"  >output.txt

#trelis mesh_with_trelis_for_serpent_2.py "output_dir='slice'" "element_type='tet'" "folder='slice/step'" "materials='Tungsten,He,Pb84.2Li15.8,Eurofer,He,He,He,He,He,He,He'"  >output.txt
#trelis mesh_with_trelis_for_serpent_2.py "output_dir='slice_hybrid_model'" "element_type='tet'" "folder='slice_hybrid_model/step'" "ignore_files='slice_envelope_mod26.step,D_slice_envelope_mod26.step'" "materials='Tungsten,He,Pb84.2Li15.8,Eurofer,He,He,He,He,He,He,He'" 


#trelis -nographics -batch mesh_with_trelis_for_serpent_2.py   > output.txt



def find_number_of_volumes_in_each_step_file():
    body_ids=''
    cubit.cmd('reset')
    volumes_in_each_step_file=[]
    for i in range(0,len(input_locations)):
      current_vols =cubit.parse_cubit_list("volume", "all")
      print('input       ',    input_locations[i])
      if input_locations[i].endswith('.sat'):
        cubit.cmd('import acis "'+input_locations[i]+'" nofreesurfaces separate_bodies')
      if input_locations[i].endswith('.stp') or input_locations[i].endswith('.step'):
        cubit.cmd('import step "'+input_locations[i]+'" heal')
      if input_locations[i].endswith('.stl'):
        cubit.cmd('import stl "'+input_locations[i]+'" merge')
      #body_ids=body_ids+' '+str(i+1)
      all_vols =cubit.parse_cubit_list("volume", "all")
      new_vols = set(current_vols).symmetric_difference(set(all_vols))
      print('all_vols    ',str(all_vols))
      print('current_vols',str(current_vols))
      print('new_vols    ',str(new_vols))
      #volumes_in_each_step_file.append(new_vols)
      new_vols=map(str, new_vols)
      new_vols=' '.join(new_vols)
      volumes_in_each_step_file.append(new_vols.split())
    print('volumes_in_each_step_file')
    print(volumes_in_each_step_file)
    print('body_ids')
    print(body_ids)
    return volumes_in_each_step_file



aprepro_vars = cubit.get_aprepro_vars()
#
print("Found the following aprepro variables:")
for var_name in aprepro_vars:
  val = cubit.get_aprepro_value_as_string(var_name)
  print("{0} = {1}".format(var_name, val))
#

#
print(aprepro_vars)


ignore_files=[]
if "ignore_files" in aprepro_vars:
  ignore_files = cubit.get_aprepro_value_as_string("ignore_files").split(',')
  print('ignoring files ='+str(ignore_files))

if "inputs" in aprepro_vars:
  input_locations = cubit.get_aprepro_value_as_string("inputs").split(',')
  print('input geometry file ='+str(input_locations))

if "folder" in aprepro_vars:
  input_locations=[]
  input_folder = cubit.get_aprepro_value_as_string("folder")
  for file in os.listdir(input_folder):
    if file not in ignore_files and file.endswith('step') or file.endswith('stp'):
      input_locations.append(input_folder+'/'+file)
  print('input geometry files from folder ='+str(input_locations))

if "materials" in aprepro_vars:
  if cubit.get_aprepro_value_as_string("materials")=='infilename':
    materials_list=[]
    for file in input_locations:
      #materials_list.append(
      filepath_and_name = os.path.split(file)
      filename ,fileextention= os.path.splitext(filepath_and_name[-1])
      #filename = filename.split(os.path.sep)
      material = filename.split('_')[-1].split('(')[0]
      print('filename',filename,material)
      materials_list.append(material)
  else:
    materials_list = cubit.get_aprepro_value_as_string("materials").split(',')
  print('matieral name ='+str(materials_list))

prefix_string=''
if "prefix" in aprepro_vars:
  prefix_string = cubit.get_aprepro_value_as_string("prefix")
  print('prefix name ='+str(prefix_string))

element_type=''
if "element_type" in aprepro_vars:
  element_type = cubit.get_aprepro_value_as_string("element_type")
  print('element_type ='+str(element_type))

output_dir=''
if "output_dir" in aprepro_vars:
  output_dir = cubit.get_aprepro_value_as_string("output_dir")
  print('output_dir ='+str(output_dir))

for mat,inputfile in zip(materials_list,input_locations):
  print('material=',mat,' file=',inputfile)

if len(materials_list)!=len(input_locations):
  print('you have unequal amounts of materials and inputfiles \n len(materials_list)=',str(len(materials_list)),' len(input_locations)=',str(len(input_locations)-len(ignore_files)))
  input()
  sys.exit()




volumes_in_each_step_file = find_number_of_volumes_in_each_step_file()
print('volumes_in_each_step_file is',volumes_in_each_step_file)

#  
materials_made=[]
cubit.cmd('set duplicate block elements off')
for i in range(0,len(materials_list)):
  if materials_list[i] not in materials_made:
    #material_dictionary = find_material_properties(materials_list[i])
    #print('material_dictionary',material_dictionary)
    cubit.cmd('create material "'+materials_list[i]+'" property_group "CUBIT-ABAQUS" ')
    #cubit.cmd('modify material "'+materials_list[i]+'" scalar_properties "DENSITY" '+str(material_dictionary["density"][0]))
    #old code that used dictionaries    #cubit.cmd('modify material "'+materials_list[i]+'" scalar_properties "DENSITY" '+str(densities_dict[materials_list[i]])+' "SPECIFIC_HEAT" '+str(specificheat_dict[materials_list[i]])+' "CONDUCTIVITY" '+str(conductivities_dict[materials_list[i]])+' ')
    materials_made.append(materials_list[i])
    #print('modify material "'+materials_list[i]+'" scalar_properties "DENSITY" '+str(densities_dict[materials_list[i]])+' "SPECIFIC_HEAT" '+str(specificheat_dict[materials_list[i]])+' "CONDUCTIVITY" '+str(conductivities_dict[materials_list[i]])+' ')
for i1 in range(0,len(volumes_in_each_step_file)):
  cubit.cmd('create block '+str(i1+1))
  cubit.cmd('block '+str(i1+1)+' material "' +materials_list[i1]+'"')
  for i2 in range(0,len(volumes_in_each_step_file[i1])):
    cubit.cmd('block '+str(i1+1)+' add volume '+str(volumes_in_each_step_file[i1][i2]))


#if min_mesh_element_size!='auto':
#  cubit.cmd("volume all size "+str(min_mesh_element_size))
#  #cubit.cmd("volume 1 sizing function type skeleton min_size "+str(min_mesh_element_size)+" max_size auto max_gradient auto min_num_layers_3d 1 min_num_layers_2d 1 min_num_layers_1d 1 ")
print('element_type',element_type)

cubit.cmd('imprint body all')
cubit.cmd('merge tolerance 1.e-6')
cubit.cmd('merge all')

if element_type=='tet':
  cubit.cmd('volume all scheme tetmesh proximity layers off')
if element_type=='hex':
  cubit.cmd('volume all scheme auto')
  cubit.cmd("volume all sizing function type skeleton min_size auto max_size auto max_gradient 1.5 min_num_layers_3d 1 min_num_layers_2d 1 min_num_layers_1d 1 ")
  cubit.cmd("volume all scheme map")

cubit.cmd('mesh volume all')

#cubit.cmd('scale mesh vol all Multiplier 0.1')

materials_list_id=[]
materials_made=[]
material_counter=1
for material in materials_list:
  print('material',material)
  if material in materials_made:
    previous_material_id = materials_made.index(material)
    materials_list_id.append(materials_list_id[previous_material_id])
  else:
    materials_list_id.append(material_counter)
    materials_made.append(material)
    material_counter=material_counter+1

print('materials_list_id',materials_list_id)
print('materials_list',materials_list_id)

elements_in_each_volume=[]
for vols in volumes_in_each_step_file:
    print('volumes in this file ',vols)
    elements_in_volume = cubit.parse_cubit_list("element", " in volume " +' '.join(vols))
    print('elements_in_volume',elements_in_volume)
    #elements_in_volume = cubit.parse_cubit_list("element", " in volume 1")
    #print('elements_in_volume',elements_in_volume)
    elements_in_each_volume.append(elements_in_volume)
    print('elements_in_volume',' '.join(vols))


def rename_files_with_prefix(prefix):
  if prefix!='':
    os.rename('serpent_mesh/constant/polyMesh/matfile'   , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'matfile' ))
    os.rename('serpent_mesh/constant/polyMesh/boundary'  , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'boundary' ))
    os.rename('serpent_mesh/constant/polyMesh/faces'     , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'faces' ))
    os.rename('serpent_mesh/constant/polyMesh/neighbour' , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'neighbour' ))
    os.rename('serpent_mesh/constant/polyMesh/owner'     , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'owner' ))
    os.rename('serpent_mesh/constant/polyMesh/points'    , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'points' ))
    os.rename('serpent_mesh/constant/polyMesh/scaled_points'    , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'scaled_points' ))
    os.rename('serpent_mesh/constant/polyMesh/detector_p'    , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'detector_p' ))
    os.rename('serpent_mesh/constant/polyMesh/detector_n'    , os.path.join('serpent_mesh/constant/polyMesh/',prefix+'detector_n' ))
  else:
    print('no prefix given')

def move_um_mesh_files(output_dir):
  for file in ['matfile','boundary','faces','neighbour','owner','points','scaled_points','detector_p','detector_n']:
    print(os.path.join('serpent_mesh/constant/polyMesh/',file))
    os.rename(os.path.join('serpent_mesh/constant/polyMesh/',file),os.path.join( output_dir,file) )


def write_openfoam_material_card(elements_in_each_volume,materials_list_id):
  file_name_and_path ='serpent_mesh/constant/polyMesh/matfile'
  #outputfile = open(file_name_and_path, 'w')
  print('elements_in_each_volume',elements_in_each_volume)
  print('materials_list_id',materials_list_id)
  #file_name_and_path =os.path.sep.join['serpent_mesh','constant','polyMesh','matfile']
  print('file_name_and_path',file_name_and_path)
  outputfile = open(file_name_and_path, 'w')
  total_number_of_elements=0
  for volume , mat_id in zip(elements_in_each_volume,materials_list_id):
    total_number_of_elements = total_number_of_elements+ len(volume)
  outputfile.write(str(total_number_of_elements)+'\n')
  elements_and_materials = []
  elements_list=[]
  for volume , mat_id in zip(elements_in_each_volume,materials_list_id):
    for element in volume:
      elements_and_materials.append((element,mat_id))
      elements_list.append(element)
      #print(element,mat_id)
  print('elements_and_materials',elements_and_materials)
  sorted_materials_ids =[x for (y,x) in sorted(elements_and_materials)]
  sorted_elements = sorted(elements_list)
  #print('sorted_elements',sorted_elements)
  for i , each_volume in enumerate(elements_in_each_volume):
    for elements in each_volume:
      outputfile.write(materials_list[i]+'\n')  
  #for x in range(0,len(sorted_elements)):
    #print(sorted_elements[x],sorted_materials_ids[x])
  #  outputfile.write(str(sorted_materials_ids[x])+'\n')
  outputfile.close()




def write_serpent_detector():
  elements_in_all_volume = cubit.parse_cubit_list("element", "in volume all")
  print('elements_in_all_volume_serpe',elements_in_all_volume)
  file_name_and_path ='serpent_mesh/constant/polyMesh/detector_n'
  print('file_name_and_path',file_name_and_path)
  outputfile = open(file_name_and_path, 'w')
  outputfile.write('det umesh_det_n n \n')
  outputfile.write('    dumsh all_um_geometry \n')
  outputfile.write(str(len(elements_in_all_volume))+' \n')
  for element_counter in range(1,len(elements_in_all_volume)+1):
    outputfile.write(str(element_counter)+' ' +str(element_counter)+'\n')
  outputfile.close()  
  elements_in_all_volume = cubit.parse_cubit_list("element", "in volume all")
  print('elements_in_all_volume_serpe',elements_in_all_volume)
  file_name_and_path ='serpent_mesh/constant/polyMesh/detector_p'
  print('file_name_and_path',file_name_and_path)
  outputfile = open(file_name_and_path, 'w')
  outputfile.write('det umesh_det_p p \n')
  outputfile.write('    dumsh all_um_geometry \n')
  outputfile.write(str(len(elements_in_all_volume))+' \n')
  for element_counter in range(1,len(elements_in_all_volume)+1):
    outputfile.write(str(element_counter)+' ' +str(element_counter)+'\n')
  outputfile.close()  


def rewrite_serpent_points(scale):
    print('scaling points by ',scale)
    file_name_and_path ='serpent_mesh/constant/polyMesh/points'
    with open(file_name_and_path) as f:
        lines = f.read().splitlines()
    new_lines=[]
    for line in lines:
        if line.startswith('(') and line.endswith(')'):
            coords=[]
            for coord in line[1:-1].split():
                new_coord = float(coord)*scale
                coords.append(str(new_coord))
            line = '('+' '.join(coords)+')'
        new_lines.append(line)
    new_file_name_and_path ='serpent_mesh/constant/polyMesh/scaled_points' 
    with open(new_file_name_and_path,"w") as f2:
        for line in new_lines:
            f2.write(line+'\n')
    print(new_lines)
    



write_serpent_detector()


write_openfoam_material_card(elements_in_each_volume,materials_list_id)



cubit.cmd('export openfoam "serpent_mesh" overwrite')

rewrite_serpent_points(scale=0.001)

move_um_mesh_files(output_dir)
#rename_files_with_prefix(prefix_string)


#
#
os.system('rm cubit*.jou')
os.system('rm history*.jou')
os.system('rm step_import.log')
#