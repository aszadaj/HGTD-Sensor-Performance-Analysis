import ROOT
import numpy as np
import root_numpy as rnm
import os

import run_log_metadata as md
import data_management as dm
import results_plot as r_plot

def produceResults():
    
    global canvas
    global processed_sensor
    global bias_voltage_max
    
    bias_voltage_max = 350
    
    categories = ["noise", "pulse_amplitude", "charge", "rise_time", "normal_peak", "system_peak", "normal_cfd", "system_cfd", "normal_peak_gain", "system_peak_gain", "normal_cfd_gain", "system_cfd_gain", "normal_peak_gain_zoom", "system_peak_gain_zoom", "normal_cfd_gain_zoom", "system_cfd_gain_zoom"]


    canvas = ROOT.TCanvas("Results", "Results")
    
    sensorNames = md.getAvailableSensors()
    sensorNames.remove("SiPM-AFP")
    
    sensorNames.sort()
    
    if md.sensor != "":
        sensorNames = [md.sensor]
    
    
    resultsDict = dict()
    resultGraphs = dict()
    legend = dict()

    print "\nStart RESULTS"
    
    zoom = False
    
    # loop through each category
    for category in categories:
        
        print "\n", category, "\n"
        
        if category.endswith("zoom"):
            zoom = True
            category = category[:-5]
    
        
        category_graph = ROOT.TMultiGraph()
        legend_graph = ROOT.TLegend(0.7, 0.9, 0.9, 0.6)
        
        graph = dict()

        doOnce = True

        for processed_sensor in sensorNames:
            
            print processed_sensor
            
            md.defineRunInfo(md.getRowForRunNumber(md.getRunsWithSensor(processed_sensor)[0]))
            md.setChannelName(md.getChannelNameForSensor(processed_sensor))

            graph[processed_sensor] = dict()
            sensor_data = dict()
            
            # Create TGraphErrors for each sensor, temperature and position (in the case of array pads)
            for temperature in md.getAvailableTemperatures():
                
                graph[processed_sensor][temperature] = dict()
                sensor_data[temperature] = dict()

                
                if processed_sensor == "W4-S204_6e14" and doOnce:
                    graph["W4-S204_6e14"]["22"] = dict()
                    graph["W4-S204_6e14"]["22"]["7_0"] = ROOT.TGraphErrors()
                    r_plot.setMarkerType(graph["W4-S204_6e14"]["22"]["7_0"], DUT_pos, temperature)
                    doOnce = False


                for DUT_pos in availableDUTPositions(processed_sensor):
                    graph[processed_sensor][temperature][DUT_pos] = ROOT.TGraphErrors()
                    sensor_data[temperature][DUT_pos] = []
                
                    # Change each marker type and color
                    r_plot.setMarkerType(graph[processed_sensor][temperature][DUT_pos], DUT_pos, temperature)

            importResultsValues(sensor_data, category)

            r_plot.addValuesToGraph([sensor_data, category, legend_graph, graph, category_graph])

        r_plot.drawAndExportResults(category, category_graph, legend_graph, zoom)


