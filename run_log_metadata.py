# This file handles information from the run log.

import data_management as dm


def defineSettings(batches, batches_exclude, number, sensor_name):
    
    dm.printTime()
    
    global sensor
    global limitRunNumbers
    
    sensor = sensor_name
    limitRunNumbers = number
    
    setBatchNumbers(batches, batches_exclude)

    dm.defineDataFolderPath()


# For main.py
def setBatchNumbers(numbers, exclude=[]):
    
    global batchNumbers
    
    if numbers == "all":
        numbers = getAllBatchNumbers()
        number_included = []
        
        if len(exclude) != 0:
            for index in range(0, len(numbers)):
                if numbers[index] not in exclude:
                    number_included.append(numbers[index])
    
            numbers = number_included
        
        elif sensor != "":
            for index in range(0, len(numbers)):
                
                if numbers[index] in getAllBatchNumberForSensor(sensor):
                    number_included.append(numbers[index])

            numbers = number_included
        
        batchNumbers = numbers

    else:
    
        batchNumbers = numbers



# Set run information from the run log (gets the row with information).
# Plays a key role for all functions in the code.
def defineRunInfo(row):
    
    global runInfo
    runInfo = row


# Return row in run log for given run number
def getRowForRunNumber(runNumber):
    
    runLog = dm.getRunLog()
    
    for row in runLog:
        if int(row[3]) == runNumber:
            return row

# This is the value which is taken from the TB paper (2018)
def getChargeWithoutGainLayer():

    return 0.46


# Structure of runLog: [runLogBatch1, runLogBatch1, ...,] and
# runLogBatch1 = [run1, run2, run3, ]... run1 = row from the run log for selected run
def getRunLogBatches(batchNumbers):

    if batchNumbers == "all":
        batchNumbers = getAllBatchNumbers()

    runLog = dm.getRunLog()

    runLog_parts = []

    for batch in batchNumbers:
        runLog_batch = []

        for row in runLog:

            if batch == int(row[5]):
                runLog_batch.append(row)

        runLog_parts.append(runLog_batch)

    return runLog_parts

# Checks if the SiPM is in different oscilloscope. Note that this is adapted for only one SiPM!
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



def getOscText():

    if checkIfSameOscAsSiPM(chan_name):

        return "same_osc"

    else:
        return "diff_osc"


# Get current run number
def getRunNumber():
    
    return int(runInfo[3])



# Return all run numbers for given batch
def getAllRunNumbers(batchNumber=0):
    
    runLog = dm.getRunLog()
    
    runNumbers = []
    
    for row in runLog:
        
        if int(row[5]) == batchNumber:
            runNumbers.append(int(row[3]))
        
        elif batchNumber == 0:
            runNumbers.append(int(row[3]))

    return runNumbers


# Return run numbers for given sensor
def getRunsWithSensor(sensor=""):
    
    if sensor == "":
        return getAllRunNumbers()
    
    runLog = dm.getRunLog()
    
    runNumbers = []
    
    for row in runLog:
        if sensor in row:
            if int(row[3]) not in runNumbers:
                runNumbers.append(int(row[3]))


    return runNumbers


# Get current time stamp (which corresponds to the run number)
def getTimeStamp():
    
    return runInfo[4]


# Get number of events inside the current ROOT file
def getNumberOfEvents():

    return int(runInfo[6])


# Get index for the name of the sensor in run log
def getChannelNameForSensor(sensor):

    for index in range(0,7):
        
        if runInfo[13+index*5] == sensor:
            return "chan"+str(index)


# Return name of sensor for chosen run and channel
def getSensor(chan=""):
    
    if chan != "":
        return runInfo[13+int(chan[-1:])*5]
    else:
    
        return runInfo[13+int(getChanName()[-1:])*5]


# Return sensors available for given run/batch (each run have same sensors for same batch)
def getSensorsForBatch(batchNumber=0):

    runNumber = getRunNumber()
    
    sensors = []

    for i in range(0,8):
        
        sensors.append(getRowForRunNumber(runNumber)[13+i*5])

    return sensors


def getBatchNumber(runNumber=""):

    if runNumber != "":
        runLog = dm.getRunLog()
        for row in runLog:
            if int(row[3]) == runNumber:
                return int(row[5])

    else:
        return int(runInfo[5])


def getAllBatchNumbers():

    runLog = dm.getRunLog()
    batchNumbers = [int(runLog[0][5])]
    
    for row in runLog:
        if int(row[5]) not in batchNumbers:
            batchNumbers.append(int(row[5]))

    return batchNumbers



def getAllBatchNumberForSensor(sensor):

    runLog = dm.getRunLog()
    batchNumbers = []

    for row in runLog:
        if sensor in row:
            batch = int(row[5])
            if batch not in batchNumbers:
                batchNumbers.append(batch)

    return batchNumbers



def getAllChannelsForSensor(batch, sensor):
    
    runLog = dm.getRunLog()
    
    channels = []
    
    for row in runLog:
        if int(row[5]) == batch:
            
            for index in range(0,7):
                
                if row[13+index*5] == sensor and "chan"+str(index) not in channels:
                    channels.append("chan"+str(index))


    return channels


def getTemperature():

    return int(runInfo[10])


# Get available sensors from the run file
def getAvailableSensors():

    runLog = dm.getRunLog()

    availableSensors = []

    for row in runLog:
        for i in range(0,8):
            if row[13+i*5] not in availableSensors and len(row[13+i*5]) > 2:
                availableSensors.append(row[13+i*5])

    return availableSensors


def getAvailableTemperatures():
    
    runLog = dm.getRunLog()
    temperatures = []
    
    for row in runLog:
        if row[10] not in temperatures:
            temperatures.append(row[10])

    return temperatures


# Reference: RD50 Workshop in Krakow (2017), E.L. Vagelis
# value in [ps]
def getSigmaSiPM():

    if getTemperature() < 0:
        return 9
    else:
        return 15


def getBiasVoltage():
    
    return float(runInfo[14+int(getChanName()[-1])*5])


def checkIfArrayPad():

    array_pad = False
    batchCategory = getBatchNumber()/100
    sensor = getSensor()

    if sensor == "W4-S215" and batchCategory != 5 and batchCategory != 7:
        array_pad = True

    elif sensor == "W4-RD01":
        array_pad = True

    elif sensor == "W4-S204_6e14":
        array_pad = True

    return array_pad


def getDUTPos():
   
    return str(runInfo[12+int(getChanName()[-1])*5])


def setChannelName(chan):

    global chan_name
    chan_name = chan


def getChanName():

    return chan_name
