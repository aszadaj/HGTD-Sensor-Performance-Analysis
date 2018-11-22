import ROOT
import numpy as np
import root_numpy as rnm
import os
import csv
import datetime as dt
import pulse_plot
import tracking_calculations as t_calc

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

    try:
        os.mkdir(getSourceFolderPath())
        del paths[0]

    except:
        return 0

    sensors = md.getAvailableSensors()

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


# Export or import ROOT file
def exportImportROOTData(group, category, data=np.empty(0)):
    
    dataPath = getDataSourceFolder() + "/" + group + "/"
    
    
    # This line is for exporting data and adapting correct dtype for the numpy array
    if group != "timing" and group != "results" and category != "position" and data.size != 0:
        data = data.astype(getDTYPE())

    if group == "tracking":
        
        if category == "tracking":
            fileName = category + str(md.getTimeStamp())
        
        elif category == "efficiency":
            fileName = category + "_" + str(md.getBatchNumber()) + "_" + md.getSensor() + "_" + md.chan_name

        # Position
        else:
            fileName = category + "_" + str(md.getBatchNumber()/100)

        dataPath += category + "/" + fileName + ".root"

    elif group == "timing":
        
        category, subcategory = category.split("_")
        
        fileName = group + "_" + category + "_" + subcategory + "_" + str(md.getRunNumber())
        
        dataPath += category + "/" + subcategory + "/" + fileName + ".root"

    else:
        
        fileName = group + "_" + category + "_" + str(md.getRunNumber())
        
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


def checkIfROOTDataFileExists(group, category):
    
    check = exportImportROOTData(group, category)
    
    if np.count_nonzero(check) > 0:
        check = True
    
    return check


# Export or import ROOT histograms
def exportImportROOTHistogram(group, category, subcategory="", chan2="", graphList = 0):
  
    fileName = getFileNameForHistogram(group, category, subcategory, chan2)
    fileName = fileName.replace(getPlotsSourceFolder(), getHistogramsSourceFolder())
    fileName = fileName.replace(".pdf", ".root")
    
    if graphList != 0:
        
        fileObject = ROOT.TFile(fileName, "RECREATE")
        graphList.Write()
        fileObject.Close()
        
    else:
        th_name = "_" + str(md.getBatchNumber()) + "_" + md.chan_name
        objectName = category + th_name
        
        if subcategory != "":
            objectName = category + "_" + subcategory + th_name
        
        if chan2 != "":
            objectName += "_" + chan2
    
    
        exists = os.path.isfile(fileName)
    
        if exists:
            fileObject = ROOT.TFile(fileName)
            histogram = fileObject.Get(objectName)
            
            histogram.SetDirectory(0) # Disconnect the ownership of the TFile object from the imported TH-object
            fileObject.Close()
            return histogram

        else:
            print fileName, "does not exist!\n"
            return exists



# only for pulse and timing
def getFileNameForHistogram(group, category, subcategory="", chan2=""):
    
    # pulse all types
    fileName = getPlotsSourceFolder() + "/" + md.getSensor() + "/" + group + "/" + category + "/" + group + "_" + category + "_" + str(md.getBatchNumber())+ "_" + md.chan_name
    ending = "_"+md.getSensor()+".pdf"
    
    
    # timing resolution
    if subcategory != "":
     
        if md.checkIfSameOscAsSiPM():
            
            getOscText = "same_osc"

        else:
            getOscText = "diff_osc"
        
        # timing normal
        fileName = fileName.replace(category + "/", category + "/" + subcategory + "/", 1)
        ending = "_" + md.getSensor() + "_" + getOscText + "_" + subcategory + ".pdf"
        
        # sys eq
        if chan2 != "":
            ending = "_" + md.getSensor() + "_and_" + md.getSensor(chan2) + "_" + subcategory + ".pdf"

    # For array-pad tracking plots
    if group == "tracking" and t_calc.array_pad_export:
        ending = ending.replace(".pdf", "_array.pdf")

    return fileName+ending



def getOscilloscopeData(first_event, last_event):
    
    dataPath = getOscillscopeSourceFolder() + "/" + "data_"+str(md.getTimeStamp())+".tree.root"

    return rnm.root2array(dataPath, start=first_event, stop=last_event)



# Read file names which are enlisted in the folder
def readFileNames(group, category=""):
    
    if group == "oscilloscope":
        
        dataPath = getOscillscopeSourceFolder() + "/"

    else:
        dataPath = getDataSourceFolder() + "/" + group + "/" + category + "/"

    # This line reads in a list of sorted files
    # from a provided folder above, strips down non-integer characters and converts to integers.
    # The file is also checks if the file is readable and avoids .DS_Store-files typical for macOS.

    availableFiles = sorted([int(filter(lambda x: x.isdigit(), f)) for f in os.listdir(dataPath) if os.path.isfile(os.path.join(dataPath, f)) and f != '.DS_Store'])

    return availableFiles


def checkIfFileAvailable(analysis):

    found = False

    if analysis == "pulse" and md.getTimeStamp() in readFileNames("oscilloscope"):
            
        found = True

    if analysis == "timing" and md.getRunNumber() in readFileNames("pulse", "cfd") and md.getRunNumber() in readFileNames("pulse", "peak_time"):
            
        found = True

    if analysis == "tracking" and md.getTimeStamp() in readFileNames("tracking", "tracking") and md.getRunNumber() in readFileNames("pulse", "pulse_amplitude"):

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
# This is adapted for TB Sep 2017
def getDTYPE(batchNumber = 0):
    
    if batchNumber == 0:
        batchNumber = md.getBatchNumber()
    
    # Batch 60X have 3 channels
    if batchNumber/100 == 6:
    
        dtype = np.dtype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ] )
    
    # Batch 30X have 7 channels
    elif batchNumber/100 == 3:
    
        dtype = np.dtype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ] )
    
    # Remaining batches have 8 channels
    else:
    
        dtype = np.dtype(  [('chan0', '<f8'), ('chan1', '<f8') ,('chan2', '<f8') ,('chan3', '<f8') ,('chan4', '<f8') ,('chan5', '<f8') ,('chan6', '<f8') ,('chan7', '<f8')] )

    return dtype


# This is a dtype for a numpy array, set for a name for each channel
# and a three dimensional array for each channel.
def getDTYPESysEq():
    
    return ([('chan0','<f8',(1,3)), ('chan1','<f8',(1,3)) ,('chan2','<f8',(1,3)) ,('chan3','<f8',(1,3))])

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

