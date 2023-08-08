# -*- coding: utf-8 -*-
"""
Created on Wed May 10 14:03:50 2023

@author: lott
GS d- s:+ a- C++ t 5 X R tv b+ D+ G e+++ h r++ 
"""

import javabridge
import bioformats
import pandas as pd
import os
javabridge.start_vm(class_path=bioformats.JARS)
# Be careful with this. After starting a VM it needs to be killed.
# After killing the vm it cannot be started in the same console ->RunTimeError

def lines_to_times(meta_lines:list)->(list,list):
    """
    Extracts the imaging times and position IDs from .nd2 metadata.
    Times will be given in seconds since imaging started.

    Parameters
    ----------
    meta_lines : list
        list of lines (str) in the metadata of the nd2 file.

    Returns
    -------
    (image_times,IDs)
        image_times: list of list. contains times of image recordings (in 
                     seconds after recording start) for each imaging position.
        IDs: list of IDs of imaging positions.

    """
    image_times = [] # list to store times of image recording for all xy positions
    time_list = [] # list to temporarily store time of image recording
    PosT_list = [] # list to temporarily store timepoint of imaging
                   # Used to check for duplicate times from multi-frame recording
    IDs = []
    
    line_no = 0
    for line in meta_lines:
        if line.startswith("<Image ID"):
            IDs.append("xy"+str(line.split("<Image ID=\"Image:")[1][0]))
            # print(line)
            # print(line_no)
            if len(time_list) > 0: 
                # if entrys are in time_lis, store list in image_times and
                # create new lists
                image_times.append(time_list)
                
                time_list = []
                PosT_list = []
            
        if line.startswith("<Plane DeltaT"):
            
            time = round(float(line.split("\" ")[0].split("DeltaT=\"")[1]))
            PosT = int(line.split("TheT=\"")[1].split("\" TheZ")[0])
            if not PosT in PosT_list:
                # if multi-channel imaging, store only first channel
                time_list.append(time)
                PosT_list.append(PosT)
        line_no+= 1
    image_times.append(time_list)
    return image_times, IDs

def create_DataFrame(image_times:list, IDs:list)->pd.DataFrame:
    """
    Creates a pandas DataFrame of the imaging times from list of lists.
    
    Columns are imaging positions, rows imaging timepoints.
    E.g. row1 -> times of first imaging, row 2 -> times of second imaging.

    Parameters
    ----------
    image_times : list of lists. contains times of image recordings for each imaging 
                  position. 
                  Generated through lines_to_times function
    IDs : list of IDs of imaging positions.
          Generated through lines_to_times function

    Returns
    -------
    df : pandas.DataFrame
        DESCRIPTION.

    """
    df = pd.DataFrame(image_times).transpose()
    df.columns = IDs
    return df

def get_times(path:str)->pd.DataFrame:
    """
    Creates a pandas DataFrame of imaging times from metadata in a .nd2 
    bioformat file as generated when using Nikon microscopy software.
    
    Rows of the Dataframe denote imaging timepoints/loops, while columns denote
    each position recorded. Times will be listed in seconds since start of
    imaging. Useful for when another process needs to be synced with obtained 
    images after recording.

    Parameters
    ----------
    path : str
        Path to the .nd2 file.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame of imaging time of each timepoint (rows) at each position 
        (columns). 
        E.g. row1 -> times of first imaging, row 2 -> times of second imaging.

    """
    meta = bioformats.get_omexml_metadata(path)
    meta_lines = meta.replace("><", ">/n<").split("/n")
    image_times, IDs = lines_to_times(meta_lines)
    df = create_DataFrame(image_times, IDs)
    return df

if __name__ == "__main__":
    # path = 'N:/shared/Learning/Experiments/5ng_5x[1-3]/20220530_MCF7_Learning_5x[1-3]_Pulse_5ng/20220530_MCF7_Learning_5x[1-3]_5ng.nd2'
    path = input("Provide a path:")
    date = path.split("/")[-1].split("_")[0]
    df = get_times(path)
    df.to_csv(os.path.join(os.path.dirname(path), date + "_metadata_image_times.csv"))
   
# to apply to a whole folder containing several folders of experiments
# iterates over all files, opens folders, searches whether appropriate nd2
# files are present and then generates the metadata file.
    # toppath = 'N:/shared/Learning/Experiments/Habituation'
    # for file in os.listdir(toppath):
    #     if not os.path.isdir(os.path.join(toppath,file)):
    #         continue
    #     date = file.split("_")[0]
    #     for filefile in os.listdir(os.path.join(toppath,file)):
    #         if not filefile.endswith(".nd2"):
    #             continue
    #         if not filefile.startswith(date):
    #             continue
    #         nd_path = os.path.join(os.path.join(toppath,file), filefile)
    #         print(nd_path)
    #         df = get_times(nd_path)
    #         df.to_csv(os.path.join(os.path.dirname(nd_path), date + "_metadata_image_times.csv"))
    
# javabridge.kill_vm() # kill the java virtual machine
# After killing the vm it cannot be started in the same console -> RunTimeError
# see the following issues on that topic:
# https://github.com/LeeKamentsky/python-javabridge/issues/161
# https://github.com/LeeKamentsky/python-javabridge/issues/88