def importResultsValues(sensor_data, category_subcategory):
    
    global oneSensorInLegend
    
    if category_subcategory.endswith('gain'):
        category_subcategory = category_subcategory[:-5]
        gain_category = True
    
    else:
        gain_category = False
    

    # here are imported all files, that is for each pad, temperature and bias voltage
    for batchNumber in md.getAllBatchNumbers():
        for chan in md.getAllChannelsForSensor(batchNumber, processed_sensor):
    
            if batchNumber not in md.getAllBatchNumberForSensor(processed_sensor) or omitBadData(batchNumber, category_subcategory):
                continue
        
        
            md.defineRunInfo(md.getRowForRunNumber(md.getAllRunNumbers(batchNumber)[0]))
      
            md.setChannelName(chan)
            
            if md.getDUTPos() in ["3_0", "3_1", "3_3", "8_1", "7_2", "7_3"]:
                continue
 


            # Define the name for the histogram, depending on type
            if category_subcategory.find("pulse_amplitude") == -1 and category_subcategory.find("charge") == -1:
                
                group = "timing"
                chan2 = ""
                parameter_number = 2
                
                if category_subcategory.find("system") != -1:
                    if md.chan_name not in ["chan0", "chan1", "chan2", "chan3"]:
                        continue
                    
                    category = "system"
                    chan2 = "chan"+str((int(md.chan_name[-1])+1)%4)
            
                else:
                    category = "normal"
                
                if category_subcategory.endswith('cfd'):
                    
                    subcategory = "cfd"
                
                else:
                    
                    subcategory = "peak"
                
                if category_subcategory.find("rise_time") != -1 or category_subcategory.find("noise") != -1:
                    group = "pulse"
                    category = category_subcategory
                    subcategory = ""
                    chan2 = ""

                # Here, import the histogram which contain the results
                histogram = dm.exportImportROOTHistogram(group, category, subcategory, chan2)
                
                if histogram:
                    fit_function = histogram.GetFunction("gaus")
                    
                    if category_subcategory.find("noise") != -1 or category_subcategory.find("rise_time") != -1:
                        parameter_number = 1

                    results = [fit_function.GetParameter(parameter_number), fit_function.GetParError(parameter_number)]
                    
                        
                else:
                    continue
            
            # pulse and gain
            else:
                
                histogram = dm.exportImportROOTHistogram("pulse", category_subcategory)
                if histogram:
                    th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
                    function_name = "Fitfcn_" + category_subcategory + th_name
                    fit_function = histogram.GetFunction(function_name)
                    try:
                        fit_function.GetTitle()
                    except:
                        continue
                    results = [fit_function.GetParameter(1), fit_function.GetParError(1)]
                else:
                    continue
        
        
            if category_subcategory.find("normal") != -1 or category_subcategory.find("system") != -1:
            
                results[0] = np.sqrt(np.power(results[0], 2) - np.power(md.getSigmaSiPM(), 2))
        
            value_error = [results[0], results[1]]
            voltage = md.getBiasVoltage()
            
            # For the timing resolution vs gain, replace the bias voltage with gain
            if (category_subcategory.find("system") != -1 or category_subcategory.find("normal") != -1) and gain_category:
                
                histogram = dm.exportImportROOTHistogram("pulse", "charge")
                th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
                function_name = "Fitfcn_" + "charge" + th_name
                fit_function = histogram.GetFunction(function_name)
                
                gain = fit_function.GetParameter(1)/md.getChargeWithoutGainLayer()
                
                voltage = int(gain) # this takes the even number of gain (to select better values)
    
            temperature = str(md.getTemperature())
            
            DUT_pos = md.getDUTPos()
        
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


    oneSensorInLegend = True


def omitBadData(batch, category):

    bool = False

    if processed_sensor == "W4-RD01" and batch in [606]:
        bool = True

    elif processed_sensor == "W4-S203" and batch in [704, 705, 706]:
        bool = True
    elif processed_sensor == "W4-S215" and batch in [405, 406, 706]:
        bool = True
    elif processed_sensor == "W4-S1022" and batch in [405, 705, 706]:
        bool = True
    elif processed_sensor == "W4-S1061" and batch in [406, 705, 706]:
        bool = True

    elif category.find("system") != -1:
        if processed_sensor in ["W4-S203", "W4-S215", "W4-S1022", "W4-S1061"] and batch in [405, 406, 704, 705, 706]:
            bool = True


    return bool


def availableDUTPositions(sensor):
    
    if sensor == "W4-S215":
        
        return ["3_0", "3_1", "3_2", "3_3"]

    elif sensor == "W4-RD01":
        
        return ["8_1", "8_2"]

    elif sensor == "W4-S204_6e14":
    
        return ["7_0", "7_2", "7_3"]
    
    else:
        
        return md.getDUTPos()
