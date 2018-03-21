import numpy as np
import root_numpy as rnm
import os
import datetime as dt

import metadata as md


# Export noise data
def exportNoiseData(pedestal, noise):

    exportROOTFile(pedestal, "noise", "pedestal")
    exportROOTFile(noise,"noise", "noise")


# Export pulse data
def exportPulseData(peak_times, peak_values, rise_times):

    exportROOTFile(peak_times, "pulse", "peak_time")
    exportROOTFile(peak_values, "pulse", "peak_value")
    exportROOTFile(rise_times, "pulse", "rise_time")


# Export timing data
def exportTimingLinearData(time_difference):

    exportROOTFile(time_difference, "timing","linear")


def exportTimingSysEqData(time_difference):

    exportROOTFile(time_difference, "timing","sys_eq")



def exportTrackingData(sensor_position):

    exportROOTFile(sensor_position, "tracking", "position")


# Export ROOT file with selected information
def exportROOTFile(data, group, category=""):
    
    if group == "timing":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif category == "position":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(category)+"_"+str(md.getBatchNumber())+".root"
    
    else:
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    if group != "timing":
        data = changeDTYPEOfData(data)


    rnm.array2root(data, fileName, mode="recreate")



# Import noise data file
def importNoiseFile(category):
    
    return importROOTFile("noise", category)


# Import pulse data file
def importPulseFile(category):

    return importROOTFile("pulse", category)

def importTrackingFile(category=""):

    return importROOTFile("tracking", category)

def importTimingFile(category):

    return importROOTFile("timing", category)



# Import selected ROOT file
def importROOTFile(group, category=""):

    if group == "tracking":
        
        if category == "":
        
            fileName = getSourceFolderPath()+"tracking_data_sep_2017/tracking"+md.getTimeStamp()+".root"
        
        else:
            fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+group+"/"+category+"_"+str(md.getBatchNumber())+".root"

        return rnm.root2array(fileName)
    
    elif group == "timing":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

        return rnm.root2array(fileName)

    
    else:
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
        
        
        return rnm.root2array(fileName)

def convertNoiseData(noise_average, noise_std):
    
    for chan in noise_std.dtype.names:
        noise_average[chan] =  np.multiply(noise_average[chan], -1000)
        noise_std[chan] = np.multiply(noise_std[chan], 1000)

    return noise_average, noise_std



def convertPulseData(peak_values):
    
    for chan in peak_values.dtype.names:
        peak_values[chan] =  np.multiply(peak_values[chan], -1000)

    return peak_values


def convertTrackingData(tracking, peak_values):

    for dimension in tracking.dtype.names:
        tracking[dimension] = np.multiply(tracking[dimension], 0.001)

    for chan in peak_values.dtype.names:
        peak_values[chan] = np.multiply(peak_values[chan], -1000)

    return tracking, peak_values


def changeDTYPEOfData(data):


    if len(data.dtype.names) == 7:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ] )

    else:
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ,('chan7', '<f8')] )

    return data


# Create array for exporting center positions, inside tracking
def createCenterPositionArray():

    dt = (  [('chan0', '<f8', 2), ('chan1', '<f8', 2) ,('chan2', '<f8', 2) ,('chan3', '<f8', 2) ,('chan4', '<f8', 2) ,('chan5', '<f8', 2) ,('chan6', '<f8', 2) ,('chan7', '<f8', 2)] )
    
    return np.zeros(1, dtype = dt)


# Check if the repository is on the stau server
def checkIfRepositoryOnStau():

    threadNumber = 4
    
    # sourceFolderPath is for plots, data, tracking data etc
    sourceFolderPath = "/Users/aszadaj/cernbox/SH203X/HGTD_material/"
    
    if os.path.dirname(os.path.realpath(__file__)) == "/home/aszadaj/Gitlab/HGTD-Efficiency-analysis":
    
        threadNumber = 16
        sourceFolderPath = "/home/warehouse/aszadaj/HGTD_material/"
        onStau = True
    
        setIfOnHDD(False)

    defineNumberOfThreads(threadNumber)
    defineDataFolderPath(sourceFolderPath)


# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])

def setIfOnHDD(value):

    global hdd
    hdd = value

def isOnHDD():

    return hdd

def setIfOnHITACHI(value):

    global hitachi
    hitachi = value

def isOnHITACHI():

    return hitachi

# Define folder where the pickle files should be
def defineDataFolderPath(source):

    global sourceFolderPath
    sourceFolderPath = source


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath


# Define thread number or multiprocessing
def defineNumberOfThreads(number):

    global threads
    threads = number

def setNumberOfThreads(number):
    threads = number

