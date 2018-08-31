import ROOT
import numpy as np
import root_numpy as rnm
import os
import datetime as dt

import run_log_metadata as md


# Export noise data
def exportNoiseData(noise, pedestal):

    exportROOTFile(noise,  "noise", "noise")
    exportROOTFile(pedestal, "noise", "pedestal")


def exportNoiseDataPlot(noise, pedestal):

    exportROOTFile(noise,  "noise_plot", "noise")
    exportROOTFile(pedestal, "noise_plot", "pedestal")


# Export pulse data
def exportPulseData(variable_array):

    [peak_times, peak_values, rise_times, cfd05, points, max_sample, charge] = [i for i in variable_array]

    exportROOTFile(peak_times, "pulse", "peak_time")
    exportROOTFile(peak_values, "pulse", "peak_value")
    exportROOTFile(rise_times, "pulse", "rise_time")
    exportROOTFile(cfd05, "pulse", "cfd05")
    exportROOTFile(points, "pulse", "points")
    exportROOTFile(max_sample, "pulse", "max_sample")
    exportROOTFile(charge, "pulse", "charge")


# Export timing data
def exportTimeDifferenceData(time_difference_peak, time_difference_cfd05):

    exportROOTFile(time_difference_peak, "timing", "linear")
    exportROOTFile(time_difference_cfd05, "timing", "linear_cfd05")

def exportTimeDifferenceDataSysEq(time_difference_peak_sys_eq, time_difference_cfd05_sys_eq ):

    exportROOTFile(time_difference_peak_sys_eq, "timing", "sys_eq")
    exportROOTFile(time_difference_cfd05_sys_eq, "timing", "sys_eq_cfd05")

def exportTrackingData(sensor_position):

    exportROOTFile(sensor_position, "tracking", "position")



# Export results

def exportNoiseResults(pedestal_result, noise_result, sensor_info):

    exportROOTFile(pedestal_result, "results", "pedestal", sensor_info)
    exportROOTFile(noise_result, "results", "noise", sensor_info)


def exportPulseResults(peak_value_result, charge_result, rise_time_result, sensor_info):

    exportROOTFile(peak_value_result, "results", "peak_value", sensor_info)
    exportROOTFile(charge_result, "results", "charge", sensor_info)
    exportROOTFile(rise_time_result, "results", "rise_time", sensor_info)


def exportTimingResults(timing_results, sensor_info, same_osc, cfd05):
    
    exportROOTFile(timing_results, "results", "timing_normal", sensor_info, same_osc, cfd05)


def exportTimingResultsSysEq(timing_results, sensor_info, cfd05):
    
    exportROOTFile(timing_results, "results", "timing_system", sensor_info, False, cfd05)



# Export ROOT file with selected information
def exportROOTFile(data, group, category="", sensor_info=[], same_osc=False, cfd05=False):
    
    if group == "timing":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+group+"_"+category+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif category == "position":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(category)+"_"+str(md.getBatchNumber())+".root"

    elif group == "results":

        fileName = getSourceFolderPath()+"results_data_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category

        if category.find("timing") != -1:
        
            fileName += "_peak"+"/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_diff_osc_peak.root"
        
            if same_osc:
                fileName = fileName.replace("diff_osc", "same_osc")
        
            if cfd05:
                fileName = fileName.replace("peak", "cfd05")


        else:
        
            fileName += "/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+".root"
            
    elif group == "noise_plot":

        group = group.replace("noise_plot", "noise")

        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_plot/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif group == "noise":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getBatchNumber())+".root"
    
    
    else:
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    if group != "timing" and group != "results" and category != "position":
        data = changeDTYPEOfData(data)

    rnm.array2root(data, fileName, mode="recreate")


def exportROOTHistogram(graphList, fileName):

    rootDestination = fileName.replace("plots_hgtd_efficiency_sep_2017", "plots_data_hgtd_efficiency_sep_2017")
    rootDestination = rootDestination.replace(".pdf", ".root")
    fileObject = ROOT.TFile(rootDestination, "RECREATE")
    graphList.Write()
    fileObject.Close()





# Import noise data file
def importNoiseFile(category):
    
    return importROOTFile("noise", category)


def importNoiseFilePlot(category):
    
    return importROOTFile("noise_plot", category)


# Import pulse data file
def importPulseFile(category):

    return importROOTFile("pulse", category)

def importTrackingFile(category=""):

    return importROOTFile("tracking", category)

def importTimingFile(category):

    return importROOTFile("timing", category)


# import results

def importNoiseResults(sensor_info):

    return importROOTFile("results", "noise", sensor_info)


def importPulseResults(category, sensor_info):

    return importROOTFile("results", category, sensor_info)


def importTimingResults(sensor_info, same_osc, cfd05):
    
    return importROOTFile("results", "timing", sensor_info, same_osc, cfd05)


