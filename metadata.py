
import csv
from os import listdir
from os.path import isfile, join

import analysis as an


########## METADATA ##########

# Return run log imported from a .csv file
def getRunLog():
    
    tb_2017_run_log_file_name = "resources/run_list_tb_sep_2017.csv"
    metaData = []
    
    with open(tb_2017_run_log_file_name, "rb") as csvFile:
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            metaData.append(row)

    del metaData[0:2]
 
    return metaData


# Check inside folder which runs should be considered
def restrictToUndoneRuns(metaData):
    
    folderPath = "data_hgtd_efficiency_sep_2017/noise_files/noise_data/"
    availableFiles = readFileNames(folderPath, "pickle")

    runLog = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][3]) not in availableFiles:
            runLog.append(metaData[index])
    
    return runLog


# Restrict runs for telescope analysis for available files
def getRunLogForTelescopeAnalysis(metaData, numberOfBatches, numberOfRunsPerBatch):

    folderPath = "forAntek/"
    availableTimeStamps = readFileNames(folderPath, "telescope")
    
    runLog = []
    actualBatch = 0
    firstBatch = True
    numberOfRuns = numberOfRunsPerBatch
    
    for index in range(0, len(metaData)):
    
        if numberOfBatches == 0:
            break
    
        elif int(metaData[index][4]) in availableTimeStamps:
        
            currentBatch = int(metaData[index][5])
            
            if firstBatch:
                actualBatch = currentBatch
                firstBatch = False
        
            if numberOfRuns != 0:
                runLog.append(metaData[index])
                numberOfRuns -= 1
            
            if actualBatch != currentBatch:
                numberOfBatches -= 1
                actualBatch = currentBatch
                numberOfRuns = numberOfRunsPerBatch

    return runLog

    
# Check if repository is on the stau server
def isRootFileAvailable(timeStamp):

    folderPath = "oscilloscope_data_sep_2017/"
    availableFiles = readFileNames(folderPath, "")
    
    found = False
    
    for file_name in availableFiles:
        if file_name == int(timeStamp):
            found = True
            break

    return found

# DEBUG
def listAvailableFiles(runLog):

    folderPath = "oscilloscope_data_sep_2017/"
    availableFiles = readFileNames(folderPath, "")
    
    found = False
  
    for row in runLog:
        if int(row[4]) not in availableFiles:
            print row[3]


# Define folder where the pickle files should be
def defineDataFolderPath():

    global sourceFolderPath
    sourceFolderPath =  "../../HGTD_material/"
    
    # define the place of the export data
    if an.checkIfRepositoryOnStau():
        sourceFolderPath = "/home/warehouse/aszadaj/HGTD_material/"


def readFileNames(folderPath, fileType):
    
    if fileType == "telescope":
        first_index = 8
        last_index = 18
    
    elif fileType == "pickle":
        first_index = 11
        last_index = 15

    else:
        first_index = 5
        last_index = -10

    folderPath = getSourceFolderPath() + folderPath
    availableFiles = [int(f[first_index:last_index]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles

# Return run numbers for telescope analysis

def getRunNumberTelescope2(timeStamp,runLog):
    runNumber = 0
    for row in runLog:
        if row[4] == timeStamp:
            runNumber = row[3]
            break
    
    return int(runNumber)


# Get current run number
def getRunNumber():
    
    return runInfo[3]


# Get current time stamp (which corresponds to the run number)
def getTimeStamp():
    
    return runInfo[4]


# Get number of events inside the current ROOT file
def getNumberOfEvents():
    
    return int(runInfo[6])


# Return name of sensor for chosen run and channel
def getNameOfSensor(chan):

    index = int(chan[-1:])
    return runInfo[13+index*5]


# Return batch number
def getBatchNumber():

    return int(runInfo[5])


#def getBatchNumbers(runLog):
#
#    batchNumbers = [int(runLog[0][5])]
#
#    for row in runLog:
#        if int(row[5]) not in batchNumbers:
#            batchNumbers.append(int(row[5]))
#
#    return batchNumbers

#def getRunLogForBatch(runLog, batch):
#
#    newRunLog = []
#
#    for row in runLog:
#        if int(row[5]) == batch:
#            newRunLog.append(row)
#
#    return newRunLog



# Return path of data files
def getSourceFolderPath():
    return sourceFolderPath


# Set run info for selected run
def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row

