import pickle
import root_numpy as rnm
import os
import numpy as np

import metadata as md


def exportNoiseData(pedestal, noise):

    exportNoiseFile(pedestal, "pedestal")
    exportNoiseFile(noise, "noise")


def exportNoiseFile(data, dataType):

    with open(md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_"+str(dataType)+"/noise_"+str(dataType)+"_"+str(md.getBatchNumber())+".pkl","wb") as output:
        
        pickle.dump(data,output,pickle.HIGHEST_PROTOCOL)


def importNoiseFile(dataType):
    
    with open(md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_"+str(dataType)+"/noise_"+str(dataType)+"_"+str(md.getBatchNumber())+".pkl","rb") as input:
       
        dataFile = pickle.load(input)

    return dataFile


def exportPulseData(amplitudes, rise_times, peak_times, criticalValues):

    exportPulseFile(amplitudes, "amplitudes")
    exportPulseFile(rise_times, "rise_times")
    exportPulseFile(peak_times, "peak_times")
    exportPulseFile(criticalValues, "critical_values")


def exportPulseFile(data, dataType):

    with open(md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/pulse_files/pulse_"+str(dataType)+"/pulse_"+str(dataType)+"_"+str(md.getBatchNumber())+".pkl","wb") as output:
        
        pickle.dump(data,output,pickle.HIGHEST_PROTOCOL)


def importPulseFile(dataType):

    with open(md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/pulse_files/pulse_"+str(dataType)+"/pulse_"+str(dataType)+"_"+str(md.getBatchNumber())+".pkl","rb") as input:
       
        dataFile = pickle.load(input)

    return dataFile


# Note, the file have only 200K entries
def importTelescopeData():
    
    dataFileName = md.getSourceFolderPath() + "forAntek/tracking"+str(md.getTimeStamp())+".root"
    data = rnm.root2array(dataFileName)
    
    # Convert into mm
    for dimension in data.dtype.names:
        data[dimension] = np.multiply(data[dimension], 0.001)
  
    return data


# Check if the repository is on the stau server
def checkIfRepositoryOnStau():

    number = 4
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



