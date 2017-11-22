
import csv
from os import listdir
from os.path import isfile, join


########## METADATA ##########


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


def restrictToUndoneRuns(metaData):
    
    folderPath = "../../HGTD_material/data_hgtd_efficiency_sep_2017/noise_files/noise_data" #noise_data_####
    availableFiles = [int(f[11:15]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    
    runLog = []

    for index in range(0, len(metaData)):
        if int(metaData[index][3]) not in availableFiles:
            runLog.append(metaData[index])
    
    return runLog

def considerOnlyRuns(runs, metaData):
  
    runLog = []
    
    for row in metaData:
        if int(row[3]) in runs:
            runLog.append(row)

    return runLog


# Here check how the run log is read
def getRunsForTelescopeAnalysis(metaData):
    # Check for already produced pickle files
    folderPath = "../../HGTD_material/forAntek/" #tracking1504949898.root
    
    availableTimeStamps = [int(f[8:18]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    availableTimeStamps.sort()
    
    runLog = []
    runNumbers = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][4]) in availableTimeStamps:
            runLog.append(metaData[index])

    # Check for telescope files
    folderPath = "../../HGTD_material/data_hgtd_efficiency_sep_2017/pulse_files/pulse_data" #pulse_data_3656.pkl

    availableRunNumbers = [int(f[11:15]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    availableRunNumbers.sort()

    runLog2 = []
    
    for index in range(0, len(runLog)):
        if int(runLog[index][3]) in availableRunNumbers:
            runLog2.append(runLog[index])
            runNumbers.append(int(metaData[index][3]))


    return runLog2, runNumbers


def getRunNumberTelescope(timeStamp,runLog):
    runNumber = 0
    for row in runLog:
        if row[4] == timeStamp:
            runNumber = row[3]
            break
    
    return int(runNumber)


def getRunNumber():
    
    return runInfo[3]


def getTimeStamp():
    
    return runInfo[4]


def getNumberOfEvents():
    
    return int(runInfo[6])


def getSensorNames():

    sensors = []

    for i in range(13,49,5):
        sensors.append(runInfo[i])
    
    return sensors


def isRootFileAvailable(timeStamp):

    folderPath = "../../HGTD_material/oscilloscope_data_sep_2017/"
    folderPath = "/Volumes/500 1"
    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    availableFiles.sort()
    
    found = False

    for file_name in availableFiles:
        if str(file_name[0]) != "." and int(file_name[5:-10]) == int(timeStamp):
            found = True
            break

    folderPath = "../../HGTD_material/oscilloscope_data_sep_2017/"
    
    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    availableFiles.sort()

    for file_name in availableFiles:
        if str(file_name[0]) != "." and int(file_name[5:-10]) == int(timeStamp):
            found = True
            break

    return found



def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row

