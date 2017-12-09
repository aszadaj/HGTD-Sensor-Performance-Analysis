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


def exportPulseData(amplitudes, rise_times, half_max_times, criticalValues):

    print "export"

    exportPulseFile(amplitudes, "amplitudes")
    exportPulseFile(rise_times, "rise_times")
    exportPulseFile(half_max_times, "half_max_times")
    exportPulseFile(criticalValues, "critical_values")


def exportPulseFile(data, dataType):

    with open(md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/pulse_files/pulse_"+str(dataType)+"/pulse_"+str(dataType)+"_"+str(md.getBatchNumber())+".pkl","wb") as output:
        
        pickle.dump(data,output,pickle.HIGHEST_PROTOCOL)


def importPulseFile(dataType):

    with open(md.getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/pulse_files/pulse_"+str(dataType)+"/pulse_"+str(dataType)+"_"+str(md.getBatchNumber())+".pkl","rb") as input:
       
        dataFile = pickle.load(input)

    return dataFile


# Note, the file have only 200K entries
def importTelescopeDataBatch():

    batchNumber = md.getBatchNumber()
    timeStamps = md.getTimeStampsForBatch(batchNumber)
    
    data_batch = np.empty(0, dtype=[('X', '<f4'), ('Y', '<f4')])

    for timeStamp in timeStamps:
        dataFileName = md.getSourceFolderPath() + "forAntek/tracking"+str(timeStamp)+".root"
        data_batch = np.concatenate((data_batch, rnm.root2array(dataFileName, start=0, stop=200000)), axis=0)

    # Convert into mm
    for dimension in data_batch.dtype.names:
        data_batch[dimension] = np.multiply(data_batch[dimension], 0.001)
  
    return data_batch


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




