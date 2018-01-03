import pickle
import root_numpy as rnm
import os
import numpy as np

import metadata as md


# Export noise data
def exportNoiseData(pedestal, noise):

    exportROOTFile(pedestal, "noise", "pedestal", "file")
    exportROOTFile(noise,"noise", "noise", "file")


# Export pulse data
def exportPulseData(peak_value, peak_time, rise_time):

    exportROOTFile(peak_value, "pulse", "peak_value", "file")
    exportROOTFile(peak_time, "pulse", "peak_time", "file")
    exportROOTFile(rise_time,"pulse", "rise_time", "file")


# Export plot information
def exportPulsePlot(peak_value, peak_time, rise_time):

    exportROOTFile(peak_value, "pulse", "peak_value", "plot")
    exportROOTFile(peak_time, "pulse", "peak_time", "plot")
    exportROOTFile(rise_time,"pulse", "rise_time", "plot")


# Export ROOT file with selected information
def exportROOTFile(data, group, category, dataType, channelName=""):
    
    fileLocation = "data_hgtd_efficiency_sep_2017"
    chan = channelName + "_"
    
    if category == "plot":
        fileLocation = "plots_hgtd_efficiency_sep_2017"
    
    else:
        chan = ""
    fileName = md.getSourceFolderPath()+str(fileLocation)+"/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getBatchNumber())+".root"

    data = changeDTYPEOfData(data)

    rnm.array2root(data, fileName, mode="recreate")


# Import noise data file
def importNoiseFile(category):
    
    return importROOTFile("noise", category, "file")


# Import pulse data file
def importPulseFile(category):

    return importROOTFile("pulse", category, "file")


# Import plot information
# Future fix, adapt the code to import plots which are dependent on channel
def importPulsePlot(dataType):

    return importROOTFile("pulse", "plot", dataType)


# Import selected ROOT file
def importROOTFile(group, category, dataType):
  
    fileLocation = "data_hgtd_efficiency_sep_2017"
    
    if category == "plot":
        fileLocation = "plots_hgtd_efficiency_sep_2017"

    fileName = md.getSourceFolderPath()+str(fileLocation)+"/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getBatchNumber())+".root"
    
    data = rnm.root2array(fileName)

    return data


# Note, the file have only 200K entries
def importTelescopeDataBatch():

    batchNumber = md.getBatchNumber()
    timeStamps = md.getTimeStampsForBatch(batchNumber)
    
    data_batch = np.empty(0, dtype=[('X', '<f8'), ('Y', '<f8')])

    for timeStamp in timeStamps:
        dataFileName = md.getSourceFolderPath() + "telescope_data_sep_2017/tracking"+str(timeStamp)+".root"
        data_batch = np.concatenate((data_batch, rnm.root2array(dataFileName, start=0, stop=200000)), axis=0)

    # Convert into mm
    for dimension in data_batch.dtype.names:
        data_batch[dimension] = np.multiply(data_batch[dimension], 0.001)
  
    return data_batch


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