def importTimingResultsSysEq(sensor_info, same_osc, cfd05):
    
    return importROOTFile("results", "timing_sys_eq", sensor_info, same_osc, cfd05)



# Import selected ROOT file, sensor_info is consisted of name of the sensor and channel name
def importROOTFile(group, category="", sensor_info=[], same_osc=False, cfd05=False):

    if group == "tracking":
        
        if category == "":
        
            fileName = getSourceFolderPath()+"tracking_data_sep_2017/tracking"+md.getTimeStamp()+".root"
        
        else:
            fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+group+"/"+category+"_"+str(md.getBatchNumber())+".root"


    elif group == "timing":

        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+group+"_"+category+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"


    elif group == "results":

        fileName = getSourceFolderPath()+"results_data_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category

        if category.find("timing") != -1:
        
            fileName += "_peak"+"/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_diff_osc_peak.root"
        
            if same_osc:
                fileName = fileName.replace("diff_osc", "same_osc")
        
            if cfd05:
                fileName = fileName.replace("peak", "cfd05")


        else:
        
            fileName += "/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+".root"

    elif group == "noise_plot":
    
        group = group.replace("noise_plot", "noise")
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_plot/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    elif group == "noise":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getBatchNumber())+".root"


    else:
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"


    return rnm.root2array(fileName)


def importROOTHistogram(fileName):

    rootDestination = fileName.replace("plots_hgtd_efficiency_sep_2017", "plots_data_hgtd_efficiency_sep_2017")
    rootDestination = rootDestination.replace(".pdf", ".root")
    fileObject = ROOT.TFile(rootDestination)

    return fileObject


# Read file names which are enlisted in the folder
def readFileNames(fileType):

    folderPath = ""
    
    if fileType == "tracking": #tracking1504949898.root
        folderPath = "tracking_data_sep_2017/"
        first_index = 8
        last_index = 18

    elif fileType == "peak_value": #pulse_peak_value_3656.root
        folderPath = "data_hgtd_efficiency_sep_2017/pulse/pulse_peak_value/"
        first_index = 17
        last_index = 21


    mainFolderPath = getSourceFolderPath() + folderPath
    
    availableFiles = [int(f[first_index:last_index]) for f in os.listdir(mainFolderPath) if os.path.isfile(os.path.join(mainFolderPath, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles


# Check if the tracking file is available
def isTrackingFileAvailableAndOK():

    availableFilesPulse         = readFileNames("peak_value")
    availableFilesTracking     = readFileNames("tracking")

    found = False
    
    for pulse_file in availableFilesPulse:
        if pulse_file == int(md.getRunNumber()):
            for tracking_file in availableFilesTracking:
                if tracking_file == int(md.getTimeStamp()):
                    if md.getRunNumber() in md.corruptedRuns():
                        found = False
                    else:
                        found = True

    return found



def convertNoiseData(noise_average, noise_std):
    
    for chan in noise_std.dtype.names:
        noise_average[chan] =  np.multiply(noise_average[chan], -1000)
        noise_std[chan] = np.multiply(noise_std[chan], 1000)



def convertPulseData(peak_values):
    
    for chan in peak_values.dtype.names:
        peak_values[chan] =  np.multiply(peak_values[chan], -1000)


def convertRiseTimeData(rise_times):
    
    for chan in rise_times.dtype.names:
        rise_times[chan] =  np.multiply(rise_times[chan], 1000)



def convertChargeData(charge):
    
    for chan in charge.dtype.names:
        charge[chan] =  np.multiply(charge[chan], 10**15)



# Conversion of charge to gain, following a charge from a MIP, which is for a pion
# 0.46 fC -> Gain = charge/MIP and convert to fC
def convertChargeToGainData(charge):

    # The deposited charge from a MIP (here pion)
    MIP_charge = 0.46*10**-15

    for chan in charge.dtype.names:
        charge[chan] = np.divide(charge[chan], MIP_charge)



def changeDTYPEOfData(data):


    if len(data.dtype.names) == 7:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ] )

    elif len(data.dtype.names) == 3:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ] )
    
    elif len(data.dtype.names) == 4:
    
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ])

    else:
        data = data.astype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ,('chan7', '<f8')] )

    return data





# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])


# Define folder where the pickle files should be
def defineDataFolderPath():
    source  = "/Users/aszadaj/cernbox/SH203X/HGTD_material/"
    global sourceFolderPath
    sourceFolderPath = source

def getSourceResultsDataPath():

    return sourceFolderPath + "results_data_hgtd_efficiency_sep_2017/"


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath


def getDataPath():

    dataPath = getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    if "HDD500" in os.listdir("/Volumes"):
    
        dataPath = "/Volumes/HDD500/" + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"


    return dataPath

