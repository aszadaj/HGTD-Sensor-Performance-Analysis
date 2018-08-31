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

        if batchNumber in omitBadDataBatches():
            continue

        if category.find("system") != -1 and batchNumber/100 == 3:
            continue

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

                # Choose low values as favorable for timing and rise time
                if category.find("timing") != -1 or category == "charge" or category == "rise_time":

                    if value_error[0] > sensor_results[1][0]:
                        omitRun = True
                        break

                    else:
                        sensor_data[temperature][DUT_pos][index] = [voltage, value_error]
                        omitRun = True
                        break

                # For other categories, highest value is selected
                else:

                    if value_error[0] < sensor_results[1][0]:
                        omitRun = True
                        break

                    else:
                        sensor_data[temperature][DUT_pos][index] = [voltage, value_error]
                        omitRun = True
                        break

        if omitRun:
            continue

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


def omitBadDataBatches():

    list = [801, 802, 803, 804, 805, 806]

    if rm.processed_sensor == "W4-RD01":

        list.append(606)
    
    elif rm.processed_sensor == "W4-S203":

        list.append(704)
        list.append(705)
        list.append(706)

    elif rm.processed_sensor == "W4-S215":
    
        list.append(405)
        list.append(406)
        list.append(706)
    
    elif rm.processed_sensor == "W4-S1022":
        
        list.append(405)
        list.append(705)
        list.append(706)

    elif rm.processed_sensor == "W4-S1061":
        
        list.append(406)
        list.append(705)
        list.append(706)


    return list

