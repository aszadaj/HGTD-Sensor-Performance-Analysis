import ROOT
import csv
import os

import data_management as dm


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
def restrictToBatch(metaData, batchNumber):
   
    runLog = []
    
    for index in range(0, len(metaData)):
        if int(metaData[index][5]) == batchNumber:
            runLog.append(metaData[index])
    
    return runLog


def getAllSensorNames():

    return ["50D-GBGR2", "SiPM-AFP", "W4-LG12", "W4-RD01", "W4-S203", "W4-S204_6e14", "W4-S215", "W4-S1022", "W4-S1061", "W9-LGA35"]



# Structure of results: [runLogBatch1, runLogBatch1, ...,] and runLogBatch1 = [run1, run2, run3, ]... run1 = row from the run log for selected run
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


# Check if the oscilloscope file is available
def isRootFileAvailable():

    availableFiles = readFileNames("oscilloscope")
    
    for file_name in availableFiles:
        if file_name == int(getTimeStamp()):
            return True

    return False

# Check if the pulse file for timing is available
def isTimingDataFilesAvailable():


    availableFilesPulse         = readFileNames("peak_value")
    found = False
    
    for pulse_file in availableFilesPulse:
        if pulse_file == int(getRunNumber()):
            return True

    return False

# Check if the tracking file is available
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


# Check if the noise file (noise = standard deviation) file is made
def isNoiseFileDone(runNumber):

    available = False

    availableFiles = readFileNames("noise_noise")
    
    if int(runNumber) in availableFiles:
        available = True
    
    return available


# Check if the pulse file (peak value) file is made
def isPulseFileDone(runNumber):

    available = False

    availableFiles = readFileNames("peak_value")

    if int(runNumber) in availableFiles:
        available = True
        
    return available


# Check if the timing resolution file is made
def isTimingFileDone(runNumber):

    available = False

    availableFiles = readFileNames("timing")

    if int(runNumber) in availableFiles:
        available = True
    
    return available


def checkIfSameOscAsSiPM(chan):

    SiPM_chan = getChannelNameForSensor("SiPM-AFP")
    
    chan_DUT = int(chan[-1])
    chan_SiPM = int(SiPM_chan[-1])
    
    if chan_DUT < 4 and chan_SiPM < 4:
        return True

    elif chan_DUT >= 4 and chan_SiPM >= 4:
        return True

    else:
        return False



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

    elif fileType == "timing": #timing_3656.root
        folderPath = "data_hgtd_efficiency_sep_2017/timing/"
        first_index = 7
        last_index = 11


    mainFolderPath = dm.getSourceFolderPath() + folderPath
    
    if dm.isOnHDD() and fileType == "oscilloscope":
    
        mainFolderPath = "/Volumes/HDD500/" + folderPath

    availableFiles = [int(f[first_index:last_index]) for f in os.listdir(mainFolderPath) if os.path.isfile(os.path.join(mainFolderPath, f)) and f != '.DS_Store']
    availableFiles.sort()

    return availableFiles


def getRunNumberForBatch(batchNumber):
    return getRunNumber(getTimeStampsForBatch(batchNumber)[0])


# Get current run number
def getRunNumber(timeStamp=""):
    
    if timeStamp == "":
        return int(runInfo[3])
    
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

# Get all time stamps for selected batch
def getTimeStampsForBatch(batchNumber):
    
    runLog = getRunLogBatches([batchNumber])
    timeStamps = []
    for row in runLog[0]:
        timeStamps.append(int(row[4]))
    
    return timeStamps

def getNumberOfRunsPerBatch():

    return len(getTimeStampsForBatch(int(runInfo[5])))


# Get number of events inside the current ROOT file
def getNumberOfEvents(timeStamp=""):
    
    if timeStamp == "":
        return int(runInfo[6])
    
    else:
        runLog = getRunLog()

        for row in runLog:
            if int(row[4]) == timeStamp:
                return int(row[6])

# Get the voltage value which cuts the amplitude (to restrict from noise furthermore).
# Value in negative voltage [-V].
def getPulseAmplitudeCut(chan):

    cut = 0

    if getNameOfSensor(chan) == "SiPM-AFP":
        cut = -0.2

    return cut



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

# Return row in run log for given run number
def getRowForBatchNumber(batchNumber):

    runLog = getRunLog()

    for row in runLog:
        if int(row[5]) == batchNumber:
            return row

def getTemperature():

    return int(runInfo[10])



def getBiasVoltage(sensor):

    if sensor == "SiPM-AFP":
        return "26.5"

    index = runInfo.index(sensor)
    bias_voltage = runInfo[index+1]

    return int(runInfo[index+1])


def checkIfArrayPad(chan="chan5"):

    if getNameOfSensor(chan) == "W4-S204_6e14":

        return True

    elif getNameOfSensor(chan) == "W4-S215":
        
        batchIndex = getBatchNumber()/100
        
        if batchIndex == 1 or batchIndex == 2 or batchIndex == 4:
        
            return True

    else:
    
        return False

def getDUTPos(sensor, chan):

    return str(runInfo[12+int(chan[-1])*5])


def availableDUTPos(sensor, chan=""):

    if sensor == "W4-S215":
    
        return ["3_0", "3_1", "3_2", "3_3"]
    
    elif sensor == "W4-RD01":

        return ["8_1", "8_2"]
    
    elif sensor == "W4-S204_6e14":
    
        return ["7_0", "7_2", "7_3"]

    elif chan=="":
    
        return 1

    else:

        return getDUTPos(sensor, chan)



# Set run info for selected run
def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row


def setBatchNumbers(numbers, exclude=[]):

    global batchNumbers
    
    if numbers == "all" and len(exclude) == 0:
        numbers = getAllBatchNumbers()

    elif numbers == "all":
        numbers = getAllBatchNumbers()
        number_excluded = []

        for index in range(0, len(numbers)):
            if numbers[index] not in exclude:
                number_excluded.append(numbers[index])

        numbers = number_excluded

                
    batchNumbers = numbers



def setLimitRunNumbers(number):
    global limitRunNumbers
    limitRunNumbers = number


def setEntriesForQuickAnalysis(value):
    global maxEntries
    maxEntries = value
