import pickle
import root_numpy as rnm
import os
import numpy as np

import metadata as md


def exportTimingData(time_difference):

    exportROOTFile(time_difference, "timing","")

# Export noise data
def exportNoiseData(pedestal, noise):

    exportROOTFile(pedestal, "noise", "pedestal")
    exportROOTFile(noise,"noise", "noise")


# Export pulse data
def exportPulseData(peak_value, peak_time, rise_time):

    exportROOTFile(peak_value, "pulse", "peak_value")
    exportROOTFile(peak_time, "pulse", "peak_time")
    exportROOTFile(rise_time, "pulse", "rise_time")


# Export ROOT file with selected information
def exportROOTFile(data, group, category=""):
    
    if category == "":
    
        fileName = md.getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    else:
        fileName = md.getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    data = changeDTYPEOfData(data)

    rnm.array2root(data, fileName, mode="recreate")


# Import noise data file
def importNoiseFile(category):
    
    return importROOTFile("noise", category)


# Import pulse data file
def importPulseFile(category):

    return importROOTFile("pulse", category)

def importTelescopeFile():

    return importROOTFile("telescope")



# Import selected ROOT file
def importROOTFile(group, category=""):

    if category == "":
    
        fileName = md.getSourceFolderPath()+"telescope_data_sep_2017/tracking"+md.getTimeStamp()+".root"
        
        data = rnm.root2array(fileName)
        
        # Convert into mm
        for dimension in data.dtype.names:
            data[dimension] = np.multiply(data[dimension], 0.001)
        
        return data
    
    else:
        fileName = md.getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

        return rnm.root2array(fileName)


def changeDTYPEOfData(data):

    if len(data.dtype.names) == 1:
    
        data = data.astype(  [('chan0', '<f8')] )

    elif len(data.dtype.names) == 2:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8')]  )

    elif len(data.dtype.names) == 3:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ] )

    elif len(data.dtype.names) == 4:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ] )

    elif len(data.dtype.names) == 5:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ] )

    elif len(data.dtype.names) == 6:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ] )

    elif len(data.dtype.names) == 7:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ] )

    else:
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ,('chan7', '<f8')] )

    return data


# Check if the repository is on the stau server
def checkIfRepositoryOnStau():

    number = 4
    # sourceFolderPath is for plots, data, telescope data etc
    sourceFolderPath = "../../HGTD_material/"
    
    if os.path.dirname(os.path.realpath(__file__)) == "/home/aszadaj/Gitlab/HGTD-Efficiency-analysis":
    
        number = 16
        sourceFolderPath = "/home/warehouse/aszadaj/HGTD_material/"
        onStau = True

    defineNumberOfThreads(number)
    md.defineDataFolderPath(sourceFolderPath)


# Define thread number or multiprocessing
def defineNumberOfThreads(number):

    global threads
    threads = number
