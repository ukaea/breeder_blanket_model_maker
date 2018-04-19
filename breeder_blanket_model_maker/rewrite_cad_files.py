#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 12:08:29 2017
@author: jshimwell
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo add-apt-repository ppa:freecad-maintainers/freecad-daily
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install freecad-daily
#sudo apt-get install freecad-daily-dev
#sudo apt-get install freecad
#sudo apt-get install freecad-dev
#sudo apt-get install freecad-daily-dev

"""


import sys

sys.path.append('/usr/lib/freecad-daily/lib/')
sys.path.append('/usr/lib/freecad/lib/')


import math
import FreeCAD
from FreeCAD import Base
import Part
import os
import Mesh
import Draft
import MeshPart
from common_CAD_functions import *
import collections
from collections import OrderedDict

#sys.path.append('/home/jshim/moab/lib/python2.7/site-packages/')

#from pymoab import core


def read_in_stl_files_and_save_as_h5m(read_file,write_file):

    mbi = core.Core()

    mbi.load_file(read_file)

    mbi.write_file(write_file)

def read_in_stl_files_and_resave(read_folder,write_folder):
    try:
        os.mkdir(write_folder)
    except:
        pass
    for file in os.listdir(read_folder):
        if file.endswith(".stl"):
            #print('reading in ' ,os.path.join(read_folder, file))
            
            # only for stp model =Part.Shape()
            # model.read(os.path.join("stl_files", file))
            
            #obj = Mesh.open(os.path.join(read_folder, file))
            obj = Mesh.Mesh(os.path.join(read_folder, file))
            #print('writing in ' ,os.path.join(read_folder, file))
            #Mesh.export(obj,os.path.join(write_folder,file))
            obj.write(os.path.join(write_folder,file))

def read_in_stl_files_and_resave_as_single_step(read_folder,write_folder):
    try:
        os.mkdir(write_folder)
    except:
        pass
    list_of_solid_parts=[]
    for file in os.listdir(read_folder):
        if file.endswith(".stl"):
            #print('reading in ' ,os.path.join(read_folder, file))
            
            # only for stp model =Part.Shape()
            # model.read(os.path.join("stl_files", file))
            
            #obj = Mesh.open(os.path.join(read_folder, file))
            obj = Mesh.Mesh(os.path.join(read_folder, file))
            #print('opening ' ,os.path.join(read_folder, file))
            #Mesh.export(obj,os.path.join(write_folder,file))
            
            shape = Part.Shape()
            shape.makeShapeFromMesh(obj.Topology,0.05)
            solid = Part.makeSolid(shape)
            list_of_solid_parts.append(solid)

    
    compound_obj=Part.makeCompound(list_of_solid_parts)
    compound_obj.exportStep(os.path.join(write_folder,file))
    
def read_in_step_file_and_save_as_seperate_step_files(file,write_folder=''):

    if file.endswith(".step") or  file.endswith(".stp"):
        print('reading in ' ,os.path.join(file))
        multipart_step = Part.read(os.path.join(file))
        file_counter=1
        for solid in multipart_step.Solids:
            print(write_folder+'/'+file+str(file_counter))
            solid.exportStep(os.path.join(write_folder,os.path.splitext(file)[0]+str(file_counter)+'.stp'))
            file_counter=file_counter+1  
                
def read_in_step_files_and_save_as_seperate_step_files(read_folder,write_folder):
    try:
        os.mkdir(write_folder)
    except:
        print('error making folder')

    if os.path.isfile(read_folder):
        file = read_folder
        if file.endswith(".step") or  file.endswith(".stp"):
                    print('reading in ' ,os.path.join(read_folder, file))
                    multipart_step = Part.read(file)
                    file_counter=1
                    for solid in multipart_step.Solids:
                        print(write_folder+'/'+file+str(file_counter))
                        solid.exportStep(write_folder+'/'+os.path.splitext(file)[0]+str(file_counter)+'.stp')
                        file_counter=file_counter+1    
        return True

    for file in os.listdir(read_folder):
        if file.endswith(".step") or  file.endswith(".stp"):
            print('reading in ' ,os.path.join(read_folder, file))
            multipart_step = Part.read(os.path.join(read_folder, file))
            file_counter=1
            for solid in multipart_step.Solids:
                print(write_folder+'/'+file+str(file_counter))
                solid.exportStep(write_folder+'/'+os.path.splitext(file)[0]+str(file_counter)+'.stp')
                file_counter=file_counter+1
    return True

def read_in_step_files_and_save_as_single_step(read_folder,write_folder,prefix_required):
    try:
        os.mkdir(write_folder)
    except:
        print('error making folder')
    list_of_all_solids=[]
    for file in os.listdir(read_folder):
        if file.endswith(".step") or  file.endswith(".stp") :
            if file.startswith(prefix_required):
                #print('reading in ' ,os.path.join(read_folder, file))
                multipart_step = Part.read(os.path.join(read_folder, file))

                if type(multipart_step.Solids)==list:
                    list_of_all_solids=list_of_all_solids+multipart_step.Solids
                else:
                    list_of_all_solids.append(multipart_step.Solids)

    Part.makeCompound(list_of_all_solids).exportStep(os.path.join(write_folder,'grouped_'+prefix_required+'.step'))

def read_in_step_files_and_save_as_seperate_stl_files(read_folder,write_folder,ignore_files=['']):


    try:
        os.mkdir(write_folder)
        print('making folder',write_folder)
    except:
        print('error making folder',write_folder)

    dictionary_of_parts = collections.defaultdict(dict)

    if type(read_folder)==str:
        print('read_folder',read_folder)
        print(os.listdir(read_folder))

        for file in os.listdir(read_folder):
            if file not in ignore_files:
                print(file)
                if file.endswith(".step") or  file.endswith(".stp"):
                    #print('reading in ' ,os.path.join(read_folder, file))
                    multipart_step = Part.read(os.path.join(read_folder, file))

                    filestub = os.path.splitext(file)[0]

                    dictionary_of_parts[filestub]['part'] = multipart_step
                    file_counter=1

                    stl_file_list=[]

                    for solid in multipart_step.Solids:
                        solid_mesh = MeshPart.meshFromShape(solid, LinearDeflection=0.1)
                        stl_filename= write_folder+'/'+os.path.splitext(file)[0]+'_'+str(file_counter)+'.stl'
                        #print(stl_filename)
                        solid_mesh.write(stl_filename)
                        file_counter=file_counter+1
                        stl_file_list.append(stl_filename)
                    if len(multipart_step.Solids)==0:
                        singlepart_step=multipart_step
                        solid_mesh = MeshPart.meshFromShape(singlepart_step, LinearDeflection=0.1)
                        stl_filename= write_folder+'/'+os.path.splitext(file)[0]+'_'+str(file_counter)+'.stl'
                        #print(stl_filename)
                        solid_mesh.write(stl_filename)
                        file_counter=file_counter+1
                        stl_file_list.append(stl_filename)

                    dictionary_of_parts[filestub]['stl_filename'] =stl_file_list
                    #if file =='plasma.stp':
                    #    print len(multipart_step.Solids)
                    #    input()
        return dictionary_of_parts
    if type(read_folder)==list:
        file_list=read_folder
        for file in file_list:
                    print('reading in ',file)
                    multipart_step = Part.read(os.path.join(read_folder, file))
                    file_counter=1
                    for solid in multipart_step.Solids:
                        solid_mesh = MeshPart.meshFromShape(solid, LinearDeflection=0.1)
                        stl_filename= os.path.join(write_folder,os.path.splitext(file)[0]+'_'+str(file_counter)+'.stl')
                        #print('writing ',stl_filename)
                        solid_mesh.write(stl_filename)
                        file_counter=file_counter+1
                    if len(multipart_step.Solids)==0:
                        singlepart_step=multipart_step
                        solid_mesh = MeshPart.meshFromShape(singlepart_step, LinearDeflection=0.1)
                        stl_filename= os.path.join(write_folder,os.path.splitext(file)[0]+'_'+str(file_counter)+'.stl')
                        #print('writing ',stl_filename)
                        solid_mesh.write(stl_filename)
                        file_counter=file_counter+1


def read_in_step_files_and_save_as_single_stl_files(read_folder,write_folder,ignore_files=['']):
    list_of_solid_parts=[]
    try:
        os.mkdir(write_folder)
        print('making folder',write_folder)
    except:
        print('error making folder',write_folder)
    #print('read_folder',read_folder)
    #print(os.listdir(read_folder))

    for file in os.listdir(read_folder):
        if file not in ignore_files:
            if file.endswith(".step") or  file.endswith(".stp"):
                #print('reading in ' ,os.path.join(read_folder, file))
                multipart_step = Part.read(os.path.join(read_folder, file))
                stl_filename= write_folder+'/'+os.path.splitext(file)[0]+'.stl'
                
                

                if len(multipart_step.Solids)==0:
                    singlepart_step=multipart_step
                    solid_mesh = MeshPart.meshFromShape(singlepart_step, LinearDeflection=0.1)
                    list_of_solid_parts.append(solid_mesh)
                else:
                    solid_mesh = MeshPart.meshFromShape(multipart_step, LinearDeflection=0.1)
                    
                solid_mesh.write(stl_filename)

def read_in_system_arguments():
    i = 1

    while i < (len(sys.argv)):
        if sys.argv[i] == "-rf":
            read_folder = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-wf":
            write_folder = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "-prefix":
            prefix_required = sys.argv[i + 1]
            i += 2            
        else:
            # end of flags found
            break

    return read_folder , write_folder,prefix_required

def copy_stl_files(read_folder,write_folder,ignore_files=[]):
    #settings.input_folder + '/stl', output_folder_stl,
    list_of_files_copied=[]
    for file in os.listdir(read_folder):
        if file.endswith(".stl"):
                if file not in ignore_files:
                    #print('copying file ', os.path.join(read_folder, file), ' to ', os.path.join(write_folder, file))
                    shutil.copyfile(os.path.join(read_folder,file), os.path.join(write_folder,file))
                    list_of_files_copied.append(file)

    return list_of_files_copied

def find_facets(file):

    multipart_step = Part.read(os.path.join(file))

    solid_mesh = MeshPart.meshFromShape(multipart_step, LinearDeflection=1)
    print(type(solid_mesh))


    for f in solid_mesh.Facets: 
        print f
        print ''
        print f.Points
        print ''
        print f.PointIndices
        print ''
        print ''

    print(len(solid_mesh.Facets))

    print('hi')


# def save_components_as_conformal_stl(dictionary_of_parts,output_folder):
#     try:
#         os.makedirs(output_folder)
#     except:
#         pass
#     #run external trelis script with list of step files as the argument
#     #convert_step_files_to_h5m_with_trelis.py
#
#
# def imprint_and_merge():
#     # import "vov.stp" heal
#     # group "mat:Blanket" add vol 1-4
#     # scale volume all 0.1
#     # imprint body all
#     # merge tolerance 1.e-6
#     # merge all
#     # for command details see the help dagmc
#     # export dagmc "filenamewithpath.h5m" faceteting_tolerance 1.e-4
#     # then to visulise run moab convert
#     # opt/moab/bin/mbconvert filenamewithpath.h5m filenamewithpath.stl
#     # the stl's for each material can be output seperatly using the mbconvert -v flag
#
#
#     pass



#find_facets('armour_mod1.step')

            #print('writing in ' ,os.path.join(read_folder, fil

#read_in_step_files_and_resave_seperated("grouped_step_files","ungrouped_step_files")
#if __name__ == "__main__":
    #read_folder, write_folder,prefix_required = read_in_system_arguments()
    #read_in_step_files_and_resave_as_seperate_stl_files(read_folder,write_folder)
    #read_in_seperate_step_files_and_resave_as_one(read_folder,write_folder,prefix_required)
    #extra_parts = read_in_step_files_and_resave_as_seperate_stl_files('Eurofusion_baseline_2016/reactor_step_files','Eurofusion_baseline_2016/detailed_HCPB/stl')

    #print(extra_parts)
    #read_in_step_files_and_resave_as_single_stl_files(read_folder,write_folder)
    #read_in_step_files_and_resave_seperated(read_folder,write_folder)
    #read_in_step_files_and_resave_as_seperate_stl_files(read_folder,write_folder)
#read_in_step_files_and_resave_as_seperate_stl_files('EU_HCLL_detailed/stp_60','EU_HCLL_detailed_stl/stl_60')
#read_in_step_files_and_resave_as_seperate_stl_files('EU_HCLL_detailed/stp_70','EU_HCLL_detailed_stl/stl_70')

#read_in_stl_files_and_resave("Nova_stl_files","freecad_stl_files")

#read_in_stl_files_and_resave_as_compound("Nova_stl_files","fused_stl_files")









