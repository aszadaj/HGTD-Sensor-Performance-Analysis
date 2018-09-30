import ROOT
import csv
import os

import data_management as dm


# Return run log imported from a .csv file
# For future .csv files, it is crucial that the run log have the same
# shape as the sep2017 one!
def getRunLog():
    
    tb_2017_run_log_file_name = "run_list_tb_sep_2017.csv"
    metaData = []
    
    with open(tb_2017_run_log_file_name, "rb") as csvFile:
        fileData = csv.reader(csvFile, delimiter=";")
        for row in fileData:
            metaData.append(row)

    del metaData[0:2]
  
    return metaData


# Set run information from the run log (gets the row with information).
# Plays a key role for all methods in the code.
def defineGlobalVariableRun(row):
    
    global runInfo
    runInfo = row


def getAllSensorNames():

    return ["50D-GBGR2", "W4-LG12", "W4-RD01", "W4-S203", "W4-S204_6e14",
    "W4-S215", "W4-S1022", "W4-S1061", "W9-LGA35"]

# Structure of runLog: [runLogBatch1, runLogBatch1, ...,] and
# runLogBatch1 = [run1, run2, run3, ]... run1 = row from the run log for selected run
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
def getAllRunNumbers(batchNumber=0):
    
    runLog = getRunLog()
    
    runNumbers = []
    
    for row in runLog:
        if int(row[5]) == batchNumber:
            runNumbers.append(int(row[3]))
        elif batchNumber == 0:
            runNumbers.append(int(row[3]))

    return runNumbers

# Return run numbers for given sensor
def getRunsWithSensor(sensor):
    
    if sensor == "":
        return getAllRunNumbers()
    
    runLog = getRunLog()
    
    runNumbers = []
    
    for row in runLog:
        if sensor in getAvailableSensorsForRun(int(row[3])):
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

    
# Get number of events inside the current ROOT file
def getNumberOfEvents():

    return int(runInfo[6])



# Get index for the name of the sensor in run log
def getChannelNameForSensor(sensor):

    for index in range(0,7):
        
        if runInfo[13+index*5] == sensor:
            return "chan"+str(index)

# Return name of sensor for chosen run and channel
def getNameOfSensor(chan):

    index = int(chan[-1:])
    return runInfo[13+index*5]

# Return sensors available for given run
def getAvailableSensorsForRun(runNumber):

    sensors = []

    for i in range(0,8):
        
        sensors.append(getRowForRunNumber(runNumber)[13+i*5])

    return sensors

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

# Return row in run log for given batch number
def getRowForBatchNumber(batchNumber):

    runLog = getRunLog()

    for row in runLog:
        if int(row[5]) == batchNumber:
            return row

def getFirstBatchNumberForSensor(sensor):

    runLog = getRunLog()

    for row in runLog:
        if sensor in row:
            return int(row[5])

def getAllBatchNumberForSensor(sensor):

    runLog = getRunLog()
    batchNumbers = []

    for row in runLog:
        if sensor in row:
            batch = int(row[5])
            if batch not in batchNumbers:
                batchNumbers.append(batch)

    return batchNumbers


def getTemperature():

    return int(runInfo[10])


def getAvailableTemperatures():

    return ["22", "-30", "-40"]


# This is a reference to Vagelis conference about SiPM-s RD50 Workshop in Krakow
# value in [ps]
def getSigmaSiPM():

    if getTemperature() < 0:
        return 9
    else:
        return 15


def getBiasVoltage(sensor, batchNumber):

    # This value is constant for the SiPMs across all batches
    if sensor == "SiPM-AFP":
        return 26.5
        
    runLogBatch = getRowForBatchNumber(batchNumber)
    index = runLogBatch.index(sensor)
    bias_voltage = int(runLogBatch[index+1])
    
    return bias_voltage


def checkIfArrayPad(chan):

    array_pad = False
    batchCategory = getBatchNumber()/100
    sensor = getNameOfSensor(chan)

    if sensor == "W4-S215" and batchCategory != 5 and batchCategory != 7:
        array_pad = True

    elif sensor == "W4-RD01":
        array_pad = True

    elif sensor == "W4-S204_6e14":
        array_pad = True

    return array_pad


# These are set values for each sensor. These values are determined between a plot for:
# Combined plot between maximum sample value and point above the threshold. In this way
# one can cut away pulses which are treated as noise

def getThresholdSamples(chan):

    sensor = getNameOfSensor(chan)

    if sensor == "50D-GBGR2" or sensor == "W9-LGA35":
        number_samples = 5
    
    elif sensor == "SiPM-AFP" or sensor == "W4-RD01":
        number_samples = 50

    elif sensor == "W4-LG12" or sensor == "W4-S203" or sensor == "W4-S215" or sensor == "W4-S1061":
        number_samples = 10

    elif sensor == "W4-S204_6e14":
        number_samples = 3

    elif sensor == "W4-S1022":
        number_samples = 7


    return number_samples


def getDUTPos(sensor, chan):
    
    if chan == "":
        return str(runInfo[runInfo.index(sensor)-1])
    
    else:
        return str(runInfo[12+int(chan[-1])*5])



def availableDUTPositions(sensor):

    if sensor == "W4-S215":
    
        return ["3_0", "3_1", "3_2", "3_3"]
    
    elif sensor == "W4-RD01":

        return ["8_1", "8_2"]
    
    elif sensor == "W4-S204_6e14":
    
        return ["7_0", "7_2", "7_3"]

    else:
        
        batch = getFirstBatchNumberForSensor(sensor)
        defineGlobalVariableRun(getRowForBatchNumber(batch))
   
        return getDUTPos(sensor, "")

# Selected runs which are marked with yellow color, probably
# have unsynchronized telescope numbers
def corruptedRuns():

    # Runs which are out of sync
    runs = [3691, 3693, 3697, 3701]

    return runs

# For main.py
def setBatchNumbers(numbers, exclude=[]):

    global batchNumbers
    
    if numbers == "all":
        numbers = getAllBatchNumbers()
        number_excluded = []

        if len(exclude) != 0:
            for index in range(0, len(numbers)):
                if numbers[index] not in exclude:
                    number_excluded.append(numbers[index])

            numbers = number_excluded

        batchNumbers = numbers
    
    else:
 
        batchNumbers = numbers



def setLimitRunNumbers(number):
    global limitRunNumbers
    limitRunNumbers = number


def setSensor(sensor_list):
    global sensor
    sensor = sensor_list


def defTimeScope():
    global dt
    dt = 0.1

def getTimeScope():
    return dt

def setChannelName(chan):

    global chan_name
    chan_name = chan


