import ROOT
import numpy as np
import root_numpy as rnm
import os
import csv
import datetime as dt

import run_log_metadata as md

# Return run log imported from a .csv file
# For future .csv files, it is crucial that the run log have the same
# shape as the sep2017 one!
def getRunLog():
    
    run_log_file_name = "supplements/run_list_tb_sep_2017.csv"
    runLog = []
    
    with open(run_log_file_name, "rb") as file:
        fileData = csv.reader(file, delimiter=";")
        for row in fileData:
            runLog.append(row)

    del runLog[0:2]

    return runLog


# Define the original folder of produced ROOT files, plots and miscellaneous data
# This creates the main folder "folder_sensor_perfomance_tb_sep17" with all subfolders with names of
# sensors imported from the run log file.
def defineDataFolderPath():
    
    sourceFolder = "../folder_sensor_perfomance_tb_sep17/"
    folderInformationFile = "supplements/folderPaths.csv"
    paths = [sourceFolder]
  
    with open(folderInformationFile, "rb") as csvFile:
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            if row[1] == "":
                paths.append(sourceFolder+row[0])
            else:
                paths.append(sourceFolder+row[0]+";"+row[1])


    defMainDirectories(paths)
    
    exists = False

    try:
        os.mkdir(getSourceFolderPath())
        del paths[0]

    except:
        #print "\nFolder with subfolders for analysis already exists. Continuing with the code.\n"
        exists = True

    sensors = md.getAvailableSensors()

    if not exists:
        for filePath in paths:
            if filePath.find(";") == -1:
                os.mkdir(filePath)
            else:
                for chosenSensor in sensors:
                    p1 = filePath.replace(";",chosenSensor)
       
                    try:
                        os.mkdir(p1)

                    except:
                        p2 = filePath.split(";")[0]

                        for selectedSensor in sensors:
                            os.mkdir(p2+selectedSensor)

                        os.mkdir(p1)

    
        print "\nFolders with subfolders created. Placed at '../folder_sensor_perfomance_tb_sep17/' \n"


# Export pulse data
def exportPulseData(variable_array):
    
    [noise, pedestal, peak_values, rise_times, charge, cfd, peak_times, points, max_sample] = [i for i in variable_array]
    
    for index in range(0, len(var_names)):
        exportImportROOTData("pulse", var_names[index], variable_array[index])


# Export or import ROOT file
def exportImportROOTData(group, category, data=np.empty(0)):
    
    # This line is for exporting data and adapting correct dtype for the numpy array
    if group != "timing" and group != "results" and category != "position" and data.size != 0:
        data = data.astype(getDTYPE())

    if group == "tracking":
        
        if category == "tracking":
            fileName = category + md.getTimeStamp()
        
        elif category == "efficiency":
            fileName = category + "_" + str(md.getBatchNumber()) + "_" + md.getSensor() + "_" + md.chan_name

        else:
            fileName = category + "_" + str(md.getBatchNumber()/100)
    else:

        fileName = group + "_" + category + "_" + str(md.getRunNumber())


    dataPath = getSourceFolderPath() + getDataSourceFolder() + "/" + group + "/"

    if group == "results":
        dataPath += md.getSensor() + "/" + category + "/" + group+"_"+category+"_"+str(md.getBatchNumber()) + "_" + md.chan_name + ".root"

    else:
        dataPath += category + "/" + fileName + ".root"


    # read the file
    if data.size == 0:
        
        try:
            return rnm.root2array(dataPath)
        
        except IOError as e:
            
            print "\nFile", fileName+".root", "not found!\n"
            return np.zeros(1)

    # export the file
    else:
        rnm.array2root(data, dataPath, mode="recreate")


# Export or import ROOT histograms
def exportImportROOTHistogram(fileName, graphList = 0):

    rootDirectory = fileName.replace(getPlotsSourceFolder(), getHistogramsSourceFolder())
    rootDirectory = rootDirectory.replace(".pdf", ".root")
    
    if graphList != 0:
        
        fileObject = ROOT.TFile(rootDirectory, "RECREATE")
        graphList.Write()
        fileObject.Close()
        
    else:
        return ROOT.TFile(rootDirectory)


