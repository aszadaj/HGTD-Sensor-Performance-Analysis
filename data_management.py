import ROOT
import numpy as np
import root_numpy as rnm
import os
import datetime as dt

import run_log_metadata as md


# Export pulse data
def exportPulseData(variable_array):

    [peak_times, peak_values, rise_times, cfd, points, max_sample, charge] = [i for i in variable_array]

    exportImportROOTData("pulse", "peak_time", peak_times, True)
    exportImportROOTData("pulse", "peak_value", peak_values, True)
    exportImportROOTData("pulse", "rise_time", rise_times, True)
    exportImportROOTData("pulse", "cfd", cfd, True)
    exportImportROOTData("pulse", "points", points, True)
    exportImportROOTData("pulse", "max_sample", max_sample, True)
    exportImportROOTData("pulse", "charge",charge, True)


def exportPulseResults(peak_value_result, charge_result, rise_time_result, sensor_info):

    exportImportROOTData("results", "peak_value", peak_value_result, True, sensor_info)
    exportImportROOTData("results", "charge", charge_result, True, sensor_info)
    exportImportROOTData("results", "rise_time", rise_time_result, True, sensor_info)


# Export ROOT file with selected information

def exportImportROOTData(group, category, export, data=0, sensor_info=[], same_osc=False, cfd=False):

    if group == "tracking":
        
        if category == "":
        
            fileName = getSourceFolderPath()+"tracking_data_sep_2017/tracking"+md.getTimeStamp()+".root"

        else:
            fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+group+"/"+category+"_"+str(md.getBatchNumber())+".root"


    elif group == "timing":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+group+"_"+category+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif category == "position":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(category)+"_"+str(md.getBatchNumber())+".root"

    elif group == "results":

        fileName = getSourceFolderPath()+"results_data_hgtd_efficiency_sep_2017/"+sensor_info[0]+"/"+category

        if category.find("timing") != -1:
        
            fileName += "_peak"+"/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+"_peak.root"
        
            if category.find("system") == -1:
        
                if same_osc:
                    fileName = fileName.replace("_peak.root", "_same_osc_peak.root")
                
                else:
                     fileName = fileName.replace("_peak.root", "_diff_osc_peak.root")

            if cfd:
                fileName = fileName.replace("peak", "cfd")
            

        else:
        
            fileName += "/"+category+"_"+str(md.getBatchNumber())+"_"+sensor_info[1]+".root"
            
    elif group == "noise_plot":

        group = group.replace("noise_plot", "noise")

        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"_plot/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif group == "noise":
    
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getBatchNumber())+".root"
    
    
    else:
        fileName = getSourceFolderPath()+"data_hgtd_efficiency_sep_2017/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    if group != "timing" and group != "results" and category != "position" and export:
        
        data = changeDTYPEOfData(data)


    if export:
    
        rnm.array2root(data, fileName, mode="recreate")

    else:
    
        return rnm.root2array(fileName)


def exportImportROOTHistogram(fileName, export, graphList = 0):
    
    rootDirectory = fileName.replace("plots_hgtd_efficiency_sep_2017", "plots_data_hgtd_efficiency_sep_2017")
    rootDirectory = rootDirectory.replace(".pdf", ".root")
    
    if export:
        
        fileObject = ROOT.TFile(rootDirectory, "RECREATE")
        graphList.Write()
        fileObject.Close()
        
    else:
        return ROOT.TFile(rootDirectory)


# Read file names which are enlisted in the folder
def readFileNames(category, subcategory=0):

    if category == "tracking":
        folderPath = getSourceFolderPath() + "tracking_data_sep_2017/"

    elif category == "oscilloscope":
        folderPath = oscilloscopePath

    else:
        folderPath = getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/" + category + "/" + category + "_" + subcategory + "/"

    # Yes, one of the craziest lines I have written. This line reads in a list of sorted files
    # from a provided folder above, strips down non-integer characters and converts to integers.
    # The file is also checked if the file is readable and avoids .DS_Store-files typical for macOS.

    availableFiles = sorted([int(filter(lambda x: x.isdigit(), f)) for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f)) and f != '.DS_Store'])

    return availableFiles


def areFilesAvailable():

    found = False

    if functionAnalysis == "noise_analysis" or functionAnalysis == "pulse_analysis" :
    
        files = readFileNames("oscilloscope")

        if int(md.getTimeStamp()) in files:
            found = True

    elif functionAnalysis == "timing_analysis":
    
        files_cfd = readFileNames("pulse", "cfd")
        files_peak_time = readFileNames("pulse", "peak_time")
    
        if int(md.getRunNumber()) in files_cfd and int(md.getRunNumber()) in files_peak_time:
            found = True
            

    elif functionAnalysis == "tracking_analysis":

        files_peak_value    = readFileNames("pulse", "peak_value")
        files_tracking = readFileNames("tracking")

        if int(md.getTimeStamp()) in files_tracking and int(md.getRunNumber()) in files_peak_value:

            found = True


    return found


def checkIfFileAvailable():
    bool = True
    
    if not areFilesAvailable():
        print "Files required for run number", md.getRunNumber(), "are missing. Skipping run.\n"
        bool = False
    
    return bool



def changeIndexNumpyArray(numpy, factor):

    for chan in numpy.dtype.names:
        numpy[chan] = np.multiply(numpy[chan], factor)



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


# Define the original folder of produced ROOT files, plots and miscallenous
def defineDataFolderPath():

    global oscilloscopePath
    global sourceFolderPath
    sourceFolderPath = "/Users/aszadaj/cernbox/SH203X/HGTD_material/"
    
    if "HDD500" in os.listdir("/Volumes"):

        oscilloscopePath = "/Volumes/HDD500/oscilloscope_data_sep_2017/"
    
    elif "HITACHI" in os.listdir("/Volumes"):
    
        oscilloscopePath = "/Volumes/HITACHI/oscilloscope_data_sep_2017/"
    
    else:
    
        oscilloscopePath = sourceFolderPath + "oscilloscope_data_sep_2017/"


def getSourceResultsDataPath():

    return sourceFolderPath + "results_data_hgtd_efficiency_sep_2017/"


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath

def setFunctionAnalysis(function):

    global functionAnalysis
    functionAnalysis = function


def getDataPath():

    dataPath = oscilloscopePath + "data_"+str(md.getTimeStamp())+".tree.root"

    return dataPath

