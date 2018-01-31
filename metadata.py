
import ROOT
import csv
import os
import datetime as dt


########## METADATA ##########

# Return run log imported from a .csv file
def getRunLog():
    
    tb_2017_run_log_file_name = "resources/run_list_tb_sep_2017.csv"
    metaData = []
    
    with open(tb_2017_run_log_file_name, "rb") as csvFile:
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            metaData.append(row)

    del metaData[0]
    return metaData


# Check inside folder which runs should be considered
def restrictToBatch(metaData, batchNumber):
   
    runLog = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][5]) == batchNumber:
            runLog.append(metaData[index])
    
    return runLog


# Structure of results: [runLogbatch1, runlogbacth2, ...,] and runLogBacth1 = [run1, run2, run3, ]... run1 = info about the run, as usual.
def getRunLogBatches(batchNumbers):

    if batchNumbers == "all":
        batchNumbers = getAllBatchNumbers()

    metaData = getRunLog()
 
    runLog = []
    
    for batch in batchNumbers:
        runLog_batch = []
        
        for row in metaData:
            
            if batch == int(row[5]):
                runLog_batch.append(row)
                
        runLog.append(runLog_batch)

    return runLog



def isRootFileAvailable():

    availableFiles = readFileNames("oscilloscope")
    
    for file_name in availableFiles:
        if file_name == int(getTimeStamp()):
            return True

    return False


def isTimingDataFilesAvailable():


    availableFilesPulse         = readFileNames("peak_value")
    found = False
    
    for pulse_file in availableFilesPulse:
        if pulse_file == int(getRunNumber()):
            return True

    return False


def isTrackingFileAvailable():


    availableFilesPulse         = readFileNames("peak_value")
    availableFilesTracking     = readFileNames("tracking")

    found = False
    
    for pulse_file in availableFilesPulse:
        if pulse_file == int(getRunNumber()):
            for tracking_file in availableFilesTracking:
                if tracking_file == int(getTimeStamp()):
                    return True

    return False


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

    elif fileType == "oscilloscope": #data_1504949898.tree.root
        folderPath = "oscilloscope_data_sep_2017/"
        first_index = 5
        last_index = 15

    elif fileType == "noise_noise": #noise_noise_3791.root
        folderPath = "data_hgtd_efficiency_sep_2017/noise/noise_noise/"
        first_index = 12
        last_index = 16

    elif fileType == "noise_pedestal": #noise_pedestal_3791.root
        folderPath = "data_hgtd_efficiency_sep_2017/noise/noise_pedestal/"
        first_index = 15
        last_index = 19

    elif fileType == "pulse_peak_time": #pulse_peak_time_3791.root
        folderPath = "data_hgtd_efficiency_sep_2017/pulse/pulse_peak_time/"
        first_index = 16
        last_index = 20

    elif fileType == "pulse_peak_value": #pulse_peak_value_3791.root
        folderPath = "data_hgtd_efficiency_sep_2017/pulse/pulse_peak_value/"
        first_index = 17
        last_index = 21

    elif fileType == "pulse_rise_time": #pulse_rise_time_3791.root
        folderPath = "data_hgtd_efficiency_sep_2017/pulse/pulse_rise_time/"
        first_index = 16
        last_index = 20

    
    folderPath = getSourceFolderPath() + folderPath

    availableFiles = [int(f[first_index:last_index]) for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles



# Define folder where the pickle files should be
def defineDataFolderPath(source):

    global sourceFolderPath
    sourceFolderPath = source


# Return path of data files
def getSourceFolderPath():

    return sourceFolderPath


# Get current run number
def getRunNumber(timeStamp=""):
    
    if timeStamp == "":
        return runInfo[3]
    
    else:
        runLog = getRunLog()

        for row in runLog:
            if int(row[4]) == timeStamp:
                return int(row[3])

# Return all run numbers for given batch

def getAllRunNumbers(batchNumber):

    runLog = getRunLog()
    
    runNumbers = []
    
    for row in runLog:
        if int(row[5]) == batchNumber:
            runNumbers.append(int(row[3]))

    return runNumbers


# Get current time stamp (which corresponds to the run number)
def getTimeStamp(runNumber=""):
    
    if runNumber == "":
        return runInfo[4]

    else:
        runLog = getRunLog()

        for row in runLog:
            if int(row[3]) == runNumber:
                return int(row[4])


def getTimeStampsForBatch(batchNumber):

    runLog = getRunLogBatches([batchNumber])

    timeStamps = []
    for row in runLog[0]:
        timeStamps.append(int(row[4]))
    
    return timeStamps


# Get number of events inside the current ROOT file
def getNumberOfEvents(timeStamp=""):
    
    if timeStamp == "":
        return int(runInfo[6])
    
    else:
        runLog = getRunLog()

        for row in runLog:
            if int(row[4]) == timeStamp:
                return int(row[6])

# Get index for the name of the sensor in run log
def getChannelNameForSensor(sensor):

    for index in range(0,7):
        
        if runInfo[13+index*5] == sensor:
            return "chan"+str(index)


# Return name of sensor for chosen run and channel
def getNameOfSensor(chan):

    index = int(chan[-1:])
    return runInfo[13+index*5]


# Return batch number
def getBatchNumber(runNumber=""):

    if runNumber != "":
        runLog = getRunLog()
        for row in runLog:
            if int(row[3]) == runNumber:
                return int(row[5])
    else:
        return int(runInfo[5])


def getAllBatchNumbers():

    metaData = getRunLog()
    batchNumbers = [int(metaData[0][5])]
    
    for row in metaData:
        if int(row[5]) not in batchNumbers:
            batchNumbers.append(int(row[5]))

    return batchNumbers


# Return row in run log for given run number
def getRowForRunNumber(runNumber):

    runLog = getRunLog()

    for row in runLog:
        if int(row[3]) == runNumber:
            return row

# Set run info for selected run
def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row


# Get actual time
def getTime():

    return dt.datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(dt.datetime.now().time())
    print  "\nTime: " + str(time[:-7])


# Function for setting up ATLAS style plots
def setupATLAS():

    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("./resources/style/AtlasStyle.C")
    ROOT.SetAtlasStyle()

def setLimitRunNumbers(number):
    global limitRunNumbers
    limitRunNumbers = number

def setQuickParameter(debug):
    global quick
    quick = debug

def setEntriesForQuickAnalysis(value):
    global maxEntries
    maxEntries = value


def setSigma(value):
    global sigma
    sigma = value





