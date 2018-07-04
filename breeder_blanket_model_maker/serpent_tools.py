import os
import multiprocessing
import sys
import math
import pprint

def find_tally_and_error(filepath):
    try :
        with open(filepath) as f:
            content=f.readlines()
    except :
        print("File", filepath , " was not found.")
        print("Was the serpent simulation run?")
        print("Has the _det0 file been output to the correct place?")

        sys.exit()
    
    tally_results_dict = {}
    for counter in range(0,len(content)):
        if content[counter].startswith('DET'):
            tally_values = []
            tally_error_values = []
            tally_name = content[counter][3:].split()[0]
            counter= counter+1
            while content[counter].startswith('];')==False:
                tally_values.append(float(content[counter].split()[-2]))
                tally_error_values.append(float(content[counter].split()[-1]))
                counter= counter+1  
            tally_total=0
            tally_error_total=0
            for i in range(len(tally_values)):
                tally_total += tally_values[i]
                tally_error_total += tally_error_values[i] ** 2
            tally_error_total = math.sqrt(tally_error_total)
            
            tally_results_dict[tally_name]={'tally_total':tally_total,'tally_error_total':tally_error_total}


    if 'photon_heating' in tally_results_dict.keys() and 'neutron_heating' in tally_results_dict.keys():

        tally_values = []
        tally_error_values = []
        for counter in range(0,len(content)):
            if content[counter].startswith('DETphoton_heating ') or content[counter].startswith('DETneutron_heating '):
                counter= counter+1
                while content[counter].startswith('];')==False:
                    tally_values.append(float(content[counter].split()[-2]))
                    tally_error_values.append(float(content[counter].split()[-1]))
                    counter= counter+1  

        tally_total=0
        tally_error_total=0
        for i in range(len(tally_values)):
            tally_total += tally_values[i]
            tally_error_total += tally_error_values[i] ** 2
        tally_error_total = math.sqrt(tally_error_total)

        total_heating =  tally_total
        total_heating_MeV =(6241506479963.2*total_heating)
        energy_amplification = total_heating_MeV/14.1

        tally_results_dict['energy_amplification']={'tally_total':energy_amplification,'tally_error_total':tally_error_total}
    
    pprint.pprint(tally_results_dict)
    return tally_results_dict


def run_serpent_locally(path_and_file):

    print(path_and_file)
    folder , file = os.path.split(path_and_file)


    os.system('cd '+folder)
    cwd = os.getcwd()
    os.chdir(folder)
    num_cpu = str(multiprocessing.cpu_count())
    os.system('rm serpent_input_file.serp_det0.m')
    os.system('rm serpent_input_file.serp_res.m')
    os.system('rm serpent_input_file.serp.seed')
    os.system('rm serpent_input_file.serp.out')
    os.system('sss2 '+file+' -omp '+num_cpu)

    os.system('cd ../..')
    os.chdir(cwd)

    tally_dict = find_tally_and_error(path_and_file+'_det0.m')

    return tally_dict

# tally_dict = find_tally_and_error('/home/jshim/detailed_HCPB/serpent_input_file.serp_det0.m')
# print(tally_dict['tbr'])
# tally_dict = find_tally_and_error('/home/jshim/detailed_HCLL/serpent_input_file.serp_det0.m')
# print(tally_dict['tbr'])
# tally_dict = find_tally_and_error('/home/jshim/detailed_DCLL/serpent_input_file.serp_det0.m')
# print(tally_dict['tbr'])
# tally_dict = find_tally_and_error('/home/jshim/detailed_WCLL/serpent_input_file.serp_det0.m')
# print(tally_dict['tbr'])