# Read file names which are enlisted in the folder
def readFileNames(group, category=""):
    
    if group == "oscilloscope":
        
        dataPath = getSourceFolderPath() + getOscillscopeSourceFolder() + "/"

    else:
        dataPath = getSourceFolderPath() + getDataSourceFolder() + "/" + group + "/" + category + "/"

    # This line reads in a list of sorted files
    # from a provided folder above, strips down non-integer characters and converts to integers.
    # The file is also checks if the file is readable and avoids .DS_Store-files typical for macOS.

    availableFiles = sorted([int(filter(lambda x: x.isdigit(), f)) for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath, f)) and f != '.DS_Store'])

    return availableFiles


def checkIfFileAvailable():

    found = False

    if functionAnalysis == "pulse_analysis" :
    
        files = readFileNames("oscilloscope")
        
        if int(md.getTimeStamp()) in files:
            found = True

    elif functionAnalysis == "timing_analysis":
    
        files_cfd = readFileNames("pulse", "cfd")
        files_peak_time = readFileNames("pulse", "peak_time")
    
        if int(md.getRunNumber()) in files_cfd and int(md.getRunNumber()) in files_peak_time:
            found = True
    

    elif functionAnalysis == "tracking_analysis":

        files_peak_value = readFileNames("pulse", "peak_value")
        files_tracking = readFileNames("tracking", "tracking")

        if int(md.getTimeStamp()) in files_tracking and int(md.getRunNumber()) in files_peak_value:

            found = True

    if not found:
        print "Files required for run number", md.getRunNumber(), "are missing. Skipping run.\n"

    return found


# Concatenate variables from multiprocessing
def concatenateResults(results):

    variable_array = []

    for variable_index in range(0, len(results[0])):
        
        variable = np.empty(0, dtype=results[0][variable_index].dtype)
        
        for clutch in range(0, len(results)):
        
            variable  = np.concatenate((variable, results[clutch][variable_index]), axis = 0)
        
        variable_array.append(variable)
    
        del variable

    return variable_array


def changeIndexNumpyArray(numpy_array, factor):

    for chan in numpy_array.dtype.names:
        numpy_array[chan] = np.multiply(numpy_array[chan], factor)


# This function changes the numpy data type to match the number of channels depending on batch.
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


def getDTYPETracking():
    
    return np.dtype( [('X', '<f4'), ('Y', '<f4')] )


def getDTYPETrackingPosition():

    return np.dtype([('chan0', '<f8', 2), ('chan1', '<f8', 2) ,('chan2', '<f8', 2) ,('chan3', '<f8', 2) ,('chan4', '<f8', 2) ,('chan5', '<f8', 2) ,('chan6', '<f8', 2) ,('chan7', '<f8', 2)])


# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])


def getDataSourceFolder():
    
    return dataSourceFolder


def getHistogramsSourceFolder():
    
    return histogramsSourceFolder


def getOscillscopeSourceFolder():
    
    return oscillscopeSourceFolder


def getPlotsSourceFolder():
    
    return plotsSourceFolder


def getResultsPlotSourceDataPath():
    
    
    return resultsPlotSourceDataPath

# Return path of data files
def getSourceFolderPath():
    
    return sourceFolderPath


def defMainDirectories(directories):
    
    global sourceFolderPath
    global dataSourceFolder
    global histogramsSourceFolder
    global oscillscopeSourceFolder
    global plotsSourceFolder
    global resultsPlotSourceDataPath
    
    sourceFolderPath = directories[0]
    dataSourceFolder = directories[1]
    histogramsSourceFolder = directories[2]
    oscillscopeSourceFolder = directories[3]
    plotsSourceFolder = directories[4]
    resultsPlotSourceDataPath = directories[5]



def setFunctionAnalysis(function):

    global functionAnalysis
    functionAnalysis = function


def getOscilloscopeFilePath():

    dataPath = getSourceFolderPath() + getOscillscopeSourceFolder() + "/" + "data_"+str(md.getTimeStamp())+".tree.root"

    return dataPath
