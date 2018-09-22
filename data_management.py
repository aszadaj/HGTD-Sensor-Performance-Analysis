import ROOT
import numpy as np
import root_numpy as rnm
import os
import datetime as dt

import run_log_metadata as md


# Export pulse data
def exportPulseData(variable_array):

    [peak_values, rise_times, charge, cfd, peak_times, points, max_sample] = [i for i in variable_array]

    exportImportROOTData("pulse", "peak_value", True, peak_values)
    exportImportROOTData("pulse", "rise_time", True, rise_times)
    exportImportROOTData("pulse", "charge", True, charge)
    exportImportROOTData("pulse", "cfd", True, cfd)
    exportImportROOTData("pulse", "peak_time", True, peak_times)
    exportImportROOTData("pulse", "points", True, points)
    exportImportROOTData("pulse", "max_sample", True, max_sample)


def exportPulseResults(peak_value_result, rise_time_result, charge_result, chan):

    exportImportROOTData("results", "peak_value", True, peak_value_result, chan)
    exportImportROOTData("results", "rise_time", True, rise_time_result, chan)
    exportImportROOTData("results", "charge", True, charge_result, chan)


# Export ROOT file with selected information

def exportImportROOTData(group, category, export, data=0, chan="", same_osc=False, cfd=False):

    if group == "tracking":
        
        if category == "":
        
            fileName = getSourceFolderPath()+getTrackingSourceFolder()+"/"+group+md.getTimeStamp()+".root"

        else:
            fileName = getSourceFolderPath()+getDataSourceFolder()+"/"+group+"/"+category+"_"+str(md.getBatchNumber())+".root"


    elif group == "timing":
    
        fileName = getSourceFolderPath()+getDataSourceFolder()+"/"+str(group)+"/"+group+"_"+category+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif category == "position":
    
        fileName = getSourceFolderPath()+getDataSourceFolder()+"/"+str(group)+"/"+str(category)+"_"+str(md.getBatchNumber())+".root"

    elif group == "results":

        fileName = getSourceFolderPath()+getResultsSourceDataPath()+"/"+md.getNameOfSensor(chan)+"/"+category

        if category.find("timing") != -1:
        
            fileName += "_peak"+"/"+category+"_"+str(md.getBatchNumber())+"_"+chan+"_peak.root"
        
            if category.find("system") == -1:
        
                if same_osc:
                    fileName = fileName.replace("_peak.root", "_same_osc_peak.root")
                
                else:
                     fileName = fileName.replace("_peak.root", "_diff_osc_peak.root")

            if cfd:
                fileName = fileName.replace("peak", "cfd")
            

        else:
        
            fileName += "/"+category+"_"+str(md.getBatchNumber())+"_"+chan+".root"
            
    elif group == "noise_plot":

        group = group.replace("noise_plot", "noise")

        fileName = getSourceFolderPath()+getDataSourceFolder()+"/"+str(group)+"/"+str(group)+"_"+str(category)+"_plot/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"
    
    elif group == "noise":
    
        fileName = getSourceFolderPath()+getPlotsSourceFolder()+"/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getBatchNumber())+".root"
    
    
    else:
        fileName = getSourceFolderPath()+getDataSourceFolder()+"/"+str(group)+"/"+str(group)+"_"+str(category)+"/"+str(group)+"_"+str(category)+"_"+str(md.getRunNumber())+".root"

    if group != "timing" and group != "results" and category != "position" and export:
        data = data.astype(getDTYPE())



    if export:
    
        rnm.array2root(data, fileName, mode="recreate")

    else:
    
        return rnm.root2array(fileName)


def exportImportROOTHistogram(fileName, export, graphList = 0):
    
    rootDirectory = fileName.replace(getPlotsSourceFolder(), getHistogramsSourceFolder())
    rootDirectory = rootDirectory.replace(".pdf", ".root")
    
    if export:
        
        fileObject = ROOT.TFile(rootDirectory, "RECREATE")
        graphList.Write()
        fileObject.Close()
        
    else:
        return ROOT.TFile(rootDirectory)


def importNoiseProperties():
    
    noise = np.zeros(1, dtype=getDTYPE())
    pedestal = np.zeros(1, dtype=getDTYPE())
    
    
    for chan in noise.dtype.names:
        noise[chan] = (exportImportROOTData("results", "noise", False, 0, chan))["noise"][0] * 0.001
        pedestal[chan] = (exportImportROOTData("results", "pedestal", False, 0, chan)) ["pedestal"][0] * -0.001
    

    return noise, pedestal


# Read file names which are enlisted in the folder
def readFileNames(category, subcategory=0):
    
    if category == "tracking":
        folderPath = getSourceFolderPath() + getTrackingSourceFolder()+"/"

    elif category == "oscilloscope":
        
        folderPath = oscilloscopePath

    else:
        folderPath = getSourceFolderPath() + getDataSourceFolder()+"/" + category + "/" + category + "_" + subcategory + "/"

    # This line reads in a list of sorted files
    # from a provided folder above, strips down non-integer characters and converts to integers.
    # The file is also checked if the file is readable and avoids .DS_Store-files typical for macOS.


    availableFiles = sorted([int(filter(lambda x: x.isdigit(), f)) for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f)) and f != '.DS_Store'])

    return availableFiles


def checkIfFileAvailable():

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

    if not found:
        print "Files required for run number", md.getRunNumber(), "are missing. Skipping run.\n"

    return found



def changeIndexNumpyArray(numpy, factor):

    for chan in numpy.dtype.names:
        numpy[chan] = np.multiply(numpy[chan], factor)



def getDTYPE(batchNumber = 0):
    
    if batchNumber == 0:
        batchNumber = md.getBatchNumber()
    
    batchMainNumber = batchNumber/100

    if batchMainNumber == 6: # Batch 6 have 3 channels
    
        dtype = np.dtype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ] )

    elif batchMainNumber == 3: # Batch 3 have 7 channels
    
        dtype = np.dtype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ] )

    else: # rest have 8 channels
    
        dtype = np.dtype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ,('chan7', '<f8')] )

    return dtype


# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])


# Define the original folder of produced ROOT files, plots and miscellaneous data
def defineDataFolderPath():

    global oscilloscopePath
    global sourceFolderPath
    
    sourceFolderPath = "/Users/aszadaj/cernbox/SH203X/HGTD_material/"
    
    if "HDD500" in os.listdir("/Volumes"):

        oscilloscopePath = "/Volumes/HDD500/"+getOscillscopeSourceFolder()+"/"
    
    elif "HITACHI" in os.listdir("/Volumes"):
    
        oscilloscopePath = "/Volumes/HITACHI/"+getOscillscopeSourceFolder()+"/"
    
    else:
    
        oscilloscopePath = sourceFolderPath + ""+getOscillscopeSourceFolder()+"/"


def getResultsSourceDataPath():

    return "results_data_hgtd_tb_sep17"

def getResultsPlotSourceDataPath():

    return "results_plots_hgtd_tb_sep17"


def getPlotsSourceFolder():

    return "plots_hgtd_tb_sep17"

def getDataSourceFolder():

     return "data_hgtd_tb_sep17"

def getTrackingSourceFolder():

     return "tracking_hgtd_tb_sep17"

def getHistogramsSourceFolder():

    return "histograms_data_hgtd_tb_sep17"

def getOscillscopeSourceFolder():

    return "oscilloscope_data_hgtd_tb_sep17"


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath

def setFunctionAnalysis(function):

    global functionAnalysis
    functionAnalysis = function


def getDataPath():

    dataPath = oscilloscopePath + "data_"+str(md.getTimeStamp())+".tree.root"

    return dataPath
