import root_numpy as rnm
import os

import results_main as rm
import run_log_metadata as md
import data_management as dm


def importResultsValues(sensor_data, category):

    # Import results for the sensor and category
    files = readResultsDataFiles(category)

    # here are imported all files, that is for each pad, temperature and bias voltage
    for filePath in files:
    
        results = rnm.root2array(filePath)
        batchNumber, chan = getBatchNumberAndChanFromFile(filePath)
        md.defineGlobalVariableRun(md.getRowForBatchNumber(batchNumber))
        
        if omitBadData(batchNumber, category):
            continue

        value_error = [results[0][0], results[1][0]]
        voltage = md.getBiasVoltage(rm.processed_sensor, batchNumber)
        
        if (category.find("system") != -1 or category.find("linear") != -1) and category.find("gain") != -1:
            md.setChannelName(chan)
            gain = dm.exportImportROOTData("results", "charge")["charge"][0]/0.46
            voltage = int(gain) # this takes the even number of gain (to select better values)
        
        temperature = str(md.getTemperature())
        
        DUT_pos = md.getDUTPos(rm.processed_sensor, chan)
      
        omitRun = False
    

        # Among the all batches, choose one with smallest error.
        for index in range(0, len(sensor_data[temperature][DUT_pos])):
            sensor_results = sensor_data[temperature][DUT_pos][index]
       

            # Check if there is an earlier filled bias voltage, otherwise fill
            if voltage == sensor_results[0]:
            
                omitRun = True
                
                # For the same voltage, choose the one with smallest error.
                if value_error[1] < sensor_results[1][1]:
                    
                    sensor_data[temperature][DUT_pos][index] = [voltage, value_error]


        if not omitRun:
            sensor_data[temperature][DUT_pos].append([voltage, value_error])


    rm.oneSensorInLegend = True



# Read in results files for each category
def readResultsDataFiles(category):
    
    if category.endswith('gain'):
        category = category[:-5]
    
    directory = dm.getSourceFolderPath() + dm.getDataSourceFolder()+ "/results/" + rm.processed_sensor + "/" + category + "/"
    availableFiles = [directory + f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store']
    availableFiles.sort()
    return availableFiles




# THis is for making the gain vs time resolution plot
# Read in results files for each category
def readResultsDataFilesTemp(category):

    directory = dm.getSourceFolderPath() + dm.getDataSourceFolder()+ "/results/" + rm.processed_sensor + "/" + category + "/"
    availableFiles = [directory + f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store']
    availableFiles.sort()
    
    return availableFiles


def getBatchNumberAndChanFromFile(file):
    
    return int(file[-14:-11]), file[-10:-5]


def omitBadData(batch, category):

    bool = False

    if rm.processed_sensor == "W4-RD01" and batch in [606]:
        bool = True

    elif rm.processed_sensor == "W4-S203" and batch in [704, 705, 706]:
        bool = True
    elif rm.processed_sensor == "W4-S215" and batch in [405, 406, 706]:
        bool = True
    elif rm.processed_sensor == "W4-S1022" and batch in [405, 705, 706]:
        bool = True
    elif rm.processed_sensor == "W4-S1061" and batch in [406, 705, 706]:
        bool = True

    elif category.find("sys") != -1:
        if rm.processed_sensor in ["W4-S203", "W4-S215", "W4-S1022", "W4-S1061"] and batch in [405, 406, 704, 705, 706]:
            bool = True


    return bool

