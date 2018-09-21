import root_numpy as rnm
import os

import results_main as rm
import run_log_metadata as md
import data_management as dm


def importResultsValues(sensor_data, category):

    # Import results for the sensor and category
    files = readFileNames(category)

    # here are imported all files, that is for each pad, temperature and bias voltage
    for filePath in files:
    
        results = rnm.root2array(filePath)
        batchNumber = getBatchNumberFromFile(filePath)
        md.defineGlobalVariableRun(md.getRowForBatchNumber(batchNumber))
        

        chan = "chan" + filePath[filePath.find("chan")+4]

        value_error = [results[0][0], results[1][0]]
        voltage = md.getBiasVoltage(rm.processed_sensor, batchNumber)
        temperature = str(md.getTemperature())
        DUT_pos = md.getDUTPos(chan)

        omitRun = False
    

        # Among the all batches, choose one with most data = best data.
        for index in range(0, len(sensor_data[temperature][DUT_pos])):
            sensor_results = sensor_data[temperature][DUT_pos][index]
       

            # Check if there is an earlier filled bias voltage, otherwise fill
            if voltage == sensor_results[0]:
            
                omitRun = True
                
                # For the same voltage, choose the one with smallest error.
                if value_error[1] < sensor_results[1][1]:
                    
                    sensor_data[temperature][DUT_pos][index] = [voltage, value_error]

        # Omit run does not append to the list as extra value.
        if not omitRun:
            sensor_data[temperature][DUT_pos].append([voltage, value_error])


    rm.oneSensorInLegend = True



# Read in results files for each category
def readFileNames(category):

    directory = dm.getSourceResultsDataPath() + rm.processed_sensor + "/" + category + "/"
    
    availableFiles = [directory + f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.DS_Store']
    availableFiles.sort()


    return availableFiles


def getBatchNumberFromFile(file):
    return int(file[file.find("chan")-4:file.find("chan")-1])


