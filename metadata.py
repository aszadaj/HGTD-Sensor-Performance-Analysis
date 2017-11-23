
import csv
from os import listdir
from os.path import isfile, join


########## METADATA ##########

# Return run log imported from a .csv file
def getRunLog():
    
    tb_2017_run_log_file_name = "resources/run_list_tb_sep_2017.csv"
    metaData = []
    
    # returns array of unproduced files (if available in folder ../../HGTD_material/data_hgtd_efficiency_sep_2017)
    
    with open(tb_2017_run_log_file_name, "rb") as csvFile:
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            metaData.append(row)

    del metaData[0:2]
 
    return metaData

# Check inside folder which runs should be considered
def restrictToUndoneRuns(metaData):
    
    folderPath = getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/noise_files/noise_data"
    availableFiles = [int(f[11:15]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    
    runLog = []

    for index in range(0, len(metaData)):
        if int(metaData[index][3]) not in availableFiles:
            runLog.append(metaData[index])
    
    return runLog


# Restrict runs for telescope analysis for available files
def getRunsForTelescopeAnalysis(metaData):

    folderPath = getSourceFolderPath() + "forAntek/"
    
    availableTimeStamps = [int(f[8:18]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    availableTimeStamps.sort()
    
    runLog = []
    runNumbers = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][4]) in availableTimeStamps:
            runLog.append(metaData[index])

    # Check for telescope files
    folderPath = getSourceFolderPath() + "data_hgtd_efficiency_sep_2017/pulse_files/pulse_data"

    availableRunNumbers = [int(f[11:15]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    availableRunNumbers.sort()

    runLog2 = []
    
    for index in range(0, len(runLog)):
        if int(runLog[index][3]) in availableRunNumbers:
            runLog2.append(runLog[index])
            runNumbers.append(int(metaData[index][3]))

    return runLog2, runNumbers

# Return run numbers for telescope analysis
def getRunNumberTelescope(timeStamp,runLog):
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


def getSensorNames():

    sensors = []

    for i in range(13,49,5):
        sensors.append(runInfo[i])
    
    return sensors


def isRootFileAvailable(timeStamp, folderPath):

    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    availableFiles.sort()
    
    found = False

    for file_name in availableFiles:
        if str(file_name[0]) != "." and int(file_name[5:-10]) == int(timeStamp):
            found = True
            break

    return found


def defineFolderPath(path):
    global sourceFolderPath
    sourceFolderPath = path

def getSourceFolderPath():
    return sourceFolderPath


def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row

