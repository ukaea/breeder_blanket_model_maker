

import multiprocessing
from breeder_blanket_model_maker.DCLL_CAD_procedure import *
from breeder_blanket_model_maker.HCLL_CAD_procedure import *
from breeder_blanket_model_maker.HCPB_CAD_procedure import *
from breeder_blanket_model_maker.WCLL_CAD_procedure import *

def detailed_module(dict_or_list_of_blanket_geometry_parameters):

    

    p = multiprocessing.Pool(multiprocessing.cpu_count()-1)

    if type(dict_or_list_of_blanket_geometry_parameters) == list:
      blanket_geometry_parameters_list=dict_or_list_of_blanket_geometry_parameters
    else:
      blanket_geometry_parameters_list=[dict_or_list_of_blanket_geometry_parameters]


    if type(dict_or_list_of_blanket_geometry_parameters) == dict:
      blanket_geometry_parameters_dict=dict_or_list_of_blanket_geometry_parameters
    else:
      blanket_geometry_parameters_dict=dict_or_list_of_blanket_geometry_parameters[0]


    try:
        os.makedirs(blanket_geometry_parameters_dict['output_folder'])
    except:
        pass

    print('Creating detailed '+blanket_geometry_parameters_dict['blanket_type'])

    #HCLL_detailed_module(blanket_geometry_parameters_dict)

    if blanket_geometry_parameters_dict['blanket_type'].upper() == 'HCLL'  :
 
       detailed_modules_parts = p.map(HCLL_detailed_module,blanket_geometry_parameters_list) 

    elif blanket_geometry_parameters_dict['blanket_type'].upper() == 'DCLL' :
       detailed_modules_parts = p.map(DCLL_detailed_module,blanket_geometry_parameters_list) 


    elif blanket_geometry_parameters_dict['blanket_type'].upper() == 'WCLL' :
       detailed_modules_parts = p.map(WCLL_detailed_module,blanket_geometry_parameters_list) 


    elif blanket_geometry_parameters_dict['blanket_type'].upper() == 'HCPB' :
       detailed_modules_parts = p.map(HCPB_detailed_module,blanket_geometry_parameters_list) 
             

    else:
        print('Blanket type ',blanket_geometry_parameters_dict['blanket_type'],' not supported yet.')

    return detailed_modules_parts