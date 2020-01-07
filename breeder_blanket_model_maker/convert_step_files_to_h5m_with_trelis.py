#!python

# to use this you must have trelis installed and the trelis command in your path
# also the dagmc plug in for trelis

import os
import sys
#os.environ["CUBIT_PLUGIN_DIR"] ='/opt/Trelis-16.4/bin/plugins/svalinn/'

print('example use')
#trelis -nographics -batch convert_step_files_to_h5m_with_trelis.py "inputs='m1.stp,m2.stp,m3.stp'" "materials='lithium,steel,copper'"  > output.txt

#trelis -nographics -batch geometry_utils/convert_step_files_to_h5m_with_trelis.py "inputs='m1.stp,m2.stp'"

#'cd /home/jshim/ukaea_git/breeder_blanket_model_maker_local'

#trelis -nographics -batch geometry_utils/convert_step_files_to_h5m_with_trelis.py "inputs='Eurofusion_baseline_2016/detailed_HCPB/step/first_wall_homogenised_mod10.step','Eurofusion_baseline_2016/detailed_HCPB/step/cooling_plate_2_mod6.step'"

# trelis geometry_utils/convert_step_files_to_h5m_with_trelis.py "inputs='Eurofusion_baseline_2016/detailed_HCPB/step/first_wall_homogenised_mod10.step,Eurofusion_baseline_2016/detailed_HCPB/step/cooling_plate_2_mod10.step'" "part='first_wall_homogenised,cooling_plate_2'"

# trelis convert_step_files_to_h5m_with_trelis.py "inputs='Eurofusion_baseline_2016/detailed_HCPB/step/back_helium_2_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/neutron_multiplier_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/cooling_plate_2_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/cooling_plate_1_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/breeder_material_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/armour_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/back_wall_3_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/end_caps_homogenised_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/back_helium_1_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/back_wall_2_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/first_wall_homogenised_mod1.step,Eurofusion_baseline_2016/detailed_HCPB/step/back_wall_1_mod1.step'" "parts='back_helium_2,neutron_multiplier,cooling_plate_2,cooling_plate_1,breeder_material,armour,back_wall_3,end_caps_homogenised,back_helium_1,back_wall_2,first_wall_homogenised,back_wall_1'"


aprepro_vars = cubit.get_aprepro_vars()

print("Found the following aprepro variables:")
print(aprepro_vars)
for var_name in aprepro_vars:
  val = cubit.get_aprepro_value_as_string(var_name)
  print("{0} = {1}".format(var_name, val))

if "inputs" in aprepro_vars:
  input_locations = cubit.get_aprepro_value_as_string("inputs").split(',')
  print('input geometry file ='+str(input_locations))   
  
if "parts" in aprepro_vars:
  parts = cubit.get_aprepro_value_as_string("parts").split(',')
  print('part identifiers ='+str(parts))

if "output_folder" in aprepro_vars:
  output_folder = cubit.get_aprepro_value_as_string("output_folder")
  print('output_folder ='+str(output_folder))   





def find_number_of_volumes_in_each_step_file(input_locations):
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




volumes_in_each_step_file = find_number_of_volumes_in_each_step_file(input_locations)

print('volumes_in_each_step_file',volumes_in_each_step_file)

cubit.cmd('scale vol all 0.1')
cubit.cmd('imprint body all')
cubit.cmd('merge tolerance 1.e-6')
cubit.cmd('merge all')


# this part makes watertight stl files
# this could also be done with moab from the h5m file
# opt/moab/bin/mbconvert filenamewithpath.h5m filenamewithpath.stl
# the stl's for each material can be output seperatly using the mbconvert -v flag
# moab offers more control over the STL files and their tolerance

for vols,part,step_filename in zip(volumes_in_each_step_file,parts,input_locations):
    print('vols',vols)
    print('part',part)
    cubit.cmd('group "mat:'+part+'" add vol '+' '.join(vols))

h5m_filename = os.path.join(output_folder,'detailed_blanket_model.h5m')
print('h5m_filename=',h5m_filename)
#export_statement = 'export dagmc "'+h5m_filename+'" faceting_tolerance 1.e-4'
#print('export_statement=',export_statement)
#cubit.cmd(export_statement)
cubit.cmd('export dagmc "'+h5m_filename+'" faceting_tolerance 1.e-4')
