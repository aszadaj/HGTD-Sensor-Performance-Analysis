
import csv
from os import listdir
from os.path import isfile, join


########## METADATA ##########


def getRunLog():
    
    tb_2017_run_log_file_name = "run_list_tb_sep_2017.csv"
    
    # returns array of unproduced files (if available in folder resources)
    runLog = createRunLogArray(tb_2017_run_log_file_name)
 
    return runLog


def createRunLogArray(fileName):

    metaData = []

    with open(fileName, "rb") as csvFile:
       
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            metaData.append(row)

    del metaData[0:2]

    return metaData


def restrictToUndoneRuns(metaData):
    
    folderPath = "../../resources/"
    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    
    availableFiles.sort()
    del availableFiles[0]
    del availableFiles[0:(len(availableFiles)/2)]
   
    availableRunNumber = []
    
    for file in availableFiles:
        availableRunNumber.append(int(file[11:15]))
    
    for runNumber in availableRunNumber:
        for index in range(0,len(metaData)):
            if int(metaData[index][3]) == runNumber:
                del metaData[index]
                break

    return metaData


def getOscilloscopeMetaData(fileName):
    
    metaData = []
    
    with open(fileName, "rb") as csvFile:
        
        fileData = csv.reader(csvFile)
        for row in fileData:
            metaData.append(row)
    
    return metaData


def getRunsForTelescopeAnalysis(runLog):

    folderPath = "../../HGTD_material/telescope_data_sep_2017/"
    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    availableFiles.sort()
    
    if '.DS_Store' in availableFiles:
        del availableFiles[0]

    telescope_runNumbers = []

    for file_name in availableFiles:
        telescope_timeStamp = file_name[8:-5]
        foundRun = getRunNumberTelescope(telescope_timeStamp, runLog)
        
        if int(foundRun) != 0:
            telescope_runNumbers.append(foundRun)
    
    telescope_runNumbers.sort()

    print "telescope run number available: " + str(len(telescope_runNumbers))
    print telescope_runNumbers

    return runLog, telescope_runNumbers


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


def getTimeScope():

    metaDataFileName = "../../HGTD_material/oscilloscope_data_sep_2017/csv/data_"+str(getTimeStamp())+".csv"
    metaData = getOscilloscopeMetaData(metaDataFileName)
    timeScope = float(metaData[0][4])*float("1E+09")
   
    return timeScope


def getSensorNames():

    sensors = []

    for i in range(13,49,5):
        sensors.append(runInfo[i])
    
    return sensors


def isRootFileAvailable(timeStamp):

    folderPath = "../../HGTD_material/oscilloscope_data_sep_2017/"
    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    availableFiles.sort()
    
    found = False

    for file_name in availableFiles:
        if str(file_name[0]) != "." and int(file_name[5:-10]) == int(timeStamp):
            found = True
            break
    return found



def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row

