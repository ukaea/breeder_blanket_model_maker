import os
import multiprocessing
import sys
import math

def find_tbr_and_error(filepath):
    try :
        with open(filepath) as f:
            content=f.readlines()
    except :
        print "File", filepath , " was not found."
        print "Was the serpent simulation run?"
        print "Has the _det0 file been output to the correct place?"

        sys.exit()
        
    photon_heating, error_photon_heating=[],[]
    neutron_heating, error_neutron_heating=[],[]
    tbr_list, tbr_error_list = [], []

    for counter in range(0,len(content)):
        if content[counter].startswith('DETtbr'):
            counter= counter+1
            while content[counter].startswith('];')==False:
                tbr_list.append(float(content[counter].split()[-2]))
                tbr_error_list.append(float(content[counter].split()[-1]))
                counter= counter+1

        if content[counter].startswith('DETneutron_heating'):
            counter= counter+1
            while content[counter].startswith('];')==False:
                print(float(content[counter].split()[-2]))
                neutron_heating.append(float(content[counter].split()[-2]))
                error_neutron_heating.append(float(content[counter].split()[-1]))
                counter= counter+1   

        if content[counter].startswith('DETphoton_heating'):
            counter= counter+1
            while content[counter].startswith('];')==False:
                print(float(content[counter].split()[-2]))
                photon_heating.append(float(content[counter].split()[-2]))
                error_photon_heating.append(float(content[counter].split()[-1]))
                counter= counter+1   

    tbr_total, tbr_error_total = 0,0
    for i in range(len(tbr_list)):
        tbr_total += tbr_list[i]
        tbr_error_total += tbr_error_list[i] ** 2
    tbr_error_total = math.sqrt(tbr_error_total)

    error_total_heating=0
    photon_heating_total, error_photon_heating_total=0,0
    for i in range(len(photon_heating)):
        photon_heating_total += photon_heating[i]
        error_photon_heating_total += error_photon_heating[i] ** 2
        error_total_heating  += error_photon_heating[i] ** 2
    error_photon_heating_total = math.sqrt(error_photon_heating_total)

    neutron_heating_total, error_neutron_heating_total=0,0
    for i in range(len(neutron_heating)):
        neutron_heating_total += neutron_heating[i]
        error_neutron_heating_total += error_neutron_heating[i] ** 2
        error_total_heating  += error_neutron_heating[i] ** 2
    error_neutron_heating_total = math.sqrt(error_neutron_heating_total)

    total_heating = neutron_heating_total+photon_heating_total
    print('total_heating',total_heating)

    error_total_heating = math.sqrt(error_total_heating)
                            
    total_heating_MeV =(6241506479963.2*total_heating)
    energy_amplification = total_heating_MeV/14.1
    
    print("\nRESULT:")
    print("tbr =: ", tbr_total,' +/- ', tbr_error_total)
    print("energy amplification ",energy_amplification,' +/- ',error_total_heating)

    return {'tbr':tbr_total,'tbr_error':tbr_error_total}



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

    tally_dict = find_tbr_and_error(path_and_file+'_det0.m')

    return tally_dict