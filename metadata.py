
import csv
from os import listdir
from os.path import isfile, join



########## METADATA ##########


def getRunLog(numberOfRuns, last_entry):
    
    tb_2017_run_log_file_name = "/Users/aszadaj/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/run_list_tb_sep_2017.csv"
    
    runLog, last_index = createRunLogArray(tb_2017_run_log_file_name,";", last_entry)
    
    del runLog[0:last_index]
    skip = 0
    notSupportedRuns = [3691,3693,3697,3698,3701,3743,3745,3786,3796,3850,3892,3916,3980]
    
    # NOTE! Earlier the code deletes the rows which are already done, last_index
    #notSupportedRuns.append(getRunNumberTelescope(runLog))
    #notSupportedRuns.sort() # comment this too
    
    for i in [index for index, row in enumerate(runLog) if int(runLog[index][3]) in notSupportedRuns]:
        del runLog[i-skip]
        skip+=1

    return runLog[0:numberOfRuns]


def createRunLogArray(fileName,delimiter, last_entry):

    
    metaData = []

    with open(fileName, "rb") as csvFile:
       
        fileData = csv.reader(csvFile, delimiter=delimiter)
        for row in fileData:
            metaData.append(row)


    for index in range(0,len(metaData)):
        try:
            if last_entry == int(metaData[index][3]):
                last_index = index
                break
        except:
            continue
    
    return metaData, last_index


def getOscilloscopeMetaData(fileName):
    
    metaData = []
    
    with open(fileName, "rb") as csvFile:
        
        fileData = csv.reader(csvFile)
        for row in fileData:
            metaData.append(row)
    
    return metaData


def getRunsForTelescopeAnalysis(runLog):

    folderPath = "/Users/aszadaj/cernbox/SH203X/HGTD_material/telescope_data_sep_2017/"
    availableFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
    telescope_runNumbers = []

    for file_name in availableFiles:
        telescope_timeStamp = file_name[8:-5]
        telescope_runNumbers.append(getRunNumberTelescope(telescope_timeStamp, runLog))
    
    telescope_runNumbers.sort()
    while 0 in telescope_runNumbers: telescope_runNumbers.remove(0)

    print "telescope run number available:"
    print telescope_runNumbers

    i = 0
    runs = []
    for row in runLog:
        
        if int(row[3]) not in telescope_runNumbers:

            runs.append(int(row[3]))
        
        i+=1
    return runLog


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

    metaDataFileName = "/Users/aszadaj/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/csv/data_"+str(getTimeStamp())+".csv"
    metaData = getOscilloscopeMetaData(metaDataFileName)
    timeScope = float(metaData[0][4])*float("1E+09")
   
    return timeScope


def getSensorNames():

    sensors = []

    for i in range(13,49,5):
        sensors.append(runInfo[i])
    
    return sensors


def globVar(input):
    
    global runInfo
    runInfo = input

